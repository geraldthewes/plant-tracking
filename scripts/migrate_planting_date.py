#!/usr/bin/env python3
"""
One-shot migration to rename planned_planting_date -> planting_date
in all existing plant records.

Usage:
    python scripts/migrate_planting_date.py --dry-run
    python scripts/migrate_planting_date.py
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from commands.plant_model import get_database_dir


def migrate(database_dir: Path, dry_run: bool = False) -> None:
    print("=" * 60)
    print("Planting Date Field Migration")
    print("=" * 60)
    print()

    migrated = 0
    skipped = 0

    for filepath in sorted(database_dir.glob("*.md")):
        with open(filepath, 'r') as f:
            content = f.read()

        if not content.startswith('---'):
            skipped += 1
            continue

        parts = content.split('---', 2)
        if len(parts) < 3:
            skipped += 1
            continue

        frontmatter = parts[1]
        body = '---\n' + parts[2]

        data = yaml.safe_load(frontmatter)
        if data is None:
            skipped += 1
            continue

        if 'planned_planting_date' not in data:
            # Already migrated or never had the field
            continue

        # Rename the field
        planting_date_val = data.pop('planned_planting_date')
        data['planting_date'] = planting_date_val
        data['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_frontmatter}---\n\n{body.lstrip(chr(10))}"

        if dry_run:
            print(f"  Would migrate: {filepath.name} ({data.get('id', 'unknown')})")
            print(f"    planned_planting_date: {planting_date_val} -> planting_date: {planting_date_val}")
        else:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"  Migrated: {filepath.name} ({data.get('id', 'unknown')})")

        migrated += 1

    print()
    if dry_run:
        print(f"DRY RUN — no changes made")
        print(f"Would migrate {migrated} plant(s), skip {skipped} non-plant file(s)")
    else:
        print(f"Migration complete: {migrated} plant(s) migrated, {skipped} skipped")


def main():
    parser = argparse.ArgumentParser(description="Migrate planned_planting_date -> planting_date")
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without applying')
    args = parser.parse_args()

    database_dir = get_database_dir()

    if not database_dir.exists():
        print(f"Error: Database directory not found: {database_dir}")
        sys.exit(1)

    migrate(database_dir, args.dry_run)


if __name__ == "__main__":
    main()
