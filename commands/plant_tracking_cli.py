#!/usr/bin/env python3
"""
Plant Tracking CLI - Main entry point for plant tracking commands
"""
import argparse
import sys
import os
from pathlib import Path
from .plant_model import Plant, get_database_dir, ALL_FIELDS, LABEL_FIELDS, RECORD_ONLY
from .seed_packet_model import (
    SeedPacket, get_seed_packets_dir, find_matching, list_all,
    SEED_PACKET_FIELDS as PACKET_OPTIONAL_FIELDS,
)

# Ensure database directories exist
DATABASE_DIR = get_database_dir()
DATABASE_DIR.mkdir(exist_ok=True)
PACKETS_DIR = get_seed_packets_dir()
PACKETS_DIR.mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Plant Tracking System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # create-plant subcommand
    plant_parser = subparsers.add_parser('create-plant', help='Create a new plant record')

    # create-label subcommand
    label_parser = subparsers.add_parser('create-label', help='Create a label for a plant')
    label_parser.add_argument('plant_id', help='Plant ID for label generation')

    # print-label subcommand
    print_parser = subparsers.add_parser('print-label', help='Print a label for a plant')
    print_parser.add_argument('plant_id', help='Plant ID or label file path')

    # create-seed-packet subcommand
    subparsers.add_parser('create-seed-packet', help='Create a new seed packet record')

    # list-seed-packets subcommand
    subparsers.add_parser('list-seed-packets', help='List all seed packets')

    # show-seed-packet subcommand
    show_spkt_parser = subparsers.add_parser('show-seed-packet', help='Show seed packet details')
    show_spkt_parser.add_argument('packet_id', help='Seed packet ID')

    args = parser.parse_args()

    if args.command == 'create-plant':
        create_plant(args)
    elif args.command == 'create-label':
        create_label(args)
    elif args.command == 'print-label':
        print_label(args)
    elif args.command == 'create-seed-packet':
        create_seed_packet(args)
    elif args.command == 'list-seed-packets':
        list_seed_packets(args)
    elif args.command == 'show-seed-packet':
        show_seed_packet(args)
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
    """Create a new plant record through interactive prompts"""
    print("=== Create New Plant Record ===")
    print("Fields needed for the label are required; record-keeping fields are optional.")
    print()

    # Define fields in logical order
    # Phase 1: Required label fields
    required_fields = [
        ('variety_name', 'Variety name (e.g., Yellow Habanero)'),
        ('latin_name', 'Latin name (e.g., Capsicum chinense)'),
        ('planned_planting_date', 'Planned planting date (YYYY-MM-DD)'),
    ]

    # Phase 2: Record-keeping fields (not on label)
    record_fields = [
        ('brand', 'Brand/company name'),
        ('days_to_maturity', 'Days to maturity (e.g., 60-75)'),
        ('germination_time', 'Germination time (e.g., 7-14 days)'),
        ('planting_depth', 'Planting depth (e.g., 0.25 inches)'),
        ('spacing', 'Plant spacing (e.g., 18 inches)'),
        ('sun_requirements', 'Sun requirements (e.g., Full sun)'),
        ('indoor_start_time', 'Indoor start time (e.g., 8 weeks before last frost)'),
    ]

    plant_data = {}

    print("--- Required fields (needed for label) ---")
    for field, description in required_fields:
        _prompt_field(field, description, plant_data)

    print()
    print("--- Optional record fields (not on label) ---")
    for field, description in record_fields:
        _prompt_optional_field(field, description, plant_data)

    try:
        # Create plant record
        plant = Plant(plant_data)

        # Save to database directory
        filename = f"{plant.data['id']}.md"
        filepath = DATABASE_DIR / filename

        with open(filepath, 'w') as f:
            f.write(plant.to_markdown())

        print(f"\n\u2713 Plant record created successfully!")
        print(f"ID: {plant.data['id']}")
        print(f"Saved to: {filepath}")
        print(f"\nNext steps:")
        print(f"  1. Generate label: python -m commands.plant_tracking_cli create-label {plant.data['id']}")
        print(f"  2. Print label: python -m commands.plant_tracking_cli print-label {plant.data['id']}")

    except Exception as e:
        print(f"\n\u2717 Error creating plant record: {e}")
        sys.exit(1)


def create_label(args):
    """Create a label for a plant"""
    from .label_generator import create_label

    try:
        label_path = create_label(args.plant_id)
        print(f"\u2713 Label created successfully: {label_path}")
        print(f"  Review the label before printing:")
        print(f"    python -m commands.plant_tracking_cli print-label {args.plant_id}")
    except FileNotFoundError as e:
        print(f"\u2717 Error: {e}")
        print(f"  Make sure you've created a plant record first:")
        print(f"    python -m commands.plant_tracking_cli create-plant")
        sys.exit(1)
    except Exception as e:
        print(f"\u2717 Error creating label: {e}")
        sys.exit(1)


def print_label(args):
    """Print a label for a plant"""
    from .printer import print_label

    try:
        success = print_label(args.plant_id)
        if success:
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


if __name__ == "__main__":
    main()
