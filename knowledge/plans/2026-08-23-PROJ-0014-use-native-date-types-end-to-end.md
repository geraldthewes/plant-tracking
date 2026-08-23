# Use native date types end-to-end for planting_date and death_date Implementation Plan

## Overview

This implementation plan addresses PROJ-0014: migrating `planting_date` and `death_date` fields from string representations to native date types (`date` objects in Python, `DATE` columns in PostgreSQL) across all layers of the plant tracking system. The goal is to eliminate repeated string parsing, leverage proper date semantics in the database, and prevent format-related bugs.

## Current State Analysis

Currently, both `planting_date` (NOT NULL) and `death_date` (nullable) are stored as `VARCHAR(10)` in PostgreSQL and carried as strings throughout the system:

- **Domain Model** (`packages/plant_service/src/plant_service/domain/plant.py`): Fields are `str` with validation via `strptime` (lines 28, 33, 54-57, 136-139, 162-165, 186-189)
- **ORM Models**: 
  - Service tree: `packages/plant_service/src/plant_service/adapters/repository/models/plant_model.py` (lines 30, 39)
  - Legacy CLI tree: `commands/models/plant.py` (lines 34, 39)
- **Repository**: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py` (lines 27-32) performs string validation
- **API Schemas**: `backend/fastapi/src/plant_tracking_api/schemas.py` already correctly uses `date | None` in responses but accepts `str` in `PlantDeathRequest` (line 8)
- **CLI**: `commands/plant_tracking_cli.py` prompts for and displays dates as strings
- **Migrations**: 
  - Death fields added as `String(10)` in `alembic/versions/a1b2c3d4e5f6_add_death_fields_to_plant.py` (lines 25, 28-30)
  - Planting date column needs migration from `String(10)` to `DATE`

Key issues identified:
1. Repeated `strptime` parsing in domain validation (lines 54-57, 162-165, 186-189 in plant.py)
2. Death date validation in API requests defers to domain instead of Pydantic
3. Postgres columns lack proper DATE semantics for ordering/ranges
4. Migration history shows confusion due to indecisive typing (referenced commits d74cf96, 00d0880, d639c80)

## Desired End State

After implementation, the system will have:
- `planting_date` and `death_date` as `DATE` columns in PostgreSQL
- `Mapped[date]` and `Mapped[Optional[date]]` in both ORM model trees
- `date` objects (not strings) in domain model with default `date.today()` for planting_date
- Native date comparisons in domain (e.g., `death_date >= planting_date`)
- Pydantic validation in API requests (`PlantDeathRequest.death_date: date`)
- CLI parsing via `date.fromisoformat()` and display via `isoformat()`
- Wire format unchanged: ISO-8601 date strings in JSON (`"2026-08-01"`)
- All `strptime`/`strftime("%Y-%m-%d")` usage removed for these two fields

### Key Discoveries:
- Both ORM model trees must be updated atomically as they map the same `plants` table
- API JSON contract remains unchanged (ISO-8601 strings on wire)
- Data guard needed: verify all existing `planting_date` values are valid ISO dates before conversion
- Frontend uses ISO strings correctly and requires no changes
- In-place edit of death column migration is safe only if revision `a1b2c3d4e5f6` remains unapplied everywhere

## What We're NOT Doing

- Changing timestamp fields (`plant_log_entries.timestamp`, `media_attachments.timestamp`) - these require `DateTime(timezone=True)` and are out of scope
- Modifying `created_at`/`updated_at` fields - already correctly typed as `DateTime(timezone=True)`
- Altering numeric-as-string fields (`days_to_maturity`, `germination_time`, etc.) - separate concern
- Changing frontend date handling - wire format stays ISO-8601 strings

## Implementation Approach

We'll implement this change in phases, following a Red/Green TDD approach:
1. Add failing domain tests asserting date-typed fields
2. Update domain model to use date objects
3. Update both ORM model trees
4. Update repository to remove string validation
5. Update API request schema for Pydantic validation
6. Update CLI for proper date parsing/display
7. Create and run data guard verification
8. Create migration for planting_date column and update death column migration
9. Update backlog documentation

Each phase includes both automated and manual verification checkpoints.

## Phase 1: Domain Model Update and Testing

### Overview
Update the domain model to use native date objects and add comprehensive tests to verify the behavior.

### Changes Required:

#### 1. Domain Model: `packages/plant_service/src/plant_service/domain/plant.py`
**Changes**: 
- Change `planting_date` field type from `str` to `date` with default `date.today()`
- Change `death_date` field type from `str | None` to `date | None`
- Remove all `strptime` validation blocks for these fields
- Update `generate_id` method to use `.year` attribute directly on date objects
- Update `validate_death_fields` to work with date objects instead of parsing strings
- Update `__post_init__` to remove date format validation

```python
# Before (lines 28, 33):
planting_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
death_date: str | None = None

