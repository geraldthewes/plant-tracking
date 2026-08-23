#!/usr/bin/env python3
"""Verify all existing planting_date values are valid ISO dates.

Pre-migration data guard for PROJ-0014: must pass before applying the
planting_date VARCHAR -> DATE conversion migration, so the ALTER ... USING
cast cannot fail mid-conversion on malformed data.

Uses a raw SQL query (no ORM) so it works against any migration state,
including databases that have not yet applied the death-field revision.

Usage:
    DATABASE_URL=postgresql://... python scripts/verify_planting_dates.py

Exit codes:
    0 - all planting_date values are valid ISO dates
    1 - one or more invalid values found (printed to stdout)
"""
import re
from datetime import date

from sqlalchemy import MetaData, Table, create_engine, select

from plant_service.config import get_database_url

ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def main() -> int:
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    metadata = MetaData()
    plants = Table("plants", metadata, autoload_with=engine)

    with engine.connect() as conn:
        rows = conn.execute(select(plants.c.id, plants.c.planting_date)).all()

    invalid_dates = []
    for plant_id, value in rows:
        if isinstance(value, date):
            continue
        if value is None:
            invalid_dates.append((plant_id, None, "planting_date is NULL"))
            continue
        text = str(value)
        if not ISO_DATE_PATTERN.match(text):
            invalid_dates.append((plant_id, text, "not in YYYY-MM-DD format"))
            continue
        try:
            date.fromisoformat(text)
        except ValueError as e:
            invalid_dates.append((plant_id, text, str(e)))

    if invalid_dates:
        print("ERROR: Found invalid planting_date values:")
        for plant_id, value, error in invalid_dates:
            print(f"  Plant {plant_id}: {value!r} - {error}")
        return 1

    print(f"SUCCESS: All {len(rows)} planting_date values are valid ISO dates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
