# Date Fixes on Plant Database - Implementation Plan

## Overview

Rename `planned_planting_date` to `planting_date` across schema, CLI, model, labels, tests, and docs. Fix plant ID generation to derive the year from `planting_date` instead of the current year. Run a migration script to update 15 existing plant records.

## Current State

| Aspect | Detail |
|--------|--------|
| Storage | Markdown files with YAML frontmatter in `database/` (15 plant `.md` files, 4 seed packet files) |
| Model | `commands/plant_model.py` — `Plant` class with `LABEL_FIELDS`, `ALL_FIELDS`, `REQUIRED_FIELDS` constants |
| CLI | `commands/plant_tracking_cli.py` — `create-plant` prompts for `planned_planting_date` on line 127 |
| Labels | `commands/label_generator.py` — reads `planned_planting_date` on line 73 for label rendering |
| Tests | `tests/test_plant_tracking.py` — 15 references to `planned_planting_date` across 6 test classes |
| ID Bug | `plant_model.py:88` — `datetime.now(timezone.utc).year` uses current year, not planting date year |
| Migration | `scripts/migrate_seed_packets.py` — existing pattern for one-shot migration with `--dry-run` |

## Key Findings

1. **Three code targets** for field rename: `plant_model.py` (6 occurrences), `plant_tracking_cli.py` (1), `label_generator.py` (1)
2. **One ID generation bug** at `plant_model.py:88` — single line fix: extract year from `self.data['planting_date']` instead of `datetime.now().year`
3. **15 database records** need migration — all contain `planned_planting_date` in YAML frontmatter (e.g., YEHA-2026-001 has `planned_planting_date: '2024-10-15'` but ID says 2026)
4. **15 test references** all in `tests/test_plant_tracking.py` — both helper methods and individual test data dicts
5. **Two doc files** need updates: `knowledge/specs/database.md` and `docs/user.md`

## What We're NOT Doing

- Retroactive fix of existing plant IDs (YEHA-2026-001 stays as-is since labels are already printed/in use)
- Frontend changes (not known to be affected)
- Soft alias / backward compatibility layer (hard rename only, per ticket)

---

- [x] Step 1.1: Rename field constants
- [x] Step 1.2: Update validation
- [x] Step 1.3: Fix ID generation
- [x] Step 1.4: Add new tests for ID year derivation

## Phase 1: Data Model — Rename + ID Fix

**Goal**: Update `plant_model.py` to use `planting_date` and fix ID year derivation.

**File**: `commands/plant_model.py`

### Step 1.1: Rename field constants (lines 12, 18, 22)

```python
# Before
LABEL_FIELDS = ['variety_name', 'latin_name', 'planned_planting_date']
ALL_FIELDS = [
    'variety_name', 'latin_name', 'brand', 'days_to_maturity',
    'germination_time', 'planting_depth', 'spacing', 'sun_requirements',
    'indoor_start_time', 'planned_planting_date', 'seed_packet_id'
]
REQUIRED_FIELDS = ['variety_name', 'latin_name', 'planned_planting_date']
```

```python
# After
LABEL_FIELDS = ['variety_name', 'latin_name', 'planting_date']
ALL_FIELDS = [
    'variety_name', 'latin_name', 'brand', 'days_to_maturity',
    'germination_time', 'planting_depth', 'spacing', 'sun_requirements',
    'indoor_start_time', 'planting_date', 'seed_packet_id'
]
REQUIRED_FIELDS = ['variety_name', 'latin_name', 'planting_date']
```

### Step 1.2: Update validation (lines 56-60)

```python
# Before
if 'planned_planting_date' in self.data:
    try:
        datetime.strptime(self.data['planned_planting_date'], '%Y-%m-%d')
    except ValueError:
        raise ValueError("planned_planting_date must be in YYYY-MM-DD format")

# After
if 'planting_date' in self.data:
    try:
        datetime.strptime(self.data['planting_date'], '%Y-%m-%d')
    except ValueError:
        raise ValueError("planting_date must be in YYYY-MM-DD format")
```

