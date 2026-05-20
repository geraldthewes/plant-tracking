#!/usr/bin/env python3
"""
Migration script to move data from Markdown files to PostgreSQL
"""
import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


from commands import database
from commands.models import Genus, Plant, PlantLogEntry, SeedPacket
from commands.genus_model import load_from_file as load_genus_from_file
from commands.plant_log_model import load_log_entries
from commands.plant_model import load_plant_from_file
from commands.seed_packet_model import load_from_file as load_seed_packet_from_file


def get_database_dir() -> Path:
    """Get the database directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database"))


def backup_markdown_data() -> None:
    """Create backup of existing markdown data"""
    database_dir = get_database_dir()
    if not database_dir.exists():
        print("No database directory found to backup")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = database_dir.parent / f"database_backup_{timestamp}"

    print(f"Creating backup at {backup_dir}")
    shutil.copytree(database_dir, backup_dir)
    print("Backup completed")


def migrate_seed_packets() -> Dict[str, str]:
    """
    Migrate seed packet data from markdown to PostgreSQL
    Returns mapping of old IDs to new IDs (should be 1:1)
    """
    print("Migrating seed packets...")

    database_dir = get_database_dir()
    packets_dir = database_dir / "seed_packets"

    if not packets_dir.exists():
        print("No seed packets directory found")
        return {}

    id_mapping = {}

    with database.get_db() as session:
        for packet_file in packets_dir.glob("*.md"):
            try:
                # Load existing markdown seed packet
                packet_data = load_seed_packet_from_file(packet_file)

                # Check if already migrated (by looking for existing ID in DB)
                existing = session.query(SeedPacket).filter_by(id=packet_data.data["id"]).first()
                if existing:
                    print(f"Seed packet {packet_data.data['id']} already exists, skipping")
                    id_mapping[packet_data.data["id"]] = packet_data.data["id"]
                    continue

                # Create new SQLAlchemy seed packet
                # Use existing ID to preserve original IDs
                new_packet = SeedPacket(**packet_data.data)
                session.add(new_packet)
                session.flush()

                id_mapping[packet_data.data["id"]] = new_packet.id
                print(f"Migrated seed packet: {packet_data.data['id']}")

            except Exception as e:
                print(f"Error migrating seed packet {packet_file}: {e}")
                continue

        session.commit()

    print(f"Migrated {len(id_mapping)} seed packets")
    return id_mapping


def migrate_genera() -> Dict[str, str]:
    """
    Migrate genus data from markdown to PostgreSQL
    Returns mapping of old IDs to new IDs (should be 1:1)
    """
    print("Migrating genera...")

    database_dir = get_database_dir()
    genera_dir = database_dir / "genera"

    if not genera_dir.exists():
        print("No genera directory found")
        return {}

    id_mapping = {}

    with database.get_db() as session:
        for genus_file in genera_dir.glob("*.md"):
            try:
                # Load existing markdown genus
                genus_data = load_genus_from_file(genus_file)

                # Check if already migrated
                existing = session.query(Genus).filter_by(id=genus_data.data["id"]).first()
                if existing:
                    print(f"Genus {genus_data.data['id']} already exists, skipping")
                    id_mapping[genus_data.data["id"]] = genus_data.data["id"]
                    continue

                # Create new SQLAlchemy genus
                new_genus = Genus(**genus_data.data)
                session.add(new_genus)
                session.flush()

                id_mapping[genus_data.data["id"]] = new_genus.id
                print(f"Migrated genus: {genus_data.data['id']}")

            except Exception as e:
                print(f"Error migrating genus {genus_file}: {e}")
                continue

        session.commit()

    print(f"Migrated {len(id_mapping)} genera")
    return id_mapping


def migrate_plants(seed_packet_mapping: Dict[str, str], genus_mapping: Dict[str, str]) -> None:
    """
    Migrate plant data from markdown to PostgreSQL
    """
    print("Migrating plants...")

    database_dir = get_database_dir()

    with database.get_db() as session:
        for plant_file in database_dir.glob("*.md"):
            try:
                # Load existing markdown plant
                plant_data = load_plant_from_file(plant_file)

                # Check if already migrated
                existing = session.query(Plant).filter_by(id=plant_data.data["id"]).first()
                if existing:
                    print(f"Plant {plant_data.data['id']} already exists, skipping")
                    continue

                # Prepare data for SQLAlchemy model
                plant_dict = plant_data.data.copy()

                # Map seed packet ID if present
                if plant_dict.get("seed_packet_id") and plant_dict["seed_packet_id"] != "unknown":
                    old_id = plant_dict["seed_packet_id"]
                    if old_id in seed_packet_mapping:
                        plant_dict["seed_packet_id"] = seed_packet_mapping[old_id]
                    else:
                        print(f"Warning: Seed packet {old_id} not found in mapping, setting to None")
                        plant_dict["seed_packet_id"] = None
                elif plant_dict.get("seed_packet_id") == "unknown":
                    plant_dict["seed_packet_id"] = None

                # Map genus ID if present
                if plant_dict.get("genus_id") and plant_dict["genus_id"] != "unknown":
                    old_id = plant_dict["genus_id"]
                    if old_id in genus_mapping:
                        plant_dict["genus_id"] = genus_mapping[old_id]
                    else:
                        print(f"Warning: Genus {old_id} not found in mapping, setting to None")
                        plant_dict["genus_id"] = None
                elif plant_dict.get("genus_id") == "unknown":
                    plant_dict["genus_id"] = None

                # Create new SQLAlchemy plant
                new_plant = Plant(**plant_dict)
                session.add(new_plant)

                print(f"Migrated plant: {plant_data.data['id']}")

            except Exception as e:
                print(f"Error migrating plant {plant_file}: {e}")
                continue

        session.commit()


def migrate_log_entries() -> None:
    """
    Migrate plant log entries from consolidated markdown file to PostgreSQL
    """
    print("Migrating log entries...")

    database_dir = get_database_dir()
    log_file = database_dir / "logs" / "plant-activity-log.md"

    if not log_file.exists():
        print("No log file found")
        return

    # Load all existing log entries
    log_entries_data = load_log_entries()

    if not log_entries_data:
        print("No log entries found")
        return

    with database.get_db() as session:
        migrated_count = 0

        for entry_data in log_entries_data:
            try:
                # Check if entry already exists (by plant_id, event_type, timestamp)
                existing = session.query(PlantLogEntry).filter_by(
                    plant_id=entry_data.get("plant_id"),
                    event_type=entry_data.get("event_type"),
                    timestamp=entry_data.get("timestamp"),
                ).first()

                if existing:
                    continue

                # Normalize field names for ORM model
                orm_data = {"plant_id": entry_data["plant_id"], "event_type": entry_data["event_type"]}

                if "timestamp" in entry_data:
                    orm_data["timestamp"] = entry_data["timestamp"]

                if entry_data["event_type"] == "water" and "amount_ml" in entry_data:
                    orm_data["amount_ml"] = int(entry_data["amount_ml"])
                elif entry_data["event_type"] == "fertilizer":
                    orm_data["fertilizer_type"] = entry_data.get("type")
                    orm_data["fertilizer_strength"] = entry_data.get("strength")
                elif entry_data["event_type"] == "humidity":
                    orm_data["level"] = entry_data.get("level")
                elif entry_data["event_type"] == "note":
                    orm_data["text"] = entry_data.get("text")

                new_entry = PlantLogEntry.create_from_dict(orm_data)
                session.add(new_entry)
                migrated_count += 1

            except Exception as e:
                print(f"Error migrating log entry: {e}")
                print(f"Entry data: {entry_data}")
                continue

        session.commit()

    print(f"Migrated {migrated_count} log entries")


def verify_migration() -> bool:
    """
    Verify that migration was successful by comparing counts
    """
    print("Verifying migration...")

    database_dir = get_database_dir()

    # Count markdown files
    markdown_plants = len(list(database_dir.glob("*.md")))
    markdown_packets = len(list((database_dir / "seed_packets").glob("*.md"))) if (database_dir / "seed_packets").exists() else 0
    markdown_genera = len(list((database_dir / "genera").glob("*.md"))) if (database_dir / "genera").exists() else 0

    # Count database records
    with database.get_db() as session:
        db_plants = session.query(Plant).count()
        db_packets = session.query(SeedPacket).count()
        db_genera = session.query(Genus).count()

        # Count log entries
        db_logs = session.query(PlantLogEntry).count()
        markdown_logs = len(load_log_entries())

    print(f"Markdown plants: {markdown_plants}, DB plants: {db_plants}")
    print(f"Markdown seed packets: {markdown_packets}, DB seed packets: {db_packets}")
    print(f"Markdown genera: {markdown_genera}, DB genera: {db_genera}")
    print(f"Markdown log entries: {markdown_logs}, DB log entries: {db_logs}")

    success = (
        markdown_plants == db_plants
        and markdown_packets == db_packets
        and markdown_genera == db_genera
        and markdown_logs == db_logs
    )

    if success:
        print("Migration verification PASSED")
    else:
        print("Migration verification FAILED")

    return success


def main():
    parser = argparse.ArgumentParser(description="Migrate plant tracking data from Markdown to PostgreSQL")
    parser.add_argument("--backup", action="store_true", help="Create backup of markdown data before migration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without actually doing it")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing migration")

    args = parser.parse_args()

    if args.verify_only:
        success = verify_migration()
        sys.exit(0 if success else 1)

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        database_dir = get_database_dir()
        packets_dir = database_dir / "seed_packets"
        genera_dir = database_dir / "genera"

        print(f"Would migrate {len(list(database_dir.glob('*.md')))} plants")
        if packets_dir.exists():
            print(f"Would migrate {len(list(packets_dir.glob('*.md')))} seed packets")
        if genera_dir.exists():
            print(f"Would migrate {len(list(genera_dir.glob('*.md')))} genera")
        print(f"Would migrate {len(load_log_entries())} log entries")
        return

    if args.backup:
        backup_markdown_data()

    # Run migration in correct order due to foreign key dependencies
    seed_packet_mapping = migrate_seed_packets()
    genus_mapping = migrate_genera()
    migrate_plants(seed_packet_mapping, genus_mapping)
    migrate_log_entries()

    # Verify migration
    success = verify_migration()

    if success:
        print("\nMigration completed successfully!")
    else:
        print("\nMigration completed with errors!")
        sys.exit(1)


if __name__ == "__main__":
    main()
