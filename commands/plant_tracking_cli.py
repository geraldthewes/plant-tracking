#!/usr/bin/env python3
"""
Plant Tracking CLI - Main entry point for plant tracking commands
"""
import argparse
import sys
import os
from pathlib import Path
from .plant_model import Plant, get_database_dir, ALL_FIELDS, LABEL_FIELDS, RECORD_ONLY

# Ensure database directory exists
DATABASE_DIR = get_database_dir()
DATABASE_DIR.mkdir(exist_ok=True)


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

    args = parser.parse_args()

    if args.command == 'create-plant':
        create_plant(args)
    elif args.command == 'create-label':
        create_label(args)
    elif args.command == 'print-label':
        print_label(args)
    else:
        parser.print_help()


def _prompt_field(field, description, plant_data):
    """Prompt user for a single field value with validation."""
    while True:
        value = input(f"{description}: ").strip()
        if value:
            # Special handling for numeric fields
            if field == 'days_to_maturity':
                try:
                    value = int(value)
                    if value <= 0:
                        print("Please enter a positive number")
                        continue
                except ValueError:
                    print("Please enter a valid integer")
                    continue
            plant_data[field] = value
            break
        else:
            print("This field is required")


def _prompt_optional_field(field, description, plant_data):
    """Prompt user for an optional field value."""
    value = input(f"{description} (optional): ").strip()
    if value:
        if field == 'days_to_maturity':
            try:
                value = int(value)
                if value <= 0:
                    print("Please enter a positive number")
                    return
            except ValueError:
                print("Please enter a valid integer")
                return
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
        ('days_to_maturity', 'Days to maturity (integer)'),
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


if __name__ == "__main__":
    main()