### Step 1.3: Fix ID generation (line 88)

```python
# Before
year = datetime.now(timezone.utc).year

# After
planting_date_val = self.data.get('planting_date', '')
if planting_date_val:
    year = datetime.strptime(planting_date_val, '%Y-%m-%d').year
else:
    year = datetime.now(timezone.utc).year  # Fallback for edge cases
```

**Rationale**: The `generate_id()` method is called from `__init__` (line 47) after `validate()` ensures required fields are present. By this point, `planting_date` is guaranteed to exist. The fallback to current year is defensive only — it would only trigger if someone constructs a `Plant` with an `id` already set (skipping `generate_id`), or in test code that bypasses validation. The fallback prevents breakage but should never execute in normal flow.

### Step 1.4: Add new tests for ID year derivation

Add two test methods to `TestPlantModel`:

```python
def test_id_year_from_planting_date_past_year(self):
    """Test that ID year comes from planting_date, not current year."""
    plant_data = self._required_plant_data(
        variety_name='Yellow Habanero',
        latin_name='Capsicum chinense',
        planting_date='2024-05-01',
    )
    plant = self.Plant(plant_data)
    self.assertIn('-2024-', plant.data['id'])

def test_id_year_from_planting_date_future_year(self):
    """Test that ID year comes from planting_date for future dates."""
    next_year = datetime.now(timezone.utc).year + 1
    plant_data = self._required_plant_data(
        variety_name='Tomato',
        latin_name='Solanum lycopersicum',
        planting_date=f'{next_year}-06-01',
    )
    plant = self.Plant(plant_data)
    self.assertIn(f'-{next_year}-', plant.data['id'])
```

**Verify**: `python -m pytest tests/test_plant_tracking.py -v` — all tests pass including new ones.

---

- [x] CLI prompt updated

## Phase 2: CLI Prompt Update

**Goal**: Update CLI prompt text from `planned_planting_date` to `planting_date`.

**File**: `commands/plant_tracking_cli.py`, line 127

```python
# Before
_prompt_field('planned_planting_date', 'Planned planting date (YYYY-MM-DD)', plant_data)

# After
_prompt_field('planting_date', 'Planting date (YYYY-MM-DD)', plant_data)
```

**Verify**: Existing `TestCreatePlantFlow` tests will pass after their data dicts are updated (Phase 4).

---

- [x] Label generator updated

## Phase 3: Label Generator Update

**Goal**: Update label generator to read `planting_date` instead of `planned_planting_date`.

**File**: `commands/label_generator.py`, line 73

```python
# Before
planting_date = plant.data.get('planned_planting_date', '')

# After
planting_date = plant.data.get('planting_date', '')
```

**Verify**: `TestLabelGeneration` tests pass after test data is updated.

---

- [x] Step 4.1: Update helper methods
- [x] Step 4.2: Update inline test data

## Phase 4: Test Suite Update

**Goal**: Update all 15 references to `planned_planting_date` in test file.

**File**: `tests/test_plant_tracking.py`

### Step 4.1: Update helper methods

Lines 35-60 — `_required_plant_data()` and `_full_plant_data()`:
```python
# Before
'planned_planting_date': '2026-05-01',
# After
'planting_date': '2026-05-01',
```

### Step 4.2: Update inline test data

All remaining references use explicit keyword args or dict literals:
- Line 67: `planned_planting_date='2026-05-01'` → `planting_date='2026-05-01'`
- Line 87: same pattern
- Line 98: same pattern
- Line 108: same pattern
- Line 156: `planned_planting_date='05-01-2026'` → `planting_date='05-01-2026'` (invalid format test)
- Lines 251, 270, 294, 307, 337, 713, 736, 755: dict literals with key rename

### Step 4.3: Update date validation error message

Line 156 tests `test_plant_invalid_date_format` — no change needed since the test just checks that `ValueError` is raised, not the specific message. But the error message in `plant_model.py:60` is already updated in Phase 1.

**Verify**: `python -m pytest tests/test_plant_tracking.py -v` — all 38+ tests pass.

---

- [x] Migration script created
- [x] 15 plant records migrated

## Phase 5: Database Migration Script

**Goal**: Create a migration script to rename `planned_planting_date` → `planting_date` in all 15 existing plant records.

**New file**: `scripts/migrate_planting_date.py`

Follows the pattern of `scripts/migrate_seed_packets.py`:

```python
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
```

**Execution order**:
1. `python scripts/migrate_planting_date.py --dry-run` — verify 15 files listed
2. `python scripts/migrate_planting_date.py` — apply migration
3. Manual check: `grep planned_planting_date database/*.md` returns nothing

**Verify**: All plant files now have `planting_date` in frontmatter, no `planned_planting_date` remains.

---

- [x] Step 6.1: database.md updated
- [x] Step 6.2: user.md updated

## Phase 6: Documentation Updates

**Goal**: Update documentation to reflect `planting_date` and corrected ID year behavior.

### Step 6.1: `knowledge/specs/database.md`

| Line | Before | After |
|------|--------|-------|
| 40 | `planned_planting_date: "2026-04-15"` | `planting_date: "2026-04-15"` |
| 61 | `planned_planting_date \| string (YYYY-MM-DD) \| Yes \| Date when planting is planned` | `planting_date \| string (YYYY-MM-DD) \| Yes \| Date when the plant was planted` |
| 66 | `(variety_name, latin_name, planned_planting_date)` | `(variety_name, latin_name, planting_date)` |
| 164 | `planned_planting_date must be valid YYYY-MM-DD` | `planting_date must be valid YYYY-MM-DD` |
| 179 | `planned_planting_date: "2026-04-15"` | `planting_date: "2026-04-15"` |

### Step 6.2: `docs/user.md`

| Line | Before | After |
|------|--------|-------|
| 102 | `planned planting date` | `planting date` |
| 120 | `planned planting date` | `planting date` |
| 142 | `YYYY: Current year` | `YYYY: Year from planting_date` |
| 159 | `planned_planting_date` | `planting_date` |
| 174 | `planned_planting_date: '2025-05-01'` | `planting_date: '2025-05-01'` |

---

## Execution Order & Verification

```
Phase 1: Model rename + ID fix     → pytest passes (after Phase 4 test updates)
Phase 2: CLI prompt                → no independent test, covered by Phase 4
Phase 3: Label generator           → covered by TestLabelGeneration
Phase 4: Test suite                → pytest passes
Phase 5: Migration script          → grep confirms no planned_planting_date in database/
Phase 6: Documentation             → visual review
```

**Final verification** (run after all phases):
```bash
# 1. All tests pass
python -m pytest tests/test_plant_tracking.py -v

# 2. No remaining references to old field name in code
grep -r "planned_planting_date" commands/ tests/   # should return nothing

# 3. No remaining references in database records
grep -r "planned_planting_date" database/           # should return nothing

# 4. ID generation uses planting year
python -c "
import os; os.environ['PLANT_DATABASE_DIR'] = '/tmp/test_id_year'
from pathlib import Path; Path('/tmp/test_id_year').mkdir(exist_ok=True)
from commands.plant_model import Plant
p = Plant({'variety_name': 'Tomato', 'latin_name': 'Solanum lycopersicum', 'planting_date': '2024-06-01'})
assert '-2024-' in p.data['id'], f'Expected -2024- in {p.data[\"id\"]}'
print(f'ID year correct: {p.data[\"id\"]}')
"
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Migration corrupts a file | Low | Medium | `--dry-run` first, git tracks all changes |
| Test import race (module caching) | Low | Low | Tests set env var before import; existing pattern works |
| ID generation fallback triggered unexpectedly | Low | Low | Only triggers without `planting_date`, which validation prevents |

## Rollback Plan

All changes are tracked in git. Rollback = `git revert` or `git reset --hard` to pre-change commit. Migration script changes are purely additive (new file + field rename in existing files), easily reversible.
