#!/usr/bin/env python3
"""
Plant Tracking CLI - Main entry point for plant tracking commands
"""
import argparse
import os
import sys

# Markdown model imports (for backup/export during transition)
from .genus_model import get_genera_dir
from .plant_log_model import get_logs_dir
from .plant_model import Plant as MarkdownPlant, get_database_dir, load_plant_from_file
from .seed_packet_model import (
    SeedPacket as MarkdownSeedPacket,
    find_matching as markdown_find_matching,
    get_seed_packets_dir,
    list_all as markdown_list_all,
)

# Fuzzy matching for genus name searches
try:
    from thefuzz import fuzz, process

    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    FUZZY_MATCHING_AVAILABLE = False
    process = None
    fuzz = None


# Service package imports
try:
    from plant_service.bootstrap import create_unit_of_work
    from plant_service.domain.exceptions import (
        PlantTrackingServiceException,
        ValidationException,
        PlantNotFoundException,
        SeedPacketNotFoundException,
        GenusNotFoundException,
        PlantLogNotFoundException,
        DatabaseUnavailableError,
        ExportError,
    )
    SERVICE_AVAILABLE = True
except ImportError:
    SERVICE_AVAILABLE = False


# Module-level directory variables for backward compatibility with tests
DATABASE_DIR = get_database_dir()
DATABASE_DIR.mkdir(exist_ok=True)
PACKETS_DIR = get_seed_packets_dir()
PACKETS_DIR.mkdir(exist_ok=True)
GENERA_DIR = get_genera_dir()
GENERA_DIR.mkdir(exist_ok=True)
LOGS_DIR = get_logs_dir()
LOGS_DIR.mkdir(exist_ok=True)


def _ensure_dirs():
    """Ensure database directories exist (for Markdown backup during transition)."""
    global DATABASE_DIR, PACKETS_DIR, GENERA_DIR, LOGS_DIR
    DATABASE_DIR = get_database_dir()
    DATABASE_DIR.mkdir(exist_ok=True)
    PACKETS_DIR = get_seed_packets_dir()
    PACKETS_DIR.mkdir(exist_ok=True)
    GENERA_DIR = get_genera_dir()
    GENERA_DIR.mkdir(exist_ok=True)
    LOGS_DIR = get_logs_dir()
    LOGS_DIR.mkdir(exist_ok=True)
    return DATABASE_DIR, PACKETS_DIR, GENERA_DIR, LOGS_DIR


def _get_db():
    """Get database module, handling missing DATABASE_URL gracefully."""
    try:
        from . import database

        database.init_db()
        return database
    except Exception:
        return None


def main():
    # Ensure directories exist for Markdown backup
    _ensure_dirs()

    # Initialize PostgreSQL if available
    db = _get_db()

    parser = argparse.ArgumentParser(description="Plant Tracking System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create-plant subcommand
    subparsers.add_parser(
        "create-plant", help="Create a new plant record"
    )

    # print-label subcommand (consolidated from create-label and print-label)
    print_parser = subparsers.add_parser(
        "print-label", help="Print a label for a plant (or generate image only)"
    )
    print_parser.add_argument("plant_id", help="Plant ID or label file path")
    print_parser.add_argument(
        "--format", "-f", default="40x30mm", help="Label format (default: 40x30mm)"
    )
    print_parser.add_argument(
        "--no-print",
        action="store_true",
        help="Generate label image only, do not print",
    )

    # create-seed-packet subcommand
    subparsers.add_parser("create-seed-packet", help="Create a new seed packet record")

    # list-seed-packets subcommand
    subparsers.add_parser("list-seed-packets", help="List all seed packets")

    # show-seed-packet subcommand
    show_spkt_parser = subparsers.add_parser(
        "show-seed-packet", help="Show seed packet details"
    )
    show_spkt_parser.add_argument("packet_id", help="Seed packet ID")

    # create-genus subcommand
    subparsers.add_parser("create-genus", help="Create a new genus record")

    # list-genera subcommand
    subparsers.add_parser("list-genera", help="List all genera")

    # show-genus subcommand
    show_genus_parser = subparsers.add_parser(
        "show-genus", help="Show genus details"
    )
    show_genus_parser.add_argument("genus_id", help="Genus ID")

    # list-plants subcommand
    subparsers.add_parser("list-plants", help="List all plants")

    # show-plant subcommand
    show_plant_parser = subparsers.add_parser(
        "show-plant", help="Show plant details"
    )
    show_plant_parser.add_argument("plant_id", help="Plant ID")

    # log subcommand
    log_parser = subparsers.add_parser("log", help="Log plant observations")
    log_subparsers = log_parser.add_subparsers(
        dest="log_command", help="Log subcommands"
    )

    # log humidity
    log_humidity_parser = log_subparsers.add_parser(
        "humidity", help="Log humidity reading"
    )
    log_humidity_parser.add_argument("plant_id", help="Plant ID")
    log_humidity_parser.add_argument(
        "--level", "-l", type=int, required=True, help="Humidity level (1-10)"
    )
    log_humidity_parser.add_argument(
        "--date", "-d", help="Date (YYYY-MM-DD, default: today)"
    )

    # log water
    log_water_parser = log_subparsers.add_parser("water", help="Log watering event")
    log_water_parser.add_argument("plant_id", help="Plant ID")
    log_water_parser.add_argument(
        "--amount", "-a", required=True, help="Amount (e.g., 4qt, 1L, 500ml)"
    )
    log_water_parser.add_argument(
        "--date", "-d", help="Date (YYYY-MM-DD, default: today)"
    )

    # log fertilizer
    log_fertilizer_parser = log_subparsers.add_parser(
        "fertilizer", help="Log fertilization"
    )
    log_fertilizer_parser.add_argument("plant_id", help="Plant ID")
    log_fertilizer_parser.add_argument(
        "--type", "-t", required=True, help="Fertilizer type/brand"
    )
    log_fertilizer_parser.add_argument(
        "--strength", "-s", required=True, help="Strength/concentration (e.g., 1/2)"
    )
    log_fertilizer_parser.add_argument(
        "--date", "-d", help="Date (YYYY-MM-DD, default: today)"
    )

    # log note
    log_note_parser = log_subparsers.add_parser(
        "note",
        help="Log a markdown note",
        description="Create a new markdown-formatted note attached to a plant",
    )
    log_note_parser.add_argument("plant_id", help="Plant ID")
    log_note_parser.add_argument("--text", "-t", help="Note text (markdown supported)")
    log_note_parser.add_argument(
        "--file", "-f", help="Read note text from a file (or '-' for stdin)"
    )
    log_note_parser.add_argument(
        "--date", "-d", help="Date (YYYY-MM-DD, default: today)"
    )

    # log list
    log_list_parser = log_subparsers.add_parser(
        "list", help="List all logs for a plant"
    )
    log_list_parser.add_argument("plant_id", help="Plant ID")
    log_list_parser.add_argument(
        "--type",
        choices=["humidity", "water", "fertilizer", "note", "all"],
        default="all",
        help="Filter by log type",
    )

    # media subcommand
    media_parser = subparsers.add_parser(
        "media", help="Manage media attachments (images, videos, audio)"
    )
    media_subparsers = media_parser.add_subparsers(
        dest="media_command", help="Media subcommands"
    )

    media_add_image_parser = media_subparsers.add_parser(
        "add-image", help="Add an image attachment to a plant"
    )
    media_add_image_parser.add_argument("plant_id", help="Plant ID")
    media_add_image_parser.add_argument("image_path", help="Path to image file")
    media_add_image_parser.add_argument(
        "--label", "-l", help="Optional label for the image"
    )
    media_add_image_parser.add_argument(
        "--tags", "-t", help="Optional comma-separated tags"
    )

    media_add_video_parser = media_subparsers.add_parser(
        "add-video", help="Add a video attachment to a plant"
    )
    media_add_video_parser.add_argument("plant_id", help="Plant ID")
    media_add_video_parser.add_argument("video_path", help="Path to video file")
    media_add_video_parser.add_argument(
        "--label", "-l", help="Optional label for the video"
    )
    media_add_video_parser.add_argument(
        "--tags", "-t", help="Optional comma-separated tags"
    )

    media_add_audio_parser = media_subparsers.add_parser(
        "add-audio", help="Add an audio attachment to a plant"
    )
    media_add_audio_parser.add_argument("plant_id", help="Plant ID")
    media_add_audio_parser.add_argument("audio_path", help="Path to audio file")
    media_add_audio_parser.add_argument(
        "--label", "-l", help="Optional label for the audio"
    )
    media_add_audio_parser.add_argument(
        "--tags", "-t", help="Optional comma-separated tags"
    )

    media_list_parser = media_subparsers.add_parser(
        "list", help="List media attachments for a plant"
    )
    media_list_parser.add_argument("plant_id", help="Plant ID")

    media_show_parser = media_subparsers.add_parser(
        "show", help="Show media attachment details"
    )
    media_show_parser.add_argument("media_id", type=int, help="Media attachment ID")

    media_delete_parser = media_subparsers.add_parser(
        "delete", help="Delete a media attachment"
    )
    media_delete_parser.add_argument("media_id", type=int, help="Media attachment ID")

    media_url_parser = media_subparsers.add_parser(
        "url", help="Get presigned URL for media attachment"
    )
    media_url_parser.add_argument("media_id", type=int, help="Media attachment ID")

    args = parser.parse_args()

    if args.command == "create-plant":
        create_plant(args, db, DATABASE_DIR, PACKETS_DIR, GENERA_DIR)
    elif args.command == "print-label":
        print_label(args)
    elif args.command == "create-seed-packet":
        create_seed_packet(args, db, PACKETS_DIR)
    elif args.command == "list-seed-packets":
        list_seed_packets(args, db)
    elif args.command == "show-seed-packet":
        show_seed_packet(args, db)
    elif args.command == "create-genus":
        create_genus(args, db, GENERA_DIR)
    elif args.command == "list-genera":
        list_genera(args, db)
    elif args.command == "show-genus":
        show_genus(args, db)
    elif args.command == "list-plants":
        list_plants(args, db)
    elif args.command == "show-plant":
        show_plant(args, db)
    elif args.command == "log":
        if args.log_command == "humidity":
            log_humidity(args, db)
        elif args.log_command == "water":
            log_water(args, db)
        elif args.log_command == "fertilizer":
            log_fertilizer(args, db)
        elif args.log_command == "note":
            log_note(args, db)
        elif args.log_command == "list":
            log_list(args, db)
        else:
            log_parser.print_help()
    elif args.command == "media":
        if args.media_command == "add-image":
            media_add_attachment(args, db, "image")
        elif args.media_command == "add-video":
            media_add_attachment(args, db, "video")
        elif args.media_command == "add-audio":
            media_add_attachment(args, db, "audio")
        elif args.media_command == "list":
            media_list_attachments(args, db)
        elif args.media_command == "show":
            media_show_attachment(args, db)
        elif args.media_command == "delete":
            media_delete_attachment(args, db)
        elif args.media_command == "url":
            media_get_url(args, db)
        else:
            media_parser.print_help()
    else:
        parser.print_help()


def _prompt_field(field, description, data):
    """Prompt user for a single field value with validation."""
    while True:
        value = input(f"{description}: ").strip()
        if value:
            data[field] = value
            break
        else:
            print("This field is required")


def _prompt_optional_field(field, description, data):
    """Prompt user for an optional field value."""
    value = input(f"{description} (optional): ").strip()
    if value:
        data[field] = value


def _write_markdown_backup(filepath, model_instance):
    """Write Markdown backup file for a model instance."""
    with open(filepath, "w") as f:
        f.write(model_instance.to_markdown())


def create_plant(args, db=None, database_dir=None, packets_dir=None, genera_dir=None):
    """Create a new plant record through interactive prompts with genus lookup."""
    from .genus_model import find_by_variety_name as markdown_find_by_variety_name

    # Backward compatibility: use module-level vars if not provided
    if database_dir is None:
        database_dir = getattr(args, "database_dir", None) or DATABASE_DIR
    if packets_dir is None:
        packets_dir = getattr(args, "packets_dir", None) or PACKETS_DIR
    if genera_dir is None:
        genera_dir = getattr(args, "genera_dir", None) or GENERA_DIR

    print("=== Create New Plant Record ===")
    print(
        "Fields needed for the label are required; record-keeping fields are optional."
    )
    print()

    plant_data = {}

    # Phase 1: Ask for variety name to look up genus
    print("--- Variety identification (used for label & genus lookup) ---")
    _prompt_field("variety_name", "Variety name (e.g., Yellow Habanero)", plant_data)

    # Try exact match by variety name first
    genus_id = None
    genus_latin = None
    genus_variety = None

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                # Get all genera and find matching variety name
                for genus in uow.genera.list_genera():
                    if genus.variety_name == plant_data["variety_name"]:
                        genus_id = genus.id
                        genus_latin = genus.latin_name
                        genus_variety = genus.variety_name
                        break
        except Exception:
            pass
    elif db:
        # Fallback to original models if service not available
        from .models import Genus

        existing_genus = Genus.find_by_variety_name(plant_data["variety_name"])
        if existing_genus:
            genus_id = existing_genus.id
            genus_latin = existing_genus.latin_name
            genus_variety = existing_genus.variety_name
    else:
        # Markdown fallback
        existing_genus = markdown_find_by_variety_name(plant_data["variety_name"])
        if existing_genus:
            genus_id = existing_genus.data["id"]
            genus_latin = existing_genus.data["latin_name"]
            genus_variety = existing_genus.data["variety_name"]

    if genus_id:
        print(
            f"\n✓ Found genus: {genus_id} - {genus_variety}"
        )
        print(f"  Latin name: {genus_latin}")
        plant_data["latin_name"] = genus_latin
        plant_data["genus_id"] = genus_id
        print("  Latin name auto-resolved from genus database.")
    else:
        # Try fuzzy search automatically
        matched_genus_id = _fuzzy_search_genus(plant_data["variety_name"], db)
        if matched_genus_id:
            if db and SERVICE_AVAILABLE:
                try:
                    with create_unit_of_work() as uow:
                        # Find the genus by ID
                        for genus in uow.genera.list_genera():
                            if genus.id == matched_genus_id:
                                print(
                                    f"\n✓ Fuzzy match found: {genus.id} - {genus.variety_name}"
                                )
                                print(f"  Latin name: {genus.latin_name}")
                                confirm = input("Use this genus? (Y/n): ").strip().lower()
                                if confirm != "n":
                                    plant_data["latin_name"] = genus.latin_name
                                    plant_data["genus_id"] = genus.id
                                    print("  Latin name auto-resolved from genus database.")
                                break
                except Exception:
                    pass
            elif db:
                # Fallback to original models
                from .models import Genus

                all_genera = Genus.list_all()
                matched_genus = next(
                    (g for g in all_genera if g.id == matched_genus_id), None
                )
                if matched_genus:
                    print(
                        f"\n✓ Fuzzy match found: {matched_genus.id} - {matched_genus.variety_name}"
                    )
                    print(f"  Latin name: {matched_genus.latin_name}")
                    confirm = input("Use this genus? (Y/n): ").strip().lower()
                    if confirm != "n":
                        plant_data["latin_name"] = matched_genus.latin_name
                        plant_data["genus_id"] = matched_genus.id
                        print("  Latin name auto-resolved from genus database.")
            else:
                # Markdown fallback
                all_genera = markdown_list_all()
                matched_genus = next(
                    (g for g in all_genera if g.data["id"] == matched_genus_id), None
                )
                if matched_genus:
                    print(
                        f"\n✓ Fuzzy match found: {matched_genus.data['id']} - {matched_genus.data['variety_name']}"
                    )
                    print(f"  Latin name: {matched_genus.data['latin_name']}")
                    confirm = input("Use this genus? (Y/n): ").strip().lower()
                    if confirm != "n":
                        plant_data["latin_name"] = matched_genus.data["latin_name"]
                        plant_data["genus_id"] = matched_genus.data["id"]
                        print("  Latin name auto-resolved from genus database.")

        # If still no match, ask for Latin name
        if "latin_name" not in plant_data:
            _prompt_field(
                "latin_name", "Latin name (e.g., Capsicum chinense)", plant_data
            )

            # Offer to create new genus entry
            create_genus = (
                input("Create a new genus entry for this variety? (y/N): ")
                .strip()
                .lower()
            )
            if create_genus == "y":
                if db and SERVICE_AVAILABLE:
                    try:
                        genus_data = {
                            "variety_name": plant_data["variety_name"],
                            "latin_name": plant_data["latin_name"],
                        }
                        with create_unit_of_work() as uow:
                            genus = uow.genera.create_genus(genus_data)
                            plant_data["genus_id"] = genus.id
                            print(f"\n✓ Genus created: {genus.id}")
                    except Exception as e:
                        print(f"Error creating genus: {e}")
                        plant_data["genus_id"] = "unknown"
                elif db:
                    # Fallback to original models
                    from .models import Genus

                    genus_data = {
                        "variety_name": plant_data["variety_name"],
                        "latin_name": plant_data["latin_name"],
                    }
                    genus = Genus.create_from_dict(genus_data)
                    with db.get_db() as session:
                        session.add(genus)
                        session.commit()
                    plant_data["genus_id"] = genus.id
                    # Markdown backup
                    from .genus_model import Genus as MarkdownGenus
                    backup_data = genus_data.copy()
                    backup_data["id"] = genus.id
                    markdown_genus = MarkdownGenus(backup_data)
                    filepath = genera_dir / f"{genus.id}.md"
                    _write_markdown_backup(filepath, markdown_genus)
                else:
                    # Markdown fallback
                    from .genus_model import Genus

                    genus_data = {
                        "variety_name": plant_data["variety_name"],
                        "latin_name": plant_data["latin_name"],
                    }
                    genus = Genus(genus_data)
                    genera_dir.mkdir(parents=True, exist_ok=True)
                    filepath = genera_dir / f"{genus.data['id']}.md"
                    _write_markdown_backup(filepath, genus)
                    plant_data["genus_id"] = genus.data["id"]
            else:
                plant_data["genus_id"] = "unknown"

    # Phase 2: Seed packet handling
    print()
    print("--- Seed packet ---")
    packet_matched = False

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                # Find matching seed packet
                for packet in uow.seed_packets.list_seed_packets():
                    if (
                        packet.variety_name == plant_data["variety_name"]
                        and packet.latin_name == plant_data["latin_name"]
                    ):
                        print(
                            f"\n✓ Found seed packet: {packet.id} - {packet.variety_name}"
                        )
                        plant_data["seed_packet_id"] = packet.id
                        packet_matched = True
                        break
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import SeedPacket

        spkt = SeedPacket.find_matching(
            plant_data["variety_name"], plant_data["latin_name"]
        )
        if spkt:
            print(
                f"\n✓ Found seed packet: {spkt.id} - {spkt.variety_name}"
            )
            plant_data["seed_packet_id"] = spkt.id
            packet_matched = True
    else:
        # Markdown fallback
        spkt = markdown_find_matching(
            plant_data["variety_name"], plant_data["latin_name"]
        )
        if spkt:
            print(
                f"\n✓ Found seed packet: {spkt.data['id']} - {spkt.data['variety_name']}"
            )
            plant_data["seed_packet_id"] = spkt.data["id"]
            packet_matched = True

    if not packet_matched:
        choice = _prompt_packet_choice(plant_data)
        if choice == "create":
            if db and SERVICE_AVAILABLE:
                try:
                    packet_id = _create_packet_inline(plant_data, db, packets_dir)
                    plant_data["seed_packet_id"] = packet_id
                except Exception as e:
                    print(f"Error creating seed packet: {e}")
                    plant_data["seed_packet_id"] = "unknown"
            elif db:
                # Fallback to original models
                packet_id = _create_packet_inline(plant_data, db, packets_dir)
                plant_data["seed_packet_id"] = packet_id
            else:
                # Markdown fallback
                packet_id = _create_packet_inline(plant_data, db, packets_dir)
                plant_data["seed_packet_id"] = packet_id
        elif choice == "select":
            if db and SERVICE_AVAILABLE:
                try:
                    selected = _select_existing_packet(db)
                    plant_data["seed_packet_id"] = selected if selected else "unknown"
                except Exception:
                    plant_data["seed_packet_id"] = "unknown"
            elif db:
                # Fallback to original models
                selected = _select_existing_packet(db)
                plant_data["seed_packet_id"] = selected if selected else "unknown"
            else:
                # Markdown fallback
                selected = _select_existing_packet(db)
                plant_data["seed_packet_id"] = selected if selected else "unknown"
        else:
            _prompt_record_fields(plant_data)
            plant_data["seed_packet_id"] = "unknown"

    # Phase 3: Plant-specific required field (always asked)
    print()
    print("--- Plant-specific field ---")
    _prompt_field("planting_date", "Planting date (YYYY-MM-DD)", plant_data)

    try:
        plant_id = None
        if db and SERVICE_AVAILABLE:
            try:
                with create_unit_of_work() as uow:
                    plant = uow.plants.create_plant(plant_data)
                    plant_id = plant.id
            except ValidationException as e:
                print(f"\n✗ Validation error: {e}")
                sys.exit(1)
            except PlantTrackingServiceException as e:
                print(f"\n✗ Service error: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"\n✗ Error creating plant record: {e}")
                sys.exit(1)
        elif db:
            # Fallback to original models
            from .models import Plant

            plant = Plant.create_from_dict(plant_data)
            with db.get_db() as session:
                session.add(plant)
                session.commit()

            plant_id = plant.id

            # Markdown backup
            backup_data = {
                "id": plant.id,
                "variety_name": plant.variety_name,
                "latin_name": plant.latin_name,
                "planting_date": plant.planting_date,
                "brand": plant.brand or "unknown",
                "days_to_maturity": plant.days_to_maturity or "unknown",
                "germination_time": plant.germination_time or "unknown",
                "planting_depth": plant.planting_depth or "unknown",
                "spacing": plant.spacing or "unknown",
                "sun_requirements": plant.sun_requirements or "unknown",
                "indoor_start_time": plant.indoor_start_time or "unknown",
                "seed_packet_id": plant.seed_packet_id or "unknown",
                "genus_id": plant.genus_id or "unknown",
            }
            markdown_plant = MarkdownPlant(backup_data)
            filepath = database_dir / f"{plant.id}.md"
            _write_markdown_backup(filepath, markdown_plant)
        else:
            # Fallback to Markdown-only mode
            plant = MarkdownPlant(plant_data)
            filepath = database_dir / f"{plant.data['id']}.md"
            _write_markdown_backup(filepath, plant)
            plant_id = plant.data["id"]

        genus_id = plant_data.get("genus_id", "unknown")
        if not db:
            plant_id = plant.data["id"]
            genus_id = plant.data.get("genus_id", "unknown")

        print("\n✓ Plant record created successfully!")
        print(f"ID: {plant_id}")
        if genus_id and genus_id != "unknown":
            print(f"Genus: {genus_id}")
        print(f"Saved to: {filepath}")
        print("\nNext steps:")
        print(
            f"  1. Generate/print label: plant-tracking print-label {plant_id}"
        )
        print(
            f"  2. Generate image only: plant-tracking print-label {plant_id} --no-print"
        )
        print(
            f"  3. Use 50x70mm format: plant-tracking print-label {plant_id} --format 50x70mm"
        )

    except Exception as e:
        print(f"\n✗ Error creating plant record: {e}")
        sys.exit(1)


def _prompt_packet_choice(plant_data):
    """Prompt user to choose how to handle seed packet.

    Returns 'create', 'select', or 'skip'.
    """
    print()
    print("No matching seed packet found. How would you like to proceed?")
    print("  (A) Create a new seed packet now")
    print("  (B) Select an existing seed packet from list")
    print("  (C) Skip - no packet info available (fields entered directly)")
    choice = input("Choose [A/B/C]: ").strip().upper()
    if choice == "A":
        return "create"
    elif choice == "B":
        return "select"
    else:
        return "skip"


def _create_packet_inline(plant_data, db, packets_dir):
    """Create a seed packet inline during plant creation.

    Returns the created packet ID.
    """
    print()
    print("--- Create new seed packet ---")
    packet_data = {
        "variety_name": plant_data["variety_name"],
        "latin_name": plant_data["latin_name"],
    }

    optional_fields = [
        ("brand", "Brand/company name"),
        ("days_to_maturity", "Days to maturity (e.g., 60-75)"),
        ("germination_time", "Germination time (e.g., 7-14 days)"),
        ("planting_depth", "Planting depth (e.g., 0.25 inches)"),
        ("spacing", "Plant spacing (e.g., 18 inches)"),
        ("sun_requirements", "Sun requirements (e.g., Full sun)"),
        ("indoor_start_time", "Indoor start time (e.g., 8 weeks before last frost)"),
    ]
    for field, description in optional_fields:
        _prompt_optional_field(field, description, packet_data)

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                packet = uow.seed_packets.create_seed_packet(packet_data)
                # Markdown backup
                backup_data = packet_data.copy()
                backup_data["id"] = packet.id
                markdown_packet = MarkdownSeedPacket(backup_data)
                filepath = packets_dir / f"{packet.id}.md"
                _write_markdown_backup(filepath, markdown_packet)
                print(f"\n✓ Seed packet created: {packet.id}")
                return packet.id
        elif db:
            # Fallback to original models
            from .models import SeedPacket

            packet = SeedPacket.create_from_dict(packet_data)
            with db.get_db() as session:
                session.add(packet)
                session.commit()

            # Markdown backup
            backup_data = packet_data.copy()
            backup_data["id"] = packet.id
            markdown_packet = MarkdownSeedPacket(backup_data)
            filepath = packets_dir / f"{packet.id}.md"
            _write_markdown_backup(filepath, markdown_packet)
            print(f"\n✓ Seed packet created: {packet.id}")
            return packet.id
        else:
            # Markdown fallback
            packet = MarkdownSeedPacket(packet_data)
            filepath = packets_dir / f"{packet.data['id']}.md"
            _write_markdown_backup(filepath, packet)
            print(f"\n✓ Seed packet created: {packet.data['id']}")
            return packet.data["id"]
    except Exception as e:
        print(f"Error creating seed packet: {e}")
        raise


def _select_existing_packet(db):
    """Show existing packets and let user select by ID.

    Returns the selected packet ID or None.
    """
    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                packets = list(uow.seed_packets.list_seed_packets())
        elif db:
            # Fallback to original models
            from .models import SeedPacket

            packets = SeedPacket.list_all()
        else:
            # Markdown fallback
            packets = markdown_list_all()

        if not packets:
            print("No seed packets exist yet.")
            return None

        print()
        print("Existing seed packets:")
        for p in packets:
            if db and SERVICE_AVAILABLE:
                brand = p.brand or ""
                pid = p.id
                variety = p.variety_name
                latin = p.latin_name
            elif db:
                # Fallback to original models
                brand = p.brand or ""
                pid = p.id
                variety = p.variety_name
                latin = p.latin_name
            else:
                # Markdown fallback
                brand = p.data.get("brand", "")
                pid = p.data["id"]
                variety = p.data["variety_name"]
                latin = p.data["latin_name"]
            print(f"  {pid:<12} {variety:<25} {latin:<25} {brand}")
        print()
        packet_id = input("Enter packet ID to use (or empty to skip): ").strip()
        if packet_id:
            return packet_id
        return None
    except Exception:
        return None


def _prompt_record_fields(plant_data):
    """Prompt for record-keeping fields when no seed packet is used."""
    print()
    print("--- Optional record fields (enter directly, no seed packet) ---")
    record_fields = [
        ("brand", "Brand/company name"),
        ("days_to_maturity", "Days to maturity (e.g., 60-75)"),
        ("germination_time", "Germination time (e.g., 7-14 days)"),
        ("planting_depth", "Planting depth (e.g., 0.25 inches)"),
        ("spacing", "Plant spacing (e.g., 18 inches)"),
        ("sun_requirements", "Sun requirements (e.g., Full sun)"),
        ("indoor_start_time", "Indoor start time (e.g., 8 weeks before last frost)"),
    ]
    for field, description in record_fields:
        _prompt_optional_field(field, description, plant_data)


def _prompt_genus_choice(plant_data):
    """Prompt user to choose genus handling method.

    Returns 'create', 'select', 'fuzzy', or 'skip'.
    """
    print()
    print("No matching genus found. How would you like to proceed?")
    print("  (A) Create a new genus now")
    print("  (B) Select an existing genus from list")
    print("  (C) Skip - enter Latin name manually (no genus reference)")
    if FUZZY_MATCHING_AVAILABLE:
        print("  (F) Fuzzy search for similar genus names")
    choice = (
        input("Choose [A/B/C" + ("/F" if FUZZY_MATCHING_AVAILABLE else "") + "]: ")
        .strip()
        .upper()
    )
    if choice == "A":
        return "create"
    elif choice == "B":
        return "select"
    elif choice == "F" and FUZZY_MATCHING_AVAILABLE:
        return "fuzzy"
    else:
        return "skip"


def _create_genus_inline(plant_data, db, genera_dir):
    """Create a genus inline during plant creation.

    Returns the created genus ID.
    """
    print()
    print("--- Create new genus ---")
    genus_data = {
        "variety_name": plant_data["variety_name"],
        "latin_name": plant_data["latin_name"],
    }

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                genus = uow.genera.create_genus(genus_data)
                # Markdown backup
                backup_data = genus_data.copy()
                backup_data["id"] = genus.id
                markdown_genus = MarkdownGenus(backup_data)
                filepath = genera_dir / f"{genus.id}.md"
                _write_markdown_backup(filepath, markdown_genus)
                print(f"\n✓ Genus created: {genus.id}")
                return genus.id
        elif db:
            # Fallback to original models
            from .models import Genus

            genus = Genus.create_from_dict(genus_data)
            with db.get_db() as session:
                session.add(genus)
                session.commit()

            # Markdown backup
            backup_data = genus_data.copy()
            backup_data["id"] = genus.id
            markdown_genus = MarkdownGenus(backup_data)
            filepath = genera_dir / f"{genus.id}.md"
            _write_markdown_backup(filepath, markdown_genus)
            print(f"\n✓ Genus created: {genus.id}")
            return genus.id
        else:
            # Markdown fallback
            from .genus_model import Genus

            genus = Genus(genus_data)
            genera_dir.mkdir(parents=True, exist_ok=True)
            filepath = genera_dir / f"{genus.data['id']}.md"
            _write_markdown_backup(filepath, genus)
            print(f"\n✓ Genus created: {genus.data['id']}")
            return genus.data["id"]
    except Exception as e:
        print(f"Error creating genus: {e}")
        raise


def _select_existing_genus(db):
    """Show existing genera and let user select by ID.

    Returns the selected genus ID or None.
    """
    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                genera = list(uow.genera.list_genera())
        elif db:
            # Fallback to original models
            from .models import Genus

            genera = Genus.list_all()
        else:
            # Markdown fallback
            from .genus_model import list_all

            genera = list_all()

        if not genera:
            print("No genera exist yet.")
            return None

        print()
        print("Existing genera:")
        for g in genera:
            if db and SERVICE_AVAILABLE:
                gid = g.id
                variety = g.variety_name
                latin = g.latin_name
            elif db:
                # Fallback to original models
                gid = g.id
                variety = g.variety_name
                latin = g.latin_name
            else:
                # Markdown fallback
                gid = g.data["id"]
                variety = g.data["variety_name"]
                latin = g.data["latin_name"]
            print(f"  {gid:<12} {variety:<25} {latin:<25}")
        print()
        genus_id = input("Enter genus ID to use (or empty to skip): ").strip()
        if genus_id:
            return genus_id
        return None
    except Exception:
        return None


def _fuzzy_search_genus(variety_name: str, db):
    """Search for genus using fuzzy matching on variety_name.

    Returns matched genus ID if good match found, otherwise None.
    """
    if not FUZZY_MATCHING_AVAILABLE:
        return None

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                genera = list(uow.genera.list_genera())
                genus_choices = {g.variety_name: g.id for g in genera}
                variety_names = list(genus_choices.keys())
        elif db:
            # Fallback to original models
            from .models import Genus

            genera = Genus.list_all()
            genus_choices = {g.variety_name: g.id for g in genera}
            variety_names = list(genus_choices.keys())
        else:
            # Markdown fallback
            from .genus_model import list_all

            genera = list_all()
            genus_choices = {g.data["variety_name"]: g.data["id"] for g in genera}
            variety_names = list(genus_choices.keys())

        if not variety_names:
            return None

        match_result = process.extractOne(
            variety_name, variety_names, scorer=fuzz.token_set_ratio
        )

        if match_result and match_result[1] >= 80:
            matched_variety, score = match_result
            return genus_choices[matched_variety]

        return None
    except Exception:
        return None


def print_label(args):
    """Print a label for a plant (consolidated create-label and print-label)"""
    from .printer import print_label as printer_print_label

    try:
        success = printer_print_label(args.plant_id, args.format, args.no_print)
        if success:
            if args.no_print:
                print("✓ Label image generated successfully")
            else:
                print("✓ Label print job submitted successfully")
        else:
            print("✗ Failed to submit label print job")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error printing label: {e}")
        sys.exit(1)


def create_seed_packet(args, db=None, packets_dir=None):
    """Create a new seed packet through interactive prompts."""
    global PACKETS_DIR
    if packets_dir is None:
        packets_dir = PACKETS_DIR
    if db is None:
        db = _get_db()

    print("=== Create New Seed Packet ===")
    print()

    packet_data = {}

    print("--- Required fields ---")
    _prompt_field("variety_name", "Variety name (e.g., Yellow Habanero)", packet_data)
    _prompt_field("latin_name", "Latin name (e.g., Capsicum chinense)", packet_data)

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                # Check for existing matching seed packet
                for existing in uow.seed_packets.list_seed_packets():
                    if (
                        existing.variety_name == packet_data["variety_name"]
                        and existing.latin_name == packet_data["latin_name"]
                    ):
                        print("\n⚠ A matching seed packet already exists:")
                        print(f"  ID: {existing.id}")
                        print(
                            f"  Variety: {existing.variety_name} ({existing.latin_name})"
                        )
                        if existing.brand:
                            print(f"  Brand: {existing.brand}")
                        resp = input("\nCreate anyway? (y/N): ").strip().lower()
                        if resp != "y":
                            print("Cancelled.")
                            return
                        break
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import SeedPacket

        existing = SeedPacket.find_matching(
            packet_data["variety_name"], packet_data["latin_name"]
        )
        if existing:
            print("\n⚠ A matching seed packet already exists:")
            print(f"  ID: {existing.id}")
            print(f"  Variety: {existing.variety_name} ({existing.latin_name})")
            if existing.brand:
                print(f"  Brand: {existing.brand}")
            resp = input("\nCreate anyway? (y/N): ").strip().lower()
            if resp != "y":
                print("Cancelled.")
                return
    else:
        # Markdown fallback
        existing = markdown_find_matching(
            packet_data["variety_name"], packet_data["latin_name"]
        )
        if existing:
            print("\n⚠ A matching seed packet already exists:")
            print(f"  ID: {existing.data['id']}")
            print(
                f"  Variety: {existing.data['variety_name']} ({existing.data['latin_name']})"
            )
            if existing.data.get("brand"):
                print(f"  Brand: {existing.data['brand']}")
            resp = input("\nCreate anyway? (y/N): ").strip().lower()
            if resp != "y":
                print("Cancelled.")
                return

    print()
    print("--- Optional fields ---")
    optional_fields = [
        ("brand", "Brand/company name"),
        ("days_to_maturity", "Days to maturity (e.g., 60-75)"),
        ("germination_time", "Germination time (e.g., 7-14 days)"),
        ("planting_depth", "Planting depth (e.g., 0.25 inches)"),
        ("spacing", "Plant spacing (e.g., 18 inches)"),
        ("sun_requirements", "Sun requirements (e.g., Full sun)"),
        ("indoor_start_time", "Indoor start time (e.g., 8 weeks before last frost)"),
    ]
    for field, description in optional_fields:
        _prompt_optional_field(field, description, packet_data)

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                packet = uow.seed_packets.create_seed_packet(packet_data)
                # Markdown backup
                backup_data = packet_data.copy()
                backup_data["id"] = packet.id
                markdown_packet = MarkdownSeedPacket(backup_data)
                filepath = packets_dir / f"{packet.id}.md"
                _write_markdown_backup(filepath, markdown_packet)

                print("\n✓ Seed packet created successfully!")
                print(f"ID: {packet.id}")
                print(f"Saved to: {filepath}")
        elif db:
            # Fallback to original models
            from .models import SeedPacket

            packet = SeedPacket.create_from_dict(packet_data)
            with db.get_db() as session:
                session.add(packet)
                session.commit()

            # Markdown backup
            backup_data = packet_data.copy()
            backup_data["id"] = packet.id
            markdown_packet = MarkdownSeedPacket(backup_data)
            filepath = packets_dir / f"{packet.id}.md"
            _write_markdown_backup(filepath, markdown_packet)

            print("\n✓ Seed packet created successfully!")
            print(f"ID: {packet.id}")
            print(f"Saved to: {filepath}")
        else:
            # Markdown fallback
            packet = MarkdownSeedPacket(packet_data)
            filepath = packets_dir / f"{packet.data['id']}.md"
            _write_markdown_backup(filepath, packet)

            print("\n✓ Seed packet created successfully!")
            print(f"ID: {packet.data['id']}")
            print(f"Saved to: {filepath}")
    except Exception as e:
        print(f"\n✗ Error creating seed packet: {e}")
        sys.exit(1)


def list_seed_packets(args, db=None):
    """List all seed packets in a table format."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                packets = list(uow.seed_packets.list_seed_packets())
        except Exception:
            # Fallback to original models if service fails
            if db:
                from .models import SeedPacket

                packets = SeedPacket.list_all()
            else:
                packets = markdown_list_all()
    elif db:
        # Fallback to original models
        from .models import SeedPacket

        packets = SeedPacket.list_all()
    else:
        # Markdown fallback
        packets = markdown_list_all()

    if not packets:
        print("No seed packets found.")
        return

    header = f"{'ID':<12} {'Variety':<25} {'Latin Name':<25} {'Brand':<20}"
    separator = f"{'-' * 12}  {'-' * 25}  {'-' * 25}  {'-' * 20}"
    print(header)
    print(separator)
    for p in packets:
        if db and SERVICE_AVAILABLE:
            brand = p.brand or ""
            pid = p.id
            variety = p.variety_name
            latin = p.latin_name
        elif db:
            # Fallback to original models
            brand = p.brand or ""
            pid = p.id
            variety = p.variety_name
            latin = p.latin_name
        else:
            # Markdown fallback
            brand = p.data.get("brand", "")
            pid = p.data["id"]
            variety = p.data["variety_name"]
            latin = p.data["latin_name"]
        print(
            f"{pid:<12} {variety:<25} {latin:<25} {brand:<20}"
        )


def show_seed_packet(args, db=None):
    """Show full details of a seed packet."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                packet = uow.seed_packets.get_seed_packet(args.packet_id)
                if not packet:
                    print(f"✗ Seed packet not found: {args.packet_id}")
                    sys.exit(1)
                    return

                print(f"=== Seed Packet: {packet.id} ===")
                print()
                fields_to_show = [
                    ("variety_name", "Variety"),
                    ("latin_name", "Latin Name"),
                    ("brand", "Brand"),
                    ("days_to_maturity", "Days to Maturity"),
                    ("germination_time", "Germination Time"),
                    ("planting_depth", "Planting Depth"),
                    ("spacing", "Spacing"),
                    ("sun_requirements", "Sun Requirements"),
                    ("indoor_start_time", "Indoor Start Time"),
                ]
                for field, label in fields_to_show:
                    val = getattr(packet, field, None)
                    if val:
                        print(f"  {label:<22} {val}")
                print()
                if packet.created_at:
                    print(f"  Created: {packet.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
                if packet.updated_at:
                    print(f"  Updated: {packet.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        except Exception as e:
            print(f"✗ Error showing seed packet: {e}")
            sys.exit(1)
    elif db:
        # Fallback to original models
        from .models import SeedPacket

        with db.get_db() as session:
            packet = session.query(SeedPacket).filter_by(id=args.packet_id).first()

        if not packet:
            print(f"✗ Seed packet not found: {args.packet_id}")
            sys.exit(1)
            return

        print(f"=== Seed Packet: {packet.id} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
            ("brand", "Brand"),
            ("days_to_maturity", "Days to Maturity"),
            ("germination_time", "Germination Time"),
            ("planting_depth", "Planting Depth"),
            ("spacing", "Spacing"),
            ("sun_requirements", "Sun Requirements"),
            ("indoor_start_time", "Indoor Start Time"),
        ]
        for field, label in fields_to_show:
            val = getattr(packet, field, None)
            if val:
                print(f"  {label:<22} {val}")
        print()
        if packet.created_at:
            print(f"  Created: {packet.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        if packet.updated_at:
            print(f"  Updated: {packet.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    else:
        # Markdown fallback
        from .seed_packet_model import load_from_file

        filepath = get_seed_packets_dir() / f"{args.packet_id}.md"
        if not filepath.exists():
            print(f"✗ Seed packet not found: {args.packet_id}")
            sys.exit(1)
            return

        packet = load_from_file(filepath)
        print(f"=== Seed Packet: {packet.data['id']} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
            ("brand", "Brand"),
            ("days_to_maturity", "Days to Maturity"),
            ("germination_time", "Germination Time"),
            ("planting_depth", "Planting Depth"),
            ("spacing", "Spacing"),
            ("sun_requirements", "Sun Requirements"),
            ("indoor_start_time", "Indoor Start Time"),
        ]
        for field, label in fields_to_show:
            val = packet.data.get(field)
            if val:
                print(f"  {label:<22} {val}")
        print()
        print(f"  Created: {packet.data.get('created_at', 'N/A')}")
        print(f"  Updated: {packet.data.get('updated_at', 'N/A')}")


def create_genus(args, db=None, genera_dir=None):
    """Create a new genus through interactive prompts."""
    global GENERA_DIR
    if genera_dir is None:
        genera_dir = GENERA_DIR
    if db is None:
        db = _get_db()

    print("=== Create New Genus ===")
    print()

    genus_data = {}

    print("--- Required fields ---")
    _prompt_field("variety_name", "Variety name (e.g., Yellow Habanero)", genus_data)
    _prompt_field("latin_name", "Latin name (e.g., Capsicum chinense)", genus_data)

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                # Check for existing matching genus
                for existing in uow.genera.list_genera():
                    if (
                        existing.variety_name == genus_data["variety_name"]
                        and existing.latin_name == genus_data["latin_name"]
                    ):
                        print("\n⚠ A matching genus already exists:")
                        print(f"  ID: {existing.id}")
                        print(
                            f"  Variety: {existing.variety_name} ({existing.latin_name})"
                        )
                        resp = input("\nCreate anyway? (y/N): ").strip().lower()
                        if resp != "y":
                            print("Cancelled.")
                            return
                        break
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import Genus

        existing = Genus.find_matching(
            genus_data["variety_name"], genus_data["latin_name"]
        )
        if existing:
            print("\n⚠ A matching genus already exists:")
            print(f"  ID: {existing.id}")
            print(f"  Variety: {existing.variety_name} ({existing.latin_name})")
            resp = input("\nCreate anyway? (y/N): ").strip().lower()
            if resp != "y":
                print("Cancelled.")
                return
    else:
        # Markdown fallback
        from .genus_model import find_matching

        existing = find_matching(
            genus_data["variety_name"], genus_data["latin_name"]
        )
        if existing:
            print("\n⚠ A matching genus already exists:")
            print(f"  ID: {existing.data['id']}")
            print(
                f"  Variety: {existing.data['variety_name']} ({existing.data['latin_name']})"
            )
            resp = input("\nCreate anyway? (y/N): ").strip().lower()
            if resp != "y":
                print("Cancelled.")
                return

    print()
    print("--- No optional fields for genus ---")

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                genus = uow.genera.create_genus(genus_data)
                # Markdown backup
                backup_data = genus_data.copy()
                backup_data["id"] = genus.id
                markdown_genus = MarkdownGenus(backup_data)
                filepath = genera_dir / f"{genus.id}.md"
                _write_markdown_backup(filepath, markdown_genus)

                print("\n✓ Genus created successfully!")
                print(f"ID: {genus.id}")
                print(f"Saved to: {filepath}")
        elif db:
            # Fallback to original models
            from .models import Genus

            genus = Genus.create_from_dict(genus_data)
            with db.get_db() as session:
                session.add(genus)
                session.commit()

            # Markdown backup
            backup_data = genus_data.copy()
            backup_data["id"] = genus.id
            markdown_genus = MarkdownGenus(backup_data)
            filepath = genera_dir / f"{genus.id}.md"
            _write_markdown_backup(filepath, markdown_genus)

            print("\n✓ Genus created successfully!")
            print(f"ID: {genus.id}")
            print(f"Saved to: {filepath}")
        else:
            # Markdown fallback
            from .genus_model import Genus

            genus = Genus(genus_data)
            genera_dir.mkdir(parents=True, exist_ok=True)
            filepath = genera_dir / f"{genus.data['id']}.md"
            _write_markdown_backup(filepath, genus)

            print("\n✓ Genus created successfully!")
            print(f"ID: {genus.data['id']}")
            print(f"Saved to: {filepath}")
    except Exception as e:
        print(f"\n✗ Error creating genus: {e}")
        sys.exit(1)


def list_genera(args, db=None):
    """List all genera in a table format."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                genera = list(uow.genera.list_genera())
        except Exception:
            # Fallback to original models if service fails
            if db:
                from .models import Genus

                genera = Genus.list_all()
            else:
                from .genus_model import list_all

                genera = list_all()
    elif db:
        # Fallback to original models
        from .models import Genus

        genera = Genus.list_all()
    else:
        # Markdown fallback
        from .genus_model import list_all

        genera = list_all()

    if not genera:
        print("No genera found.")
        return

    header = f"{'ID':<12} {'Variety':<25} {'Latin Name':<25}"
    separator = f"{'-' * 12}  {'-' * 25}  {'-' * 25}"
    print(header)
    print(separator)
    for g in genera:
        if db and SERVICE_AVAILABLE:
            gid = g.id
            variety = g.variety_name
            latin = g.latin_name
        elif db:
            # Fallback to original models
            gid = g.id
            variety = g.variety_name
            latin = g.latin_name
        else:
            # Markdown fallback
            gid = g.data["id"]
            variety = g.data["variety_name"]
            latin = g.data["latin_name"]
        print(
            f"{gid:<12} {variety:<25} {latin:<25}"
        )


def show_genus(args, db=None):
    """Show full details of a genus."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                genus = uow.genera.get_genus(args.genus_id)
                if not genus:
                    print(f"✗ Genus not found: {args.genus_id}")
                    sys.exit(1)
                    return

                print(f"=== Genus: {genus.id} ===")
                print()
                fields_to_show = [
                    ("variety_name", "Variety"),
                    ("latin_name", "Latin Name"),
                ]
                for field, label in fields_to_show:
                    val = getattr(genus, field, None)
                    if val:
                        print(f"  {label:<22} {val}")
                print()
                if genus.created_at:
                    print(f"  Created: {genus.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
                if genus.updated_at:
                    print(f"  Updated: {genus.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        except Exception as e:
            print(f"✗ Error showing genus: {e}")
            sys.exit(1)
    elif db:
        # Fallback to original models
        from .models import Genus

        with db.get_db() as session:
            genus = session.query(Genus).filter_by(id=args.genus_id).first()

        if not genus:
            print(f"✗ Genus not found: {args.genus_id}")
            sys.exit(1)
            return

        print(f"=== Genus: {genus.id} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
        ]
        for field, label in fields_to_show:
            val = getattr(genus, field, None)
            if val:
                print(f"  {label:<22} {val}")
        print()
        if genus.created_at:
            print(f"  Created: {genus.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        if genus.updated_at:
            print(f"  Updated: {genus.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    else:
        # Markdown fallback
        from .genus_model import load_from_file

        filepath = get_genera_dir() / f"{args.genus_id}.md"
        if not filepath.exists():
            print(f"✗ Genus not found: {args.genus_id}")
            sys.exit(1)
            return

        genus = load_from_file(filepath)
        print(f"=== Genus: {genus.data['id']} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
        ]
        for field, label in fields_to_show:
            val = genus.data.get(field)
            if val:
                print(f"  {label:<22} {val}")
        print()
        print(f"  Created: {genus.data.get('created_at', 'N/A')}")
        print(f"  Updated: {genus.data.get('updated_at', 'N/A')}")


def _list_plants_from_files():
    """List all plants from markdown files in the database directory."""
    db_dir = get_database_dir()
    if not db_dir.exists():
        return []
    plants = []
    for filepath in sorted(db_dir.glob("*.md")):
        try:
            plants.append(load_plant_from_file(filepath))
        except Exception:
            continue
    return plants


def list_plants(args, db=None):
    """List all plants in a table format."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plants = list(uow.plants.list_plants())
        except Exception:
            # Fallback to original models if service fails
            if db:
                from .models import Plant

                plants = Plant.list_all()
            else:
                plants = _list_plants_from_files()
    elif db:
        # Fallback to original models
        from .models import Plant

        plants = Plant.list_all()
    else:
        # Markdown fallback
        plants = _list_plants_from_files()

    if not plants:
        print("No plants found.")
        return

    header = f"{'ID':<12} {'Variety':<25} {'Latin Name':<25} {'Planting Date':<15}"
    separator = f"{'-' * 12}  {'-' * 25}  {'-' * 25}  {'-' * 15}"
    print(header)
    print(separator)
    for p in plants:
        if db and SERVICE_AVAILABLE:
            pid = p.id
            variety = p.variety_name
            latin = p.latin_name
            planting_date = p.planting_date
        elif db:
            # Fallback to original models
            pid = p.id
            variety = p.variety_name
            latin = p.latin_name
            planting_date = p.planting_date
        else:
            # Markdown fallback
            pid = p.data["id"]
            variety = p.data["variety_name"]
            latin = p.data["latin_name"]
            planting_date = p.data["planting_date"]
        print(
            f"{pid:<12} {variety:<25} {latin:<25} {planting_date:<15}"
        )


def show_plant(args, db=None):
    """Show full details of a plant."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if not plant:
                    print(f"✗ Plant not found: {args.plant_id}")
                    sys.exit(1)
                    return

                print(f"=== Plant: {plant.id} ===")
                print()
                fields_to_show = [
                    ("variety_name", "Variety"),
                    ("latin_name", "Latin Name"),
                    ("brand", "Brand"),
                    ("days_to_maturity", "Days to Maturity"),
                    ("germination_time", "Germination Time"),
                    ("planting_depth", "Planting Depth"),
                    ("spacing", "Spacing"),
                    ("sun_requirements", "Sun Requirements"),
                    ("indoor_start_time", "Indoor Start Time"),
                    ("planting_date", "Planting Date"),
                    ("seed_packet_id", "Seed Packet ID"),
                    ("genus_id", "Genus ID"),
                ]
                for field, label in fields_to_show:
                    val = getattr(plant, field, None)
                    if val:
                        print(f"  {label:<22} {val}")
                print()
                if plant.created_at:
                    print(f"  Created: {plant.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
                if plant.updated_at:
                    print(f"  Updated: {plant.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        except Exception as e:
            print(f"✗ Error showing plant: {e}")
            sys.exit(1)
    elif db:
        # Fallback to original models
        from .models import Plant

        with db.get_db() as session:
            plant = session.query(Plant).filter_by(id=args.plant_id).first()

        if not plant:
            print(f"✗ Plant not found: {args.plant_id}")
            sys.exit(1)
            return

        print(f"=== Plant: {plant.id} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
            ("brand", "Brand"),
            ("days_to_maturity", "Days to Maturity"),
            ("germination_time", "Germination Time"),
            ("planting_depth", "Planting Depth"),
            ("spacing", "Spacing"),
            ("sun_requirements", "Sun Requirements"),
            ("indoor_start_time", "Indoor Start Time"),
            ("planting_date", "Planting Date"),
            ("seed_packet_id", "Seed Packet ID"),
            ("genus_id", "Genus ID"),
        ]
        for field, label in fields_to_show:
            val = getattr(plant, field, None)
            if val:
                print(f"  {label:<22} {val}")
        print()
        if plant.created_at:
            print(f"  Created: {plant.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        if plant.updated_at:
            print(f"  Updated: {plant.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    else:
        # Markdown fallback
        filepath = get_database_dir() / f"{args.plant_id}.md"
        if not filepath.exists():
            print(f"✗ Plant not found: {args.plant_id}")
            sys.exit(1)
            return

        plant = load_plant_from_file(filepath)
        print(f"=== Plant: {plant.data['id']} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
            ("brand", "Brand"),
            ("days_to_maturity", "Days to Maturity"),
            ("germination_time", "Germination Time"),
            ("planting_depth", "Planting Depth"),
            ("spacing", "Spacing"),
            ("sun_requirements", "Sun Requirements"),
            ("indoor_start_time", "Indoor Start Time"),
            ("planting_date", "Planting Date"),
            ("seed_packet_id", "Seed Packet ID"),
            ("genus_id", "Genus ID"),
        ]
        for field, label in fields_to_show:
            val = plant.data.get(field)
            if val:
                print(f"  {label:<22} {val}")
        print()
        print(f"  Created: {plant.data.get('created_at', 'N/A')}")
        print(f"  Updated: {plant.data.get('updated_at', 'N/A')}")


# ─── Log command handlers ────────────────────────────────────────

def log_humidity(args, db=None):
    """Log a humidity reading for a plant."""
    if db is None:
        db = _get_db()

    # Validate plant exists
    plant_exists = False
    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if plant:
                    plant_exists = True
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import Plant

        with db.get_db() as session:
            plant = session.query(Plant).filter_by(id=args.plant_id).first()
            if plant:
                plant_exists = True
    else:
        # Markdown fallback
        plant_file = get_database_dir() / f"{args.plant_id}.md"
        if plant_file.exists():
            plant_exists = True

    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        return

    entry_data = {
        "plant_id": args.plant_id,
        "event_type": "humidity",
        "level": args.level,
    }

    if args.date:
        entry_data["date"] = args.date

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                log_entry = uow.logs.create_log_entry(entry_data)
                print(f"✓ Humidity logged for plant {args.plant_id}")
        elif db:
            # Fallback to original models
            from .models import PlantLogEntry

            log_entry = PlantLogEntry.create_from_dict(entry_data)
            with db.get_db() as session:
                session.add(log_entry)
                session.commit()
            print(f"✓ Humidity logged for plant {args.plant_id}")
        else:
            # Markdown fallback
            from .plant_log_model import PlantLogEntry as MarkdownLogEntry, append_log_entry

            entry = MarkdownLogEntry(entry_data)
            append_log_entry(entry)
            print(f"✓ Humidity logged for plant {args.plant_id}")
    except ValidationException as e:
        print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def log_water(args, db=None):
    """Log a watering event."""
    if db is None:
        db = _get_db()

    # Validate plant exists
    plant_exists = False
    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if plant:
                    plant_exists = True
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import Plant

        with db.get_db() as session:
            plant = session.query(Plant).filter_by(id=args.plant_id).first()
            if plant:
                plant_exists = True
    else:
        # Markdown fallback
        plant_file = get_database_dir() / f"{args.plant_id}.md"

    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        return

    from .plant_log_model import normalize_water_amount

    try:
        water_data = normalize_water_amount(args.amount)
    except ValueError as e:
        print(f"✗ Error: Invalid water amount: {e}")
        return

    entry_data = {
        "plant_id": args.plant_id,
        "event_type": "water",
        "amount_ml": int(water_data["value_ml"]),
        "amount_display": f"{water_data['display_value']} {water_data['display_unit']}",
    }

    if args.date:
        entry_data["date"] = args.date

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                log_entry = uow.logs.create_log_entry(entry_data)
                print(f"✓ Watering logged for plant {args.plant_id}")
        elif db:
            # Fallback to original models
            from .models import PlantLogEntry

            log_entry = PlantLogEntry.create_from_dict(entry_data)
            with db.get_db() as session:
                session.add(log_entry)
                session.commit()
            print(f"✓ Watering logged for plant {args.plant_id}")
        else:
            # Markdown fallback
            from .plant_log_model import PlantLogEntry as MarkdownLogEntry, append_log_entry

            entry = MarkdownLogEntry(entry_data)
            append_log_entry(entry)
            print(f"✓ Watering logged for plant {args.plant_id}")
    except ValidationException as e:
        print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def log_fertilizer(args, db=None):
    """Log a fertilization event."""
    if db is None:
        db = _get_db()

    # Validate plant exists
    plant_exists = False
    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if plant:
                    plant_exists = True
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import Plant

        with db.get_db() as session:
            plant = session.query(Plant).filter_by(id=args.plant_id).first()
            if plant:
                plant_exists = True
    else:
        # Markdown fallback
        plant_file = get_database_dir() / f"{args.plant_id}.md"
        if plant_file.exists():
            plant_exists = True

    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        return

    entry_data = {
        "plant_id": args.plant_id,
        "event_type": "fertilizer",
        "fertilizer_type": args.type,
        "fertilizer_strength": args.strength,
    }

    if args.date:
        entry_data["date"] = args.date

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                log_entry = uow.logs.create_log_entry(entry_data)
                print(f"✓ Fertilizer logged for plant {args.plant_id}")
        elif db:
            # Fallback to original models
            from .models import PlantLogEntry

            log_entry = PlantLogEntry.create_from_dict(entry_data)
            with db.get_db() as session:
                session.add(log_entry)
                session.commit()
            print(f"✓ Fertilizer logged for plant {args.plant_id}")
        else:
            # Markdown fallback
            from .plant_log_model import PlantLogEntry as MarkdownLogEntry, append_log_entry

            # For markdown, use original field names
            md_entry_data = {
                "plant_id": args.plant_id,
                "event_type": "fertilizer",
                "type": args.type,
                "strength": args.strength,
            }
            if args.date:
                md_entry_data["date"] = args.date
            entry = MarkdownLogEntry(md_entry_data)
            append_log_entry(entry)
            print(f"✓ Fertilizer logged for plant {args.plant_id}")
    except ValidationException as e:
        print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def log_note(args, db=None):
    """Log a note for a plant."""
    if db is None:
        db = _get_db()

    # Resolve note text: --text > --file > stdin
    note_text = None
    if args.text is not None:
        note_text = args.text
    elif args.file is not None:
        if args.file == "-":
            note_text = sys.stdin.read()
        else:
            try:
                with open(args.file) as f:
                    note_text = f.read()
            except FileNotFoundError:
                print(f"✗ Error: File not found: {args.file}")
                return
    else:
        # Check if stdin has data (not a terminal)
        if not sys.stdin.isatty():
            note_text = sys.stdin.read()
        else:
            print("Error: No note text provided. Use --text, --file, or pipe to stdin.")
            return

    if not note_text or not note_text.strip():
        print("Error: Note text is empty")
        return

    # Validate plant exists
    plant_exists = False
    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if plant:
                    plant_exists = True
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import Plant

        with db.get_db() as session:
            plant = session.query(Plant).filter_by(id=args.plant_id).first()
            if plant:
                plant_exists = True
    else:
        # Markdown fallback
        plant_file = get_database_dir() / f"{args.plant_id}.md"
        if plant_file.exists():
            plant_exists = True

    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        return

    entry_data = {"plant_id": args.plant_id, "event_type": "note", "text": note_text}

    if args.date:
        entry_data["date"] = args.date

    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                log_entry = uow.logs.create_log_entry(entry_data)
                print(f"✓ Note logged for plant {args.plant_id}")
        elif db:
            # Fallback to original models
            from .models import PlantLogEntry

            log_entry = PlantLogEntry.create_from_dict(entry_data)
            with db.get_db() as session:
                session.add(log_entry)
                session.commit()
            print(f"✓ Note logged for plant {args.plant_id}")
        else:
            # Markdown fallback
            from .plant_log_model import PlantLogEntry as MarkdownLogEntry, append_log_entry

            entry = MarkdownLogEntry(entry_data)
            append_log_entry(entry)
            print(f"✓ Note logged for plant {args.plant_id}")
    except ValidationException as e:
        print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def log_list(args, db=None):
    """List all log entries for a plant."""
    if db is None:
        db = _get_db()

    # Validate plant exists
    plant_exists = False
    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if plant:
                    plant_exists = True
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import Plant

        with db.get_db() as session:
            plant = session.query(Plant).filter_by(id=args.plant_id).first()
            if plant:
                plant_exists = True
    else:
        # Markdown fallback
        plant_file = get_database_dir() / f"{args.plant_id}.md"
        if plant_file.exists():
            plant_exists = True

    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        return

    event_type = None if args.type == "all" else args.type

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                entries = list(uow.logs.list_entries(
                    plant_id=args.plant_id, event_type=event_type
                ))
                # Convert domain objects to dict for display
                entries_dict = []
                for entry in entries:
                    d = {
                        "timestamp": entry.timestamp,
                        "event_type": entry.event_type,
                    }
                    if entry.event_type == "humidity":
                        d["level"] = entry.level
                    elif entry.event_type == "water":
                        d["amount_display"] = f"{entry.amount_ml} ml"
                    elif entry.event_type == "fertilizer":
                        d["type"] = entry.fertilizer_type
                        d["strength"] = entry.fertilizer_strength
                    elif entry.event_type == "note":
                        d["text"] = entry.text
                    entries_dict.append(d)
        except Exception:
            # Fallback to original models if service fails
            if db:
                from .models import PlantLogEntry

                entries = PlantLogEntry.load_entries(
                    plant_id=args.plant_id, event_type=event_type
                )
                # Convert ORM objects to dict for display
                entries_dict = []
                for entry in entries:
                    d = {
                        "timestamp": entry.timestamp,
                        "event_type": entry.event_type,
                    }
                    if entry.event_type == "humidity":
                        d["level"] = entry.level
                    elif entry.event_type == "water":
                        d["amount_display"] = f"{entry.amount_ml} ml"
                    elif entry.event_type == "fertilizer":
                        d["type"] = entry.fertilizer_type
                        d["strength"] = entry.fertilizer_strength
                    elif entry.event_type == "note":
                        d["text"] = entry.text
                    entries_dict.append(d)
            else:
                # Markdown fallback
                from .plant_log_model import load_log_entries

                entries_dict = load_log_entries(plant_id=args.plant_id, event_type=event_type)
    elif db:
        # Fallback to original models
        from .models import PlantLogEntry

        entries = PlantLogEntry.load_entries(
            plant_id=args.plant_id, event_type=event_type
        )
        # Convert ORM objects to dict for display
        entries_dict = []
        for entry in entries:
            d = {
                "timestamp": entry.timestamp,
                "event_type": entry.event_type,
            }
            if entry.event_type == "humidity":
                d["level"] = entry.level
            elif entry.event_type == "water":
                d["amount_display"] = f"{entry.amount_ml} ml"
            elif entry.event_type == "fertilizer":
                d["type"] = entry.fertilizer_type
                d["strength"] = entry.fertilizer_strength
            elif entry.event_type == "note":
                d["text"] = entry.text
            entries_dict.append(d)
    else:
        # Markdown fallback
        from .plant_log_model import load_log_entries

        entries_dict = load_log_entries(plant_id=args.plant_id, event_type=event_type)

    if not entries_dict:
        print(f"No log entries found for plant {args.plant_id}")
        return

    print(f"\nLog entries for plant {args.plant_id}:")
    print("-" * 80)

    for entry in entries_dict:
        timestamp = entry.get("timestamp", "Unknown")
        display_date = timestamp.split("T")[0] if "T" in timestamp else timestamp

        event_type = entry.get("event_type", "unknown")
        date_str = f" [{entry.get('date', 'today')}]" if entry.get("date") else ""

        if event_type == "humidity":
            level = entry.get("level", "N/A")
            print(f"{display_date}{date_str} | Humidity: {level}/10")
        elif event_type == "water":
            amount = entry.get("amount_display", "N/A")
            print(f"{display_date}{date_str} | Water: {amount}")
        elif event_type == "fertilizer":
            ftype = entry.get("type", "N/A")
            strength = entry.get("strength", "N/A")
            print(f"{display_date}{date_str} | Fertilizer: {ftype} ({strength})")
        elif event_type == "note":
            text = entry.get("text", "N/A")
            display_text = text[:50] + "..." if len(text) > 50 else text
            print(f"{display_date}{date_str} | Note: {display_text}")

    print("-" * 80)
    print(f"Total entries: {len(entries_dict)}")


# ─── Media command handlers ─────────────────────────────────────

def media_add_attachment(args, db=None, media_type="image"):
    """Handle adding media attachment (image, video, audio)."""
    if db is None:
        db = _get_db()

    file_path = getattr(args, f"{media_type}_path")
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    plant_exists = False
    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if plant:
                    plant_exists = True
        except Exception:
            pass
    else:
        plant_file = get_database_dir() / f"{args.plant_id}.md"
        if plant_file.exists():
            plant_exists = True

    if not plant_exists:
        print(f"Error: Plant ID '{args.plant_id}' not found")
        return

    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        return

    try:
        from plant_service.service_layer.s3_service import S3Service
        from plant_service.service_layer.media_attachment_service_impl import (
            MediaAttachmentServiceImpl,
        )

        with create_unit_of_work() as uow:
            s3_service = S3Service()
            media_service = MediaAttachmentServiceImpl(
                uow.media_attachments, s3_service
            )

            media_data = {
                "plant_id": args.plant_id,
                "media_type": media_type,
                "label": getattr(args, "label", None),
                "tags": getattr(args, "tags", None),
                "file_path": file_path,
                "filename": os.path.basename(file_path),
            }

            media_attachment = media_service.create_media_attachment(media_data)
            uow.commit()

            print(f"✓ {media_type.capitalize()} attachment created!")
            print(f"ID: {media_attachment.id}")
            print(f"Plant ID: {media_attachment.plant_id}")
            print(f"Timestamp: {media_attachment.timestamp}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error creating {media_type} attachment: {e}")


def media_list_attachments(args, db=None):
    """List media attachments for a plant."""
    if db is None:
        db = _get_db()

    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        return

    try:
        with create_unit_of_work() as uow:
            media_attachments = uow.media_attachments.get_media_attachments_by_plant(
                args.plant_id
            )

            if not media_attachments:
                print(f"No media attachments found for plant {args.plant_id}")
                return

            print(f"Media attachments for plant {args.plant_id}:")
            print(
                f"{'ID':<5} {'Type':<8} {'Label':<25} {'Tags':<30} {'Timestamp':<20}"
            )
            print("-" * 90)
            for ma in media_attachments:
                label = ma.label or ""
                tags = ma.tags or ""
                print(
                    f"{ma.id:<5} {ma.media_type:<8} {label:<25} "
                    f"{tags:<30} {ma.timestamp:<20}"
                )
    except Exception as e:
        print(f"Error listing media attachments: {e}")


def media_show_attachment(args, db=None):
    """Show media attachment details."""
    if db is None:
        db = _get_db()

    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        return

    try:
        with create_unit_of_work() as uow:
            media_attachment = uow.media_attachments.get_media_attachment(
                args.media_id
            )

            if not media_attachment:
                print(f"Media attachment not found: {args.media_id}")
                return

            print(f"=== Media Attachment: {media_attachment.id} ===")
            print()
            print(f"Plant ID: {media_attachment.plant_id}")
            print(f"Media Type: {media_attachment.media_type}")
            print(f"S3 Key: {media_attachment.s3_key}")
            print(f"Label: {media_attachment.label or 'N/A'}")
            print(f"Tags: {media_attachment.tags or 'N/A'}")
            print(f"Timestamp: {media_attachment.timestamp}")
    except Exception as e:
        print(f"Error showing media attachment: {e}")


def media_delete_attachment(args, db=None):
    """Delete media attachment."""
    if db is None:
        db = _get_db()

    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        return

    try:
        from plant_service.service_layer.s3_service import S3Service

        with create_unit_of_work() as uow:
            media_attachment = uow.media_attachments.get_media_attachment(
                args.media_id
            )
            if not media_attachment:
                print(f"Media attachment not found: {args.media_id}")
                return

            s3_service = S3Service()
            s3_service.delete_file(media_attachment.s3_key)

            success = uow.media_attachments.delete_media_attachment(args.media_id)
            if success:
                uow.commit()
                print(f"✓ Media attachment {args.media_id} deleted successfully")
            else:
                print(f"Failed to delete media attachment {args.media_id}")
    except Exception as e:
        print(f"Error deleting media attachment: {e}")


def media_get_url(args, db=None):
    """Get presigned URL for media attachment."""
    if db is None:
        db = _get_db()

    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        return

    try:
        from plant_service.service_layer.s3_service import S3Service

        with create_unit_of_work() as uow:
            media_attachment = uow.media_attachments.get_media_attachment(
                args.media_id
            )
            if not media_attachment:
                print(f"Media attachment not found: {args.media_id}")
                return

            s3_service = S3Service()
            url = s3_service.get_presigned_url(media_attachment.s3_key)
            if url:
                print(f"URL for media attachment {args.media_id}:")
                print(url)
            else:
                print("Failed to generate URL")
    except Exception as e:
        print(f"Error getting media attachment URL: {e}")


if __name__ == "__main__":
    main()