# After:
planting_date: date = field(default_factory=date.today)
death_date: date | None = None

# Before (lines 54-57, 136-139, 162-165, 186-189):
# Multiple strptime validation blocks

# After: Remove all strptime validation for planting_date/death_date

# Before (lines 91-94):
if planting_date:
    year = datetime.strptime(planting_date, "%Y-%m-%d").year
else:
    year = datetime.now().year

# After:
year = planting_date.year if planting_date else date.today().year

# Before (lines 162-165, 186-189):
death_dt: date | None = None
if death_date is not None:
    try:
        death_dt = datetime.strptime(death_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("death_date must be in YYYY-MM-DD format")

# After: Direct date comparison since death_date is already date object
if death_date is not None and planting_date is not None:
    if death_date < planting_date:
        raise ValueError("death_date cannot be before planting_date")
    if death_date > date.today():
        raise ValueError("death_date cannot be in the future")
```

#### 2. Domain Tests: `packages/plant_service/tests/unit/test_plant_model.py`
**Changes**: Add tests that verify date object behavior and remove/update string-specific tests.

```python
# Add tests like:
def test_planting_date_is_date_object():
    plant = Plant(variety_name="Test", latin_name="Test")
    assert isinstance(plant.planting_date, date)
    assert plant.planting_date == date.today()

def test_death_date_can_be_date_or_none():
    plant = Plant(variety_name="Test", latin_name="Test")
    assert plant.death_date is None
    
    death_date = date(2026, 8, 1)
    plant = Plant(
        variety_name="Test", 
        latin_name="Test", 
        planting_date=date(2026, 7, 1),
        death_date=death_date
    )
    assert plant.death_date == death_date
```

### Success Criteria:

#### Automated Verification:
- [x] Domain unit tests pass: `cd packages/plant_service && python -m pytest tests/unit/test_plant_model.py`
- [x] No `strptime`/`strftime("%Y-%m-%d")` remains for planting_date/death_date in domain model
- [x] Type checking passes: `cd packages/plant_service && mypy src/` (completed in Phase 2 — 38 source files, no issues)

#### Manual Verification:
- [x] Domain object creation works with date objects
- [x] Invalid date comparisons are caught (death before planting, future dates)
- [x] Default planting_date is today's date

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

## Phase 2: ORM Model Updates

### Overview
Update both ORM model trees to use Mapped[date] columns with Date() type.

### Changes Required:

#### 1. Service Tree ORM: `packages/plant_service/src/plant_service/adapters/repository/models/plant_model.py`
**Changes**:
- Change `planting_date` column from `Mapped[str] = mapped_column(String(10), nullable=False)` to `Mapped[date] = mapped_column(Date(), nullable=False)`
- Change `death_date` column from `Mapped[Optional[str]] = mapped_column(String(10), nullable=True)` to `Mapped[Optional[date]] = mapped_column(Date(), nullable=True)`
- Import `Date` from SQLAlchemy
- Update `to_domain()` method to pass date objects directly (no conversion needed)

```python
# Before (lines 30, 39):
planting_date: Mapped[str] = mapped_column(String(10), nullable=False)
death_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

# After:
from sqlalchemy import Date  # Add import

planting_date: Mapped[date] = mapped_column(Date(), nullable=False)
death_date: Mapped[Optional[date]] = mapped_column(Date(), nullable=True)

# Before (lines 65-72 in to_domain()):
planting_date=self.planting_date,
death_date=self.death_date,

# After: Same - no conversion needed since both are date objects
```

#### 2. Legacy CLI Tree ORM: `commands/models/plant.py`
**Changes**:
- Change `planting_date` column from `Mapped[str] = mapped_column(String(10), nullable=False)` to `Mapped[date] = mapped_column(Date(), nullable=False)`
- Change `death_date` column from `Mapped[Optional[str]] = mapped_column(String(10), nullable=True)` to `Mapped[Optional[date]] = mapped_column(Date(), nullable=True)`
- Import `Date` from SQLAlchemy
- Update `generate_id` and `_find_next_sequence` to work with date objects
- Update `create_from_dict` to handle date objects

```python
# Before (lines 34, 39):
planting_date: Mapped[str] = mapped_column(String(10), nullable=False)
death_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

# After:
from sqlalchemy import Date  # Add import

planting_date: Mapped[date] = mapped_column(Date(), nullable=False)
death_date: Mapped[Optional[date]] = mapped_column(Date(), nullable=True)

# Before (lines 62-65):
if planting_date:
    year = datetime.strptime(planting_date, "%Y-%m-%d").year
else:
    year = datetime.now(timezone.utc).year

# After:
year = planting_date.year if planting_date else datetime.now(timezone.utc).year

# Before (lines 111-115):
if "planting_date" in data:
    try:
        datetime.strptime(data["planting_date"], "%Y-%m-%d")
    except ValueError:
        raise ValueError("planting_date must be in YYYY-MM-DD format")

# After: Remove string validation - handled at API/CLI boundary
```

#### 3. Repository: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py`
**Changes**: Remove string validation for planting_date in `create_plant` method (lines 27-32)

```python
# Before (lines 27-32):
planting_date = plant_data.get("planting_date")
if planting_date is not None:
    try:
        datetime.datetime.strptime(planting_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("planting_date must be in YYYY-MM-DD format")

# After: Remove this validation block entirely
# Validation now happens at API/CLI boundary
```

### Success Criteria:

#### Automated Verification:
- [x] ORM unit tests pass: `cd packages/plant_service && python -m pytest tests/unit/test_plant_model.py` (plus full suite: 131 passed incl. SQLite integration tests)
- [x] No `strptime`/`strftime("%Y-%m-%d")` remains for planting_date/death_date in ORM models/repository
- [x] Type checking passes: `cd packages/plant_service && mypy src/`
- [x] Database migration generation works: `alembic revision --autogenerate` (verified in Phase 5 against live DB — zero diff for the plants table; remaining autogen diff is pre-existing media_attachments drift)

#### Manual Verification:
- [x] ORM models can be instantiated with date objects
- [x] to_domain()/from_domain() conversions work correctly
- [x] Repository create_plant works with date objects

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

## Phase 3: API Schema Update

### Overview
Update API request schema to use Pydantic date validation instead of relying on domain validation.

### Changes Required:

#### 1. API Schemas: `backend/fastapi/src/plant_tracking_api/schemas.py`
**Changes**:
- Change `PlantDeathRequest.death_date` from `str` to `date`
- Pydantic will automatically validate ISO format and convert to date object
- Response schemas already correct (`date | None`)

```python
# Before (line 8):
death_date: str

# After:
death_date: date
```

### Success Criteria:

#### Automated Verification:
- [x] API unit tests pass: `cd backend/fastapi && python -m pytest tests/test_plants.py` (32 passed, incl. 5 new date-type tests)
- [x] Malformed date in PlantDeathRequest returns 422 (Pydantic validation)
- [x] Valid date in PlantDeathRequest is accepted and converted to date object
- [x] Linting passes: `cd backend/fastapi && flake8` (project uses ruff: `ruff check backend/fastapi/src/` — all checks passed; mypy also improved, 5 pre-existing route errors resolved)

#### Manual Verification:
- [x] API endpoint `/plants/{id}/dead` rejects invalid dates with 422
- [x] API endpoint accepts valid dates and processes correctly
- [x] Wire format remains ISO-8601 strings in JSON

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

## Phase 4: CLI Update

### Overview
Update CLI to parse date inputs using `date.fromisoformat()` and display dates using `isoformat()`.

### Changes Required:

#### 1. CLI: `commands/plant_tracking_cli.py`
**Changes**:
- Update `_prompt_field` for planting_date to use `date.fromisoformat()` and store date object
- Update `_prompt_death_details` to use `date.fromisoformat()` for death_date
- Update display functions to use `.isoformat()` when showing dates
- Update plant creation flow to handle date objects
- Update mark-dead flow to handle date objects

```python
# Before (line 653 in create_plant):
_prompt_field("planting_date", "Planting date (YYYY-MM-DD)", plant_data)

# After: Need to modify _prompt_field or create specialized date prompt
# Option 1: Modify _prompt_field to accept a type parameter
# Option 2: Create _prompt_date_field function

# New function approach:
def _prompt_date_field(field, description, data):
    """Prompt user for a date field value with validation."""
    while True:
        value = input(f"{description}: ").strip()
        if value:
            try:
                data[field] = date.fromisoformat(value)
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("This field is required")

# Then in create_plant (line 653):
_prompt_date_field("planting_date", "Planting date (YYYY-MM-DD)", plant_data)

# Similar change in _prompt_death_details (around line 739):
# Before:
death_date = input("Death date (YYYY-MM-DD): ").strip()
try:
    d = datetime.strptime(death_date, "%Y-%m-%d")
    if d > datetime.now():
        print("Date cannot be in the future.")
        continue
    break

# After:
while True:
    death_date_str = input("Death date (YYYY-MM-DD): ").strip()
    if death_date_str:
        try:
            death_date = date.fromisoformat(death_date_str)
            if death_date > date.today():
                print("Date cannot be in the future.")
                continue
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    else:
        print("This field is required")

# Update display functions to use .isoformat()
# In list_plants function around line 1859-1869:
# Before:
planting_date = p.planting_date  # This was a string
print(f"{pid:<12} {variety:<25} {latin:<25} {planting_date:<15} {status:<10}")

# After:
planting_date_str = p.planting_date.isoformat() if p.planting_date else ""
print(f"{pid:<12} {variety:<25} {latin:<25} {planting_date_str:<15} {status:<10}")

# Similar updates in show_plant function around line 1901 and 1948-1950
```

### Success Criteria:

#### Automated Verification:
- [x] CLI unit tests pass (if any exist) — root suite: 81 passed
- [x] No `strptime`/`strftime("%Y-%m-%d")` remains for planting_date/death_date in CLI (only created_at/updated_at timestamps remain — out of scope)
- [x] Linting passes: `flake8 commands/` (project uses ruff/mypy: no new errors vs. baseline)

#### Manual Verification:
- [x] CLI prompts accept YYYY-MM-DD format and reject invalid formats
- [x] CLI displays dates in YYYY-MM-DD format
- [x] CLI create-plant works with date input
- [x] CLI mark-dead works with date input (prompts verified; DB write verified in Phase 5 after migration)
- [x] CLI list-plants shows dates correctly
- [x] CLI show-plant shows dates correctly

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

## Phase 5: Data Guard and Migration

### Overview
Create and run data guard verification to ensure existing data is valid, then create and apply database migrations.

### Changes Required:

#### 1. Data Guard Script
Create a script to verify all existing `planting_date` values are valid ISO dates:

```python
# scripts/verify_planting_dates.py
#!/usr/bin/env python3
"""Verify all existing planting_date values are valid ISO dates."""

from datetime import date
from plant_service.bootstrap import create_unit_of_work

def main():
    with create_unit_of_work() as uow:
        # Get all plants with planting_date
        plants = uow.plants.list_plants()
        
        invalid_dates = []
        for plant in plants:
            try:
                # This will fail if planting_date is not a valid date object
                # In the current state, we need to check the string format
                if isinstance(plant.planting_date, str):
                    date.fromisoformat(plant.planting_date)
                # If it's already a date object, it's valid
            except ValueError as e:
                invalid_dates.append((plant.id, plant.planting_date, str(e)))
        
        if invalid_dates:
            print("ERROR: Found invalid planting_date values:")
            for plant_id, date_val, error in invalid_dates:
                print(f"  Plant {plant_id}: '{date_val}' - {error}")
            return 1
        else:
            print(f"SUCCESS: All {len(plants)} planting_date values are valid ISO dates")
            return 0

if __name__ == "__main__":
    exit(main())
```

#### 2. Migration for planting_date column
Create a new migration to alter the planting_date column type:

```bash
# Generate migration
alembic revision -m "Convert planting_date to DATE"
```

Then edit the generated migration file:

```python
# In the generated migration file:
def upgrade() -> None:
    """Convert planting_date column to DATE type."""
    op.execute(
        "ALTER TABLE plants ALTER COLUMN planting_date TYPE DATE "
        "USING planting_date::date"
    )

def downgrade() -> None:
    """Revert planting_date column to STRING type."""
    op.execute(
        "ALTER TABLE plants ALTER COLUMN planting_date TYPE VARCHAR(10) "
        "USING planting_date::varchar"
    )
```

#### 3. Update death_date migration (in-place edit)
Verify that revision `a1b2c3d4e5f6` is truly unapplied everywhere, then edit it:

```python
# In alembic/versions/a1b2c3d4e5f6_add_death_fields_to_plant.py
# Change line 25 from:
sa.Column('death_date', sa.String(length=10), nullable=True)
# To:
sa.Column('death_date', sa.Date(), nullable=True)
```

### Success Criteria:

#### Automated Verification:
- [x] Data guard script passes: `python scripts/verify_planting_dates.py` (local DB: SUCCESS on valid data; correctly fails exit 1 on injected invalid rows — note: rewritten to use raw SQL instead of the ORM so it works against pre-death-revision databases like the cluster's current state)
- [x] Migration applies cleanly on fresh database: `alembic upgrade head` (fresh `plant_tracking_fresh` DB: all 4 revisions applied cleanly)
- [ ] Conversion migration succeeds against copy of cluster schema (cluster DB not reachable from this environment — no credentials; must run at deploy time)
- [x] `alembic upgrade head` creates planting_date and death_date as DATE columns (verified on fresh DB: both `date` in information_schema)
- [x] Downgrade migrations work correctly (step-down, full `downgrade base` + `upgrade head` cycle on fresh DB; step-down on data DB reverts planting_date to varchar)
- [x] Postgres columns show as DATE type in information_schema (verified on both local data DB and fresh DB)

#### Manual Verification:
- [ ] Data guard confirms no invalid existing planting_date values
- [ ] Migration applies without errors to development database
- [ ] Existing data is preserved and accessible after migration
- [ ] Can insert new plants with date values
- [ ] Can query plants using date comparisons (>=, <=, BETWEEN, etc.)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

## Phase 6: Backlog Update and Final Verification

### Overview
Update backlog documentation and run final comprehensive tests.

### Changes Required:

#### 1. Backlog Entry: `knowledge/backlog/death-date-and-planting-date-are-typed-as-str-none-or-str.md`
**Changes**: Update to record that this ticket is the resolution path:

```markdown
# Death date and planting date are typed as str | None or str

## Status
RESOLVED by PROJ-0014 - Use native date types end-to-end for planting_date and death_date

## Resolution Summary
Changed planting_date and death_date from string representations to native date types:
- DATABASE: VARCHAR(10) → DATE columns
- ORM: Mapped[String] → Mapped[date] with Date() type
- DOMAIN: str/str | None → date/date | None objects
- API: Already correct in responses, fixed in requests (Pydantic validation)
- CLI: String input/output → date.fromisoformat()/isoformat()
- All strptime/strftime usage removed for these fields
```

### Success Criteria:

#### Automated Verification:
- [x] All unit tests pass: `make test` (or equivalent) — root 81 + plant_service 131 (incl. integration) + fastapi 32 = 244 passed
- [x] All integration tests pass: `make test-integration` (or equivalent) — plant_service SQLite integration suite in the 131 above
- [x] Type checking passes: `mypy .` or equivalent — plant_service clean (38 files); commands/ 12 pre-existing (unchanged vs. baseline); fastapi improved 12 → 7 pre-existing
- [x] Linting passes: `flake8 .` or equivalent — project uses ruff: no new errors vs. baseline in any tree; all newly added files clean
- [x] No `strptime`/`strftime("%Y-%m-%d")` remains for planting_date/death_date anywhere in codebase — except `commands/plant_model.py` (Markdown *file* model, a string-based format the plan does not list for change; it parses ISO strings it owns) and `created_at` display headers in Markdown models (out-of-scope timestamp fields)

#### Manual Verification:
- [ ] CLI end-to-end tests pass (add plant with planting date, mark dead, list display)
- [ ] API integration tests pass with unchanged wire format
- [ ] Manual testing confirms:
  - CLI: add plant with planting date, mark dead, list — all display ISO dates
  - API: PATCH /plants/{id}/dead with "2026-13-99" → 422; with valid date → success
  - Date comparisons work correctly in domain (death >= planting, death <= today)
  - Default planting_date is today's date
  - Wire format remains ISO-8601 strings in JSON

## Testing Strategy

### Unit Tests:
- Domain model tests for date object behavior and validation
- ORM model tests for proper mapping and conversion
- Repository tests for correct handling of date objects
- API tests for Pydantic validation of date inputs
- CLI tests for date parsing and formatting

### Integration Tests:
- Full plant creation workflow via CLI
- Plant death marking workflow via CLI and API
- Plant listing and display workflows
- Database persistence and retrieval of date values
- Cross-layer data flow validation

### Manual Testing Steps:
1. Verify data guard passes on existing data
2. Create plant via CLI with valid planting date
3. Verify plant appears in list with correct date
4. Mark plant as dead via CLI with valid death date
5. Verify plant shows as dead with correct death date
6. Attempt to mark plant as dead with invalid date → should get clear error
7. Attempt to create plant with invalid planting date → should get clear error
8. Test API endpoint for marking plant as dead with valid/invalid dates
9. Verify date comparisons work (cannot die before planting, cannot die in future)
10. Verify default planting_date is today's date
11. Check that wire format remains ISO-8601 strings in API responses
12. Verify listing shows dates in YYYY-MM-DD format

## Performance Considerations

- Positive: Eliminates repeated `strptime` parsing, improving performance
- Neutral: Date objects have similar memory footprint to strings for dates
- Positive: Enables proper DATE indexing and query optimization in PostgreSQL
- Neutral: No change to API wire format or throughput

## Migration Notes

1. **Data Guard**: Must run before applying migrations to catch invalid data
2. **Atomic ORM Update**: Both ORM model trees must be updated in same deployment
3. **Migration Order**: 
   - Verify data guard passes
   - Apply planting_date migration (ALTER TYPE)
   - Verify death_date migration can be safely edited in-place
4. **Rollback**: 
   - Downgrade migrations available for both columns
   - Data remains as strings during downgrade (safe conversion)
5. **Deployment**: All layers must be updated together to avoid interface mismatches

## References

- Original ticket: `knowledge/tickets/PROJ-0014.md`
- Related ticket: PROJ-0013 (added the death fields as strings)
- Domain model: `packages/plant_service/src/plant_service/domain/plant.py`
- ORM (service): `packages/plant_service/src/plant_service/adapters/repository/models/plant_model.py`
- ORM (legacy CLI): `commands/models/plant.py`
- Repository: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py`
- API schemas: `backend/fastapi/src/plant_tracking_api/schemas.py`
- CLI: `commands/plant_tracking_cli.py`
- Migration (death): `alembic/versions/a1b2c3d4e5f6_add_death_fields_to_plant.py`
- Backlog entry: `knowledge/backlog/death-date-and-planting-date-are-typed-as-str-none-or-str.md`