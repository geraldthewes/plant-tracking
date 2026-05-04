#!/usr/bin/env python3
"""
Plant Tracking CLI - Main entry point for plant tracking commands
"""
import argparse
import sys
from pathlib import Path
from .plant_model import Plant, get_database_dir
from .seed_packet_model import (
    SeedPacket, get_seed_packets_dir, find_matching, list_all,
    SEED_PACKET_FIELDS as PACKET_OPTIONAL_FIELDS,
)
from .genus_model import (
    Genus, get_genera_dir, find_matching as find_genus_matching,
    find_by_variety_name, list_all as list_all_genera
)

# Fuzzy matching for genus name searches
try:
    from thefuzz import process, fuzz
    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    FUZZY_MATCHING_AVAILABLE = False
    process = None
    fuzz = None

# Ensure database directories exist
DATABASE_DIR = get_database_dir()
DATABASE_DIR.mkdir(exist_ok=True)
PACKETS_DIR = get_seed_packets_dir()
PACKETS_DIR.mkdir(exist_ok=True)
GENERA_DIR = get_genera_dir()
GENERA_DIR.mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Plant Tracking System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # create-plant subcommand
    plant_parser = subparsers.add_parser('create-plant', help='Create a new plant record')

    # print-label subcommand (consolidated from create-label and print-label)
    print_parser = subparsers.add_parser('print-label', help='Print a label for a plant (or generate image only)')
    print_parser.add_argument('plant_id', help='Plant ID or label file path')
    print_parser.add_argument('--format', '-f', default='40x30mm',
                              help='Label format (default: 40x30mm)')
    print_parser.add_argument('--no-print', action='store_true',
                              help='Generate label image only, do not print')

    # create-seed-packet subcommand
    subparsers.add_parser('create-seed-packet', help='Create a new seed packet record')

    # list-seed-packets subcommand
    subparsers.add_parser('list-seed-packets', help='List all seed packets')

    # show-seed-packet subcommand
    show_spkt_parser = subparsers.add_parser('show-seed-packet', help='Show seed packet details')
    show_spkt_parser.add_argument('packet_id', help='Seed packet ID')

    # create-genus subcommand
    subparsers.add_parser('create-genus', help='Create a new genus record')

    # list-genera subcommand
    subparsers.add_parser('list-genera', help='List all genera')

    # show-genus subcommand
    show_genus_parser = subparsers.add_parser('show-genus', help='Show genus details')
    show_genus_parser.add_argument('genus_id', help='Genus ID')

    args = parser.parse_args()

    if args.command == 'create-plant':
        create_plant(args)
    elif args.command == 'print-label':
        print_label(args)
    elif args.command == 'create-seed-packet':
        create_seed_packet(args)
    elif args.command == 'list-seed-packets':
        list_seed_packets(args)
    elif args.command == 'show-seed-packet':
        show_seed_packet(args)
    elif args.command == 'create-genus':
        create_genus(args)
    elif args.command == 'list-genera':
        list_genera(args)
    elif args.command == 'show-genus':
        show_genus(args)
    else:
        parser.print_help()


def _prompt_field(field, description, plant_data):
    """Prompt user for a single field value with validation."""
    while True:
        value = input(f"{description}: ").strip()
        if value:
            plant_data[field] = value
            break
        else:
            print("This field is required")


def _prompt_optional_field(field, description, plant_data):
    """Prompt user for an optional field value."""
    value = input(f"{description} (optional): ").strip()
    if value:
        plant_data[field] = value


def create_plant(args):
    """Create a new plant record through interactive prompts with genus lookup."""
    print("=== Create New Plant Record ===")
    print("Fields needed for the label are required; record-keeping fields are optional.")
    print()

    plant_data = {}

    # Phase 1: Ask for variety name to look up genus
    print("--- Variety identification (used for label & genus lookup) ---")
    _prompt_field('variety_name', 'Variety name (e.g., Yellow Habanero)', plant_data)

    # Try exact match by variety name first
    existing_genus = find_by_variety_name(plant_data['variety_name'])

    if existing_genus:
        print(f"\n\u2713 Found genus: {existing_genus.data['id']} - {existing_genus.data['variety_name']}")
        print(f"  Latin name: {existing_genus.data['latin_name']}")
        plant_data['latin_name'] = existing_genus.data['latin_name']
        plant_data['genus_id'] = existing_genus.data['id']
        print("  Latin name auto-resolved from genus database.")
    else:
        # Try fuzzy search automatically
        matched_genus_id = _fuzzy_search_genus(plant_data['variety_name'])
        if matched_genus_id:
            # Find the matched genus to show details
            all_genera = list_all_genera()
            matched_genus = next((g for g in all_genera if g.data['id'] == matched_genus_id), None)
            if matched_genus:
                print(f"\n\u2713 Fuzzy match found: {matched_genus.data['id']} - {matched_genus.data['variety_name']}")
                print(f"  Latin name: {matched_genus.data['latin_name']}")
                confirm = input("Use this genus? (Y/n): ").strip().lower()
                if confirm != 'n':
                    plant_data['latin_name'] = matched_genus.data['latin_name']
                    plant_data['genus_id'] = matched_genus.data['id']
                    print("  Latin name auto-resolved from genus database.")

        # If still no match, ask for Latin name
        if 'latin_name' not in plant_data:
            _prompt_field('latin_name', 'Latin name (e.g., Capsicum chinense)', plant_data)

            # Offer to create new genus entry
            create_genus = input("Create a new genus entry for this variety? (y/N): ").strip().lower()
            if create_genus == 'y':
                plant_data['genus_id'] = _create_genus_inline(plant_data)
            else:
                plant_data['genus_id'] = 'unknown'

    # Phase 2: Plant-specific required field (always asked)
    print()
    print("--- Plant-specific field ---")
    _prompt_field('planting_date', 'Planting date (YYYY-MM-DD)', plant_data)

    try:
        plant = Plant(plant_data)

        filename = f"{plant.data['id']}.md"
        filepath = DATABASE_DIR / filename

        with open(filepath, 'w') as f:
            f.write(plant.to_markdown())

        print(f"\n\u2713 Plant record created successfully!")
        print(f"ID: {plant.data['id']}")
        if plant_data.get('genus_id') and plant_data['genus_id'] != 'unknown':
            print(f"Genus: {plant_data['genus_id']}")
        print(f"Saved to: {filepath}")
        print(f"\nNext steps:")
        print(f"  1. Generate/print label: plant-tracking print-label {plant.data['id']}")
        print(f"  2. Generate image only: plant-tracking print-label {plant.data['id']} --no-print")
        print(f"  3. Use 50x70mm format: plant-tracking print-label {plant.data['id']} --format 50x70mm")

    except Exception as e:
        print(f"\n\u2717 Error creating plant record: {e}")
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
    if choice == 'A':
        return 'create'
    elif choice == 'B':
        return 'select'
    else:
        return 'skip'


def _create_packet_inline(plant_data):
    """Create a seed packet inline during plant creation.
    
    Returns the created packet ID.
    """
    print()
    print("--- Create new seed packet ---")
    packet_data = {
        'variety_name': plant_data['variety_name'],
        'latin_name': plant_data['latin_name'],
    }

    optional_fields = [
        ('brand', 'Brand/company name'),
        ('days_to_maturity', 'Days to maturity (e.g., 60-75)'),
        ('germination_time', 'Germination time (e.g., 7-14 days)'),
        ('planting_depth', 'Planting depth (e.g., 0.25 inches)'),
        ('spacing', 'Plant spacing (e.g., 18 inches)'),
        ('sun_requirements', 'Sun requirements (e.g., Full sun)'),
        ('indoor_start_time', 'Indoor start time (e.g., 8 weeks before last frost)'),
    ]
    for field, description in optional_fields:
        _prompt_optional_field(field, description, packet_data)

    packet = SeedPacket(packet_data)
    filepath = PACKETS_DIR / f"{packet.data['id']}.md"
    with open(filepath, 'w') as f:
        f.write(packet.to_markdown())
    print(f"\n\u2713 Seed packet created: {packet.data['id']}")
    return packet.data['id']


def _select_existing_packet():
    """Show existing packets and let user select by ID.
    
    Returns the selected packet ID or None.
    """
    packets = list_all()
    if not packets:
        print("No seed packets exist yet.")
        return None

    print()
    print("Existing seed packets:")
    for p in packets:
        brand = p.data.get('brand', '')
        print(f"  {p.data['id']:<12} {p.data['variety_name']:<25} {p.data['latin_name']:<25} {brand}")
    print()
    packet_id = input("Enter packet ID to use (or empty to skip): ").strip()
    if packet_id:
        return packet_id
    return None


def _prompt_record_fields(plant_data):
    """Prompt for record-keeping fields when no seed packet is used."""
    print()
    print("--- Optional record fields (enter directly, no seed packet) ---")
    record_fields = [
        ('brand', 'Brand/company name'),
        ('days_to_maturity', 'Days to maturity (e.g., 60-75)'),
        ('germination_time', 'Germination time (e.g., 7-14 days)'),
        ('planting_depth', 'Planting depth (e.g., 0.25 inches)'),
        ('spacing', 'Plant spacing (e.g., 18 inches)'),
        ('sun_requirements', 'Sun requirements (e.g., Full sun)'),
        ('indoor_start_time', 'Indoor start time (e.g., 8 weeks before last frost)'),
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
    choice = input("Choose [A/B/C" + ("/F" if FUZZY_MATCHING_AVAILABLE else "") + "]: ").strip().upper()
    if choice == 'A':
        return 'create'
    elif choice == 'B':
        return 'select'
    elif choice == 'F' and FUZZY_MATCHING_AVAILABLE:
        return 'fuzzy'
    else:
        return 'skip'


def _create_genus_inline(plant_data):
    """Create a genus inline during plant creation.

    Returns the created genus ID.
    """
    print()
    print("--- Create new genus ---")
    genus_data = {
        'variety_name': plant_data['variety_name'],
        'latin_name': plant_data['latin_name'],
    }

    genus = Genus(genus_data)
    genera_dir = get_genera_dir()
    genera_dir.mkdir(parents=True, exist_ok=True)
    filepath = genera_dir / f"{genus.data['id']}.md"
    with open(filepath, 'w') as f:
        f.write(genus.to_markdown())
    print(f"\n\u2713 Genus created: {genus.data['id']}")
    return genus.data['id']


def _select_existing_genus():
    """Show existing genera and let user select by ID.

    Returns the selected genus ID or None.
    """
    genera = list_all_genera()
    if not genera:
        print("No genera exist yet.")
        return None

    print()
    print("Existing genera:")
    for g in genera:
        print(f"  {g.data['id']:<12} {g.data['variety_name']:<25} {g.data['latin_name']:<25}")
    print()
    genus_id = input("Enter genus ID to use (or empty to skip): ").strip()
    if genus_id:
        return genus_id
    return None


def _fuzzy_search_genus(variety_name: str):
    """Search for genus using fuzzy matching on variety_name.

    Returns matched genus ID if good match found, otherwise None.
    """
    if not FUZZY_MATCHING_AVAILABLE:
        return None

    genera = list_all_genera()
    if not genera:
        return None

    genus_choices = {g.data['variety_name']: g.data['id'] for g in genera}
    variety_names = list(genus_choices.keys())

    match_result = process.extractOne(variety_name, variety_names, scorer=fuzz.token_set_ratio)

    if match_result and match_result[1] >= 80:
        matched_variety, score = match_result
        return genus_choices[matched_variety]

    return None


def print_label(args):
    """Print a label for a plant (consolidated create-label and print-label)"""
    from .printer import print_label

    try:
        success = print_label(args.plant_id, args.format, args.no_print)
        if success:
            if args.no_print:
                print(f"\u2713 Label image generated successfully")
            else:
                print(f"\u2713 Label print job submitted successfully")
        else:
            print(f"\u2717 Failed to submit label print job")
            sys.exit(1)
    except Exception as e:
        print(f"\u2717 Error printing label: {e}")
        sys.exit(1)


def create_seed_packet(args):
    """Create a new seed packet through interactive prompts."""
    print("=== Create New Seed Packet ===")
    print()

    packet_data = {}

    print("--- Required fields ---")
    _prompt_field('variety_name', 'Variety name (e.g., Yellow Habanero)', packet_data)
    _prompt_field('latin_name', 'Latin name (e.g., Capsicum chinense)', packet_data)

    existing = find_matching(packet_data['variety_name'], packet_data['latin_name'])
    if existing:
        print(f"\n\u26a0 A matching seed packet already exists:")
        print(f"  ID: {existing.data['id']}")
        print(f"  Variety: {existing.data['variety_name']} ({existing.data['latin_name']})")
        if existing.data.get('brand'):
            print(f"  Brand: {existing.data['brand']}")
        resp = input("\nCreate anyway? (y/N): ").strip().lower()
        if resp != 'y':
            print("Cancelled.")
            return

    print()
    print("--- Optional fields ---")
    optional_fields = [
        ('brand', 'Brand/company name'),
        ('days_to_maturity', 'Days to maturity (e.g., 60-75)'),
        ('germination_time', 'Germination time (e.g., 7-14 days)'),
        ('planting_depth', 'Planting depth (e.g., 0.25 inches)'),
        ('spacing', 'Plant spacing (e.g., 18 inches)'),
        ('sun_requirements', 'Sun requirements (e.g., Full sun)'),
        ('indoor_start_time', 'Indoor start time (e.g., 8 weeks before last frost)'),
    ]
    for field, description in optional_fields:
        _prompt_optional_field(field, description, packet_data)

    try:
        packet = SeedPacket(packet_data)
        filepath = PACKETS_DIR / f"{packet.data['id']}.md"

        with open(filepath, 'w') as f:
            f.write(packet.to_markdown())

        print(f"\n\u2713 Seed packet created successfully!")
        print(f"ID: {packet.data['id']}")
        print(f"Saved to: {filepath}")
    except Exception as e:
        print(f"\n\u2717 Error creating seed packet: {e}")
        sys.exit(1)


def list_seed_packets(args):
    """List all seed packets in a table format."""
    packets = list_all()
    if not packets:
        print("No seed packets found.")
        return

    header = f"{'ID':<12} {'Variety':<25} {'Latin Name':<25} {'Brand':<20}"
    separator = f"{'-'*12}  {'-'*25}  {'-'*25}  {'-'*20}"
    print(header)
    print(separator)
    for p in packets:
        brand = p.data.get('brand', '')
        print(f"{p.data['id']:<12} {p.data['variety_name']:<25} {p.data['latin_name']:<25} {brand:<20}")


def show_seed_packet(args):
    """Show full details of a seed packet."""
    from .seed_packet_model import load_from_file

    filepath = PACKETS_DIR / f"{args.packet_id}.md"
    if not filepath.exists():
        print(f"\u2717 Seed packet not found: {args.packet_id}")
        sys.exit(1)
        return

    packet = load_from_file(filepath)
    print(f"=== Seed Packet: {packet.data['id']} ===")
    print()
    fields_to_show = [
        ('variety_name', 'Variety'),
        ('latin_name', 'Latin Name'),
        ('brand', 'Brand'),
        ('days_to_maturity', 'Days to Maturity'),
        ('germination_time', 'Germination Time'),
        ('planting_depth', 'Planting Depth'),
        ('spacing', 'Spacing'),
        ('sun_requirements', 'Sun Requirements'),
        ('indoor_start_time', 'Indoor Start Time'),
    ]
    for field, label in fields_to_show:
        val = packet.data.get(field)
        if val:
            print(f"  {label:<22} {val}")
    print()
    print(f"  Created: {packet.data.get('created_at', 'N/A')}")
    print(f"  Updated: {packet.data.get('updated_at', 'N/A')}")


def create_genus(args):
    """Create a new genus through interactive prompts."""
    print("=== Create New Genus ===")
    print()

    genus_data = {}

    print("--- Required fields ---")
    _prompt_field('variety_name', 'Variety name (e.g., Yellow Habanero)', genus_data)
    _prompt_field('latin_name', 'Latin name (e.g., Capsicum chinense)', genus_data)

    existing = find_genus_matching(genus_data['variety_name'], genus_data['latin_name'])
    if existing:
        print(f"\n\u26a0 A matching genus already exists:")
        print(f"  ID: {existing.data['id']}")
        print(f"  Variety: {existing.data['variety_name']} ({existing.data['latin_name']})")
        resp = input("\nCreate anyway? (y/N): ").strip().lower()
        if resp != 'y':
            print("Cancelled.")
            return

    print()
    print("--- No optional fields for genus ---")

    try:
        genus = Genus(genus_data)
        genera_dir = get_genera_dir()
        genera_dir.mkdir(parents=True, exist_ok=True)
        filepath = genera_dir / f"{genus.data['id']}.md"

        with open(filepath, 'w') as f:
            f.write(genus.to_markdown())

        print(f"\n\u2713 Genus created successfully!")
        print(f"ID: {genus.data['id']}")
        print(f"Saved to: {filepath}")
    except Exception as e:
        print(f"\n\u2717 Error creating genus: {e}")
        sys.exit(1)


def list_genera(args):
    """List all genera in a table format."""
    genera = list_all_genera()
    if not genera:
        print("No genera found.")
        return

    header = f"{'ID':<12} {'Variety':<25} {'Latin Name':<25}"
    separator = f"{'-'*12}  {'-'*25}  {'-'*25}"
    print(header)
    print(separator)
    for g in genera:
        print(f"{g.data['id']:<12} {g.data['variety_name']:<25} {g.data['latin_name']:<25}")


def show_genus(args):
    """Show full details of a genus."""
    from .genus_model import load_from_file

    filepath = get_genera_dir() / f"{args.genus_id}.md"
    if not filepath.exists():
        print(f"\u2717 Genus not found: {args.genus_id}")
        sys.exit(1)
        return

    genus = load_from_file(filepath)
    print(f"=== Genus: {genus.data['id']} ===")
    print()
    fields_to_show = [
        ('variety_name', 'Variety'),
        ('latin_name', 'Latin Name'),
    ]
    for field, label in fields_to_show:
        val = genus.data.get(field)
        if val:
            print(f"  {label:<22} {val}")
    print()
    print(f"  Created: {genus.data.get('created_at', 'N/A')}")
    print(f"  Updated: {genus.data.get('updated_at', 'N/A')}")


if __name__ == "__main__":
    main()
