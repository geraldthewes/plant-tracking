#!/usr/bin/env python3
"""
One-shot migration to extract unique seed packets from existing plants
and backfill seed_packet_id on each plant record.

Usage:
    python scripts/migrate_seed_packets.py --dry-run
    python scripts/migrate_seed_packets.py
"""
import argparse
import copy
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Ensure commands package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
from commands.plant_model import load_plant_from_file, get_database_dir
from commands.seed_packet_model import SeedPacket, get_seed_packets_dir


PACKET_FIELDS = [
    'brand', 'days_to_maturity', 'germination_time',
    'planting_depth', 'spacing', 'sun_requirements', 'indoor_start_time'
]


def load_all_plants(database_dir: Path) -> list:
    """Load all plant records from database directory."""
    plants = []
    for filepath in sorted(database_dir.glob("*.md")):
        try:
            plants.append(load_plant_from_file(filepath))
        except Exception as e:
            print(f"  ⚠ Skipping {filepath.name}: {e}")
    return plants


def has_packet_data(plant) -> bool:
    """Check if a plant has any seed packet fields beyond required fields."""
    for field in PACKET_FIELDS:
        if plant.data.get(field):
            return True
    return False


def group_plants(plants: list) -> dict:
    """Group plants by (variety_name, latin_name).
    
    Returns dict of (variety_name, latin_name) -> [plants].
    """
    groups = defaultdict(list)
    for plant in plants:
        key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
        groups[key].append(plant)
    return dict(groups)


def pick_representative(plant_list: list) -> dict:
    """Pick representative values for a group of plants.
    
    For each packet field, picks the most common non-empty value.
    """
    rep = {}
    for field in PACKET_FIELDS:
        values = [p.data.get(field) for p in plant_list if p.data.get(field)]
        if values:
            counts = defaultdict(int)
            for v in values:
                counts[v] += 1
            rep[field] = max(counts, key=counts.get)
    return rep


def create_packet_from_group(group_key, representative: dict, packets_dir: Path) -> SeedPacket:
    """Create a SeedPacket record from a group's representative data."""
    packet_data = {
        'variety_name': group_key[0],
        'latin_name': group_key[1],
    }
    packet_data.update(representative)
    packet = SeedPacket(packet_data)
    filepath = packets_dir / f"{packet.data['id']}.md"
    with open(filepath, 'w') as f:
        f.write(packet.to_markdown())
    return packet


def update_plant_file(plant, filepath: Path, packet_id: str) -> bool:
    """Add seed_packet_id to a plant's frontmatter and save.
    
    Returns True if file was changed.
    """
    if plant.data.get('seed_packet_id'):
        return False

    plant.data['seed_packet_id'] = packet_id
    plant.data['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    md_content = plant.to_markdown()
    with open(filepath, 'w') as f:
        f.write(md_content)
    return True


def migrate(database_dir: Path, packets_dir: Path, dry_run: bool = False) -> None:
    """Run the migration."""
    print("=" * 60)
    print("Seed Packet Migration")
    print("=" * 60)
    print()

    # Load all plants
    plants = load_all_plants(database_dir)
    if not plants:
        print("No plant records found. Nothing to migrate.")
        return

    print(f"Found {len(plants)} plant record(s)\n")

    # Group by (variety_name, latin_name)
    groups = group_plants(plants)
    print(f"Found {len(groups)} unique variety group(s)\n")

    # Plan: create packets and map to plants
    packet_map = {}  # group_key -> packet_id
    changes = []     # list of (plant_id, packet_id)

    for group_key, plant_list in sorted(groups.items()):
        variety, latin = group_key
        count = len(plant_list)
        packet_data = has_packet_data(plant_list[0])

        if packet_data:
            representative = pick_representative(plant_list)
            rep_display = {k: v for k, v in representative.items()}
            print(f"Group: {variety} ({latin}) — {count} plant(s)")
            if dry_run:
                print(f"  Would create seed packet with: {rep_display}")
                print(f"  Would assign ID: SPKT-??? (auto-generated)")
                packet_id = "SPKT-???"
            else:
                packet = create_packet_from_group(group_key, representative, packets_dir)
                print(f"  Created: {packet.data['id']} — {representative}")
                packet_id = packet.data['id']
        else:
            print(f"Group: {variety} ({latin}) — {count} plant(s)")
            print(f"  No packet data available → marking as 'unknown'")
            packet_id = 'unknown'

        packet_map[group_key] = packet_id

    print()

    # Apply changes to plant files
    if not dry_run:
        updated_count = 0
        for plant in plants:
            group_key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
            packet_id = packet_map[group_key]
            filepath = database_dir / f"{plant.data['id']}.md"
            if update_plant_file(plant, filepath, packet_id):
                updated_count += 1
                changes.append((plant.data['id'], packet_id))

        print(f"Migration complete:")
        print(f"  Packets created: {sum(1 for p in packet_map.values() if p != 'unknown')}")
        print(f"  Plants updated:  {updated_count}")
        print()
        print("Updated plants:")
        for plant_id, packet_id in changes:
            print(f"  {plant_id} → {packet_id}")
    else:
        print("DRY RUN — no changes made")
        print(f"Would create {sum(1 for p in packet_map.values() if p != 'unknown')} seed packet(s)")
        print(f"Would update {len(plants)} plant(s)")
        print()
        print("Plant updates:")
        for plant in plants:
            group_key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
            packet_id = packet_map[group_key]
            print(f"  {plant.data['id']} → {packet_id}")


def main():
    parser = argparse.ArgumentParser(description="Migrate existing plants to seed packets")
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without applying')
    args = parser.parse_args()

    database_dir = get_database_dir()
    packets_dir = get_seed_packets_dir()

    if not database_dir.exists():
        print(f"Error: Database directory not found: {database_dir}")
        sys.exit(1)

    packets_dir.mkdir(parents=True, exist_ok=True)
    migrate(database_dir, packets_dir, args.dry_run)


if __name__ == "__main__":
    main()
