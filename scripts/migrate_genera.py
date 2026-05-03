#!/usr/bin/env python3
"""
Migration script to populate genus database from existing plant records.
Extracts unique (variety_name, latin_name) pairs and creates genus records.

Usage:
    python scripts/migrate_genera.py --dry-run
    python scripts/migrate_genera.py
"""
import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Ensure commands package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
from commands.genus_model import Genus, get_genera_dir, load_from_file as load_genus_from_file
from commands.plant_model import load_plant_from_file, get_database_dir


def load_all_plants(database_dir: Path) -> list:
    """Load all plant records from database directory."""
    plants = []
    for filepath in sorted(database_dir.glob("*.md")):
        try:
            plants.append(load_plant_from_file(filepath))
        except Exception as e:
            print(f"  Warning: Skipping {filepath.name}: {e}")
    return plants


def group_plants(plants: list) -> dict:
    """Group plants by (variety_name, latin_name).

    Returns dict of (variety_name, latin_name) -> [plants].
    """
    groups = defaultdict(list)
    for plant in plants:
        key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
        groups[key].append(plant)
    return dict(groups)


def find_existing_genus(variety_name: str, latin_name: str, genera_dir: Path):
    """Find an existing genus record matching variety_name and latin_name."""
    if not genera_dir.exists():
        return None
    for filepath in genera_dir.glob("*.md"):
        try:
            genus = load_genus_from_file(filepath)
            if (genus.data.get('variety_name') == variety_name and
                    genus.data.get('latin_name') == latin_name):
                return genus
        except Exception:
            continue
    return None


def create_genus(variety_name: str, latin_name: str, genera_dir: Path, dry_run: bool) -> str:
    """Create a new genus record. Returns the genus ID."""
    genus_data = {
        'variety_name': variety_name,
        'latin_name': latin_name,
    }

    genus = Genus(genus_data)
    genus_file = genera_dir / f"{genus.data['id']}.md"

    if dry_run:
        print(f"  [DRY RUN] Would create genus: {genus.data['id']} - {variety_name} ({latin_name})")
        print(f"            Would save to: {genus_file}")
    else:
        with open(genus_file, 'w') as f:
            f.write(genus.to_markdown())
        print(f"  Created genus: {genus.data['id']} - {variety_name} ({latin_name})")
        print(f"            Saved to: {genus_file}")

    return genus.data['id']


def update_plant_file(plant, filepath: Path, genus_id: str, dry_run: bool) -> bool:
    """Add genus_id to a plant's frontmatter and save.

    Returns True if file was changed.
    """
    if plant.data.get('genus_id'):
        return False

    if dry_run:
        print(f"  [DRY RUN] Would update {filepath.name} with genus_id: {genus_id}")
        return True

    plant.data['genus_id'] = genus_id
    plant.data['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    md_content = plant.to_markdown()
    with open(filepath, 'w') as f:
        f.write(md_content)
    print(f"  Updated {filepath.name} with genus_id: {genus_id}")
    return True


def migrate(database_dir: Path, genera_dir: Path, dry_run: bool = False) -> None:
    """Run the migration."""
    print("=" * 60)
    print("Genus Database Migration")
    print("=" * 60)
    print()

    # Ensure genera directory exists
    genera_dir.mkdir(parents=True, exist_ok=True)

    # Load all plants
    plants = load_all_plants(database_dir)
    if not plants:
        print("No plant records found. Nothing to migrate.")
        return

    print(f"Found {len(plants)} plant record(s)")
    print()

    # Group by (variety_name, latin_name)
    groups = group_plants(plants)
    print(f"Found {len(groups)} unique (variety_name, latin_name) pair(s)")
    print()

    # Statistics
    total_with_data = sum(1 for k, v in groups.items() if k[0] and k[1])
    print(f"Total plants with genus data: {total_with_data}")
    print()

    # Plan: create/find genera and map to plants
    genus_map = {}  # group_key -> genus_id
    created_count = 0
    existing_count = 0

    for group_key, plant_list in sorted(groups.items()):
        variety, latin = group_key
        count = len(plant_list)

        print(f"Group: {variety} ({latin}) — {count} plant(s)")

        if not variety or not latin:
            print(f"  No variety/latin data → skipping")
            genus_map[group_key] = None
            continue

        # Check if genus already exists
        existing_genus = find_existing_genus(variety, latin, genera_dir)
        if existing_genus:
            genus_id = existing_genus.data['id']
            print(f"  Genus already exists: {genus_id}")
            existing_count += 1
        else:
            genus_id = create_genus(variety, latin, genera_dir, dry_run)
            created_count += 1

        genus_map[group_key] = genus_id

    print()

    # Apply changes to plant files
    updated_count = 0
    changes = []

    for plant in plants:
        group_key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
        genus_id = genus_map.get(group_key)
        if genus_id is None:
            continue

        filepath = database_dir / f"{plant.data['id']}.md"
        if update_plant_file(plant, filepath, genus_id, dry_run):
            updated_count += 1
            changes.append((plant.data['id'], genus_id))

    print()
    print("Migration complete:")
    print(f"  Genera created: {created_count}")
    print(f"  Genera reused:  {existing_count}")
    print(f"  Plants updated:  {updated_count}")

    if not dry_run and changes:
        print()
        print("Updated plants:")
        for plant_id, genus_id in changes:
            print(f"  {plant_id} → {genus_id}")
    elif dry_run:
        print()
        print("DRY RUN — no changes made")


def main():
    parser = argparse.ArgumentParser(description="Migrate existing plant records to genus database")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")
    args = parser.parse_args()

    database_dir = get_database_dir()
    genera_dir = get_genera_dir()

    if not database_dir.exists():
        print(f"Error: Database directory not found: {database_dir}")
        sys.exit(1)

    migrate(database_dir, genera_dir, args.dry_run)


if __name__ == "__main__":
    main()
