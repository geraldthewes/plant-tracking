# Mark plant as dead Implementation Plan

## Overview

This implementation adds the ability to mark a plant as dead by recording the date of death and reason, while keeping the record in the system for future analysis. The feature includes adding `death_date`, `death_reason`, and `death_comment` fields to the plant record, implementing CLI and API commands to mark plants as dead, and enabling filtering of plant listings by alive/dead status.

## Current State Analysis

Currently, the plant tracking system supports basic CRUD operations for plants but lacks functionality to track plant mortality. The system follows a port/adapter (hexagonal) architecture with:
- Domain model in `packages/plant_service/src/plant_service/domain/plant.py`
- ORM model in `packages/plant_service/src/plant_service/adapters/repository/models/plant_model.py`
- Service layer interface (Protocol) in `packages/plant_service/src/plant_service/service_layer/plant_service.py`
- Repository implementation in `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py`
- CLI commands in `commands/plant_tracking_cli.py`
- API routes in `backend/fastapi/src/plant_tracking_api/routes/plants.py` (currently only has `/care-needed` endpoint)
- Frontend API client in `frontend/src/api/plantTrackingAPI.ts`

The existing Alembic migration pattern creates tables with appropriate constraints, as seen in `alembic/versions/72fff22905dd_initial_migration.py`.

## Desired End State

After implementation, users will be able to:
1. Mark a plant as dead via CLI with date, reason, and optional comment
2. Mark a plant as dead via API endpoint
3. Filter plant listings to show only alive or dead plants
4. View death date and reason when displaying plant details
5. Maintain dead plant records in the database for historical analysis

### Key Discoveries:
- The plant domain model uses `@dataclass(frozen=False)` allowing modification after creation
- ID generation follows `VARIETY-YYYY-SEQ` format handled in domain layer
- Service layer uses Protocol/interface pattern with Unit of Work for transactions
- CLI implements three-tier fallback: service package → legacy ORM → Markdown files
- API currently lacks plant CRUD endpoints (only `/care-needed` exists)
- Alembic migrations follow standard pattern with `op.create_table()` and column definitions

## What We're NOT Doing

- Bulk operations for marking multiple plants as dead
- Graveyard visualization or special UI for dead plants
- Mortality statistics/dashboards
- Archival to cold storage or deletion of dead plant records
- Notifications when plants are marked as dead
- Automatic detection of plant death based on sensor data

## Implementation Approach

We will implement this feature by following the existing patterns in the codebase:
1. Add new fields to the domain model (`Plant` class)
2. Add corresponding columns to the ORM model (`PlantModel` class)
3. Create Alembic migration to add columns to the `plants` table
4. Update the service layer to handle the new fields
5. Implement CLI command for marking plants as dead
6. Implement API endpoint for marking plants as dead
7. Update plant listing functionality to filter by alive/dead status
8. Ensure proper validation (e.g., "Other" reason requires comment)
9. Update frontend API client to handle new fields
10. Add unit tests for all new functionality

The implementation will be done in phases to ensure each layer works correctly before moving to the next.

## Phase 1: Domain and Database Changes

### Overview
This phase adds the death tracking fields to the domain model and ORM model, creates the database migration, and ensures the core data structures support the new functionality.

### Changes Required:

#### 1. Domain Model
**File**: `packages/plant_service/src/plant_service/domain/plant.py`
**Changes**: Add `death_date`, `death_reason`, and `death_comment` fields with appropriate validation

```python
@dataclass(frozen=False)
class Plant:
    # ... existing fields ...
    
    # New fields for death tracking
    death_date: str = ""  # YYYY-MM-DD format, empty if alive
    death_reason: str = ""  # From predefined list or "Other"
    death_comment: str = ""  # Optional comment, required if reason is "Other"
    
    # Add validation in create_from_dict method
```

#### 2. ORM Model
**File**: `packages/plant_service/src/plant_service/adapters/repository/models/plant_model.py`
**Changes**: Add columns for the new fields to the Plant table

```python
class Plant(Base, TimestampMixin):
    # ... existing columns ...
    
    # New columns for death tracking
    death_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    death_reason: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    death_comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Update to_domain method to include new fields
```

#### 3. Alembic Migration
**File**: `alembic/versions/<new_revision_id>_add_death_fields_to_plant.py`
**Changes**: Add columns to the plants table

```python
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plants', sa.Column('death_date', sa.String(length=10), nullable=True))
    op.add_column('plants', sa.Column('death_reason', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('death_comment', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plants', 'death_comment')
    op.drop_column('plants', 'death_reason')
    op.drop_column('plants', 'death_date')
    # ### end Alembic commands ###
```

### Success Criteria:

#### Automated Verification:
- [x] Alembic migration runs successfully: `alembic upgrade head`
- [x] Domain model accepts new fields: `python -c "from plant_service.domain import Plant; p = Plant(death_date='2026-08-07')" `
- [x] ORM model includes new columns: Check `PlantModel.__table__.columns`
- [x] Unit tests pass: `python -m pytest packages/plant_service/tests/unit/test_plant_model.py`
- [x] Type checking passes: `mypy packages/plant_service/src/plant_service/domain/plant.py`
- [x] Linting passes: `ruff check packages/plant_service/src/plant_service/domain/plant.py`

#### Manual Verification:
- [ ] New fields appear in Plant domain object when instantiated
- [ ] Database schema shows new columns in plants table
- [ ] Migration can be rolled back and applied repeatedly

---

## Phase 2: Service Layer and Repository Updates

### Overview
This phase updates the service layer and repository to handle the new death tracking fields, ensuring they are properly persisted and retrieved.

### Changes Required:

#### 1. Plant Repository
**File**: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py`
**Changes**: 
- Update `create_plant()` method to map new fields from domain to ORM object
- Update `update_plant()` method to handle new fields
- Ensure `to_domain()` method in ORM model includes new fields (already covered in Phase 1)

#### 2. Service Layer Implementation
**File**: `packages/plant_service/src/plant_service/service_layer/plant_service.py`
**Changes**: No changes needed to the Protocol interface, but the repository implementation (which implements the Protocol) will handle the new fields

### Success Criteria:

#### Automated Verification:
- [x] Repository correctly maps death fields between domain and ORM objects
- [x] Creating a plant with death fields persists to database
- [x] Retrieving a plant returns correct death field values
- [x] Updating a plant's death fields works correctly
- [x] Unit tests for repository and service layer pass
- [x] Existing tests continue to pass

#### Manual Verification:
- [ ] Plant record with death fields can be created and retrieved correctly
- [ ] Death fields update properly when modified
- [ ] No regression in existing plant CRUD operations

---

## Phase 3: CLI Implementation

### Overview
This phase implements the CLI command to mark a plant as dead, following the existing CLI patterns for plant operations.

### Changes Required:

#### 1. CLI Command
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add new subcommand `mark-dead` with interactive prompts for date, reason, and comment

```python
def mark_dead(args, db=None, database_dir=None, packets_dir=None, genera_dir=None):
    """Mark a plant as dead with date, reason, and optional comment."""
    # Implementation similar to create_plant but for updating existing plant
    # Prompt for plant ID lookup
    # Prompt for death date (YYYY-MM-DD)
    # Prompt for death reason from predefined list
    # If reason is "Other", prompt for required comment
    # Call uow.plants.update_plant(plant_id, update_data)
```

### Success Criteria:

#### Automated Verification:
- [x] CLI command `plant-tracking mark-dead --help` shows correct usage
- [x] Unit tests for mark-dead command pass
- [x] Existing CLI tests continue to pass

#### Manual Verification:
- [ ] CLI command prompts for plant ID, death date, reason, and comment
- [ ] "Other" reason requires comment input
- [ ] Invalid date format shows error
- [ ] Plant is correctly marked as dead in database
- [ ] Error handling for non-existent plant ID works

---

## Phase 4: API Implementation

### Overview
This phase implements the API endpoint to mark a plant as dead, adding the missing plant CRUD endpoints to the FastAPI backend.

### Changes Required:

#### 1. API Routes
**File**: `backend/fastapi/src/plant_tracking_api/routes/plants.py`
**Changes**: 
- Add PATCH endpoint `/plants/{plant_id}/dead` to mark plant as dead
- Add GET endpoint `/plants/` to list plants with filtering capability
- Add GET endpoint `/plants/{plant_id}` to get specific plant details

#### 2. API Dependencies
**File**: `backend/fastapi/src/plant_tracking_api/dependencies.py`
**Changes**: No changes needed (already provides UoW dependency)

### Success Criteria:

#### Automated Verification:
- [x] API endpoint `/plants/{plant_id}/dead` accepts PATCH request with death data
- [x] API endpoint `/plants/` returns list of plants
- [x] API endpoint `/plants/{plant_id}` returns single plant details
- [x] API tests for new endpoints pass
- [x] Existing API tests continue to pass
- [x] OpenAPI spec is updated correctly

#### Manual Verification:
- [ ] PATCH to `/plants/{plant_id}/dead` with valid data marks plant as dead
- [ ] GET to `/plants/` returns plants with death fields when applicable
- [ ] GET to `/plants/{plant_id}` returns correct death field values
- [ ] Error handling for invalid plant ID or validation errors works
- [ ] Frontend API client can successfully call new endpoints

---

## Phase 5: Frontend Integration and Listing Filter

### Overview
This phase updates the frontend API client to handle the new death fields and implements filtering of plant listings by alive/dead status.

### Changes Required:

#### 1. Frontend API Client
**File**: `frontend/src/api/plantTrackingAPI.ts`
**Changes**: 
- Update generated client to include new fields in plant data structures
- Add methods for marking plant as dead if not auto-generated
- Update existing methods to handle new fields

#### 2. Plant Listing Enhancement
**Note**: Since the frontend currently only contains the API client and no UI components, 
filtering would need to be implemented in any future UI that uses this client.
For now, we'll ensure the API supports filtering.

#### 3. API Filtering Support
**File**: `backend/fastapi/src/plant_tracking_api/routes/plants.py`
**Changes**: 
- Modify GET `/plants/` endpoint to accept query parameters for filtering:
  - `alive_only`: boolean to show only living plants
  - `dead_only`: boolean to show only dead plants

### Success Criteria:

#### Automated Verification:
- [x] Frontend API client compiles without errors
- [x] New fields are properly typed in TypeScript interfaces
- [x] API filtering parameters work correctly
- [x] Unit tests for frontend updates pass
- [x] Existing frontend tests continue to pass

#### Manual Verification:
- [ ] Plant data retrieved via API includes death fields when applicable
- [ ] Filtering by alive/dead status works via API query parameters
- [ ] No errors when accessing new fields from TypeScript client

---

## Phase 6: Testing and Validation

### Overview
This phase adds comprehensive tests for the new functionality and validates that all success criteria are met.

### Changes Required:

#### 1. Unit Tests
**File**: `packages/plant_service/tests/unit/test_plant_model.py`
**Changes**: Add tests for death field validation and model behavior

#### 2. Integration Tests
**File**: `packages/plant_service/tests/integration/test_repository.py`
**Changes**: Add tests for creating/retrieving/updating plants with death fields

#### 3. CLI Tests
**File**: `tests/test_plant_tracking.py`
**Changes**: Add tests for mark-dead CLI command

#### 4. API Tests
**File**: `backend/fastapi/tests/test_plants.py`
**Changes**: Add tests for new API endpoints

### Success Criteria:

#### Automated Verification:
- [x] All unit tests pass: `python -m pytest packages/plant_service/tests/unit/`
- [x] All integration tests pass: `python -m pytest packages/plant_service/tests/integration/`
- [x] All CLI tests pass: `python -m pytest tests/`
- [x] All API tests pass: `python -m pytest backend/fastapi/tests/`
- [x] Full test suite passes: `python -m pytest`
- [x] Linting passes across entire project: `ruff check .`
- [x] Type checking passes (where applicable): `mypy packages/plant_service/src/`

#### Manual Verification:
- [ ] End-to-end workflow: Mark plant dead via CLI → Verify via API → List shows correct status
- [ ] End-to-end workflow: Mark plant dead via API → Verify via CLI → List shows correct status
- [ ] "Other" reason requires comment in both CLI and API
- [ ] Invalid inputs are properly rejected
- [ ] Dead plants remain in database and can be queried historically
- [ ] Existing functionality remains unaffected

## Testing Strategy

### Unit Tests:
- Test Plant domain model validation for death fields
- Test ORM model mapping of death fields
- Test repository methods for death field persistence
- Test service layer handling of death fields
- Test CLI command parsing and validation
- Test API endpoint request/response handling

### Integration Tests:
- Test complete flow: create plant → mark dead → retrieve → verify death fields
- Test filtering of plant listings by alive/dead status
- Test edge cases: "Other" reason with/without comment
- Test death field updates and clearing

### Manual Testing Steps:
1. Create a new plant using existing CLI
2. Mark the plant as dead using CLI with valid date and reason
3. Verify plant appears in dead-only listing
4. Verify plant does not appear in alive-only listing
5. Check that death date and reason are correctly stored
6. Test marking plant dead with "Other" reason and verify comment is required
7. Test API endpoints for marking plant dead and retrieving plant info
8. Verify existing plant CRUD operations still work correctly
9. Test database migration upgrade and downgrade processes

## Performance Considerations

- Adding three nullable columns to the plants table has minimal performance impact
- No additional indexes are needed for the basic filtering use case
- Queries filtering by death fields will benefit from standard table scans
- No changes to existing query patterns or performance characteristics
- The implementation follows existing patterns so performance should remain consistent

## Migration Notes

- The Alembic migration will add three nullable columns to the existing plants table
- Existing plant records will have NULL values for death fields (indicating alive plants)
- No data migration is needed as NULL values correctly represent alive plants
- Rollback of migration will simply drop the columns, removing death tracking capability
- Backward compatibility is maintained as existing code will ignore new NULL fields

## Documentation Updates

To ensure all project documentation remains in sync, the following records should be updated during implementation:

- **Architecture Records**: Update `ARCHITECTURE.md` (if exists) to document the new death tracking fields and their relationship to the plant entity
- **PRD Update**: Update the Product Requirements Document to reflect the completed feature
- **API Documentation**: Update any API specification documents to reflect the new endpoints
- **Database Schema Documentation**: Document the new columns in the plants table
- **CLI Command Reference**: Add documentation for the new `mark-dead` command
- **User Guide**: Update any user-facing documentation to include the new functionality

## Git Workflow

To maintain proper version control and traceability:
- All implementation work should be carried out on a git branch named after the ticket: `PROJ-0013`
- The branch should be created from the latest main branch
- Regular commits should be made with descriptive messages
- Before creating a pull request, ensure the branch is up-to-date with main
- The pull request should reference the ticket ID (PROJ-0013) in the title or description

## Documentation Updates

To ensure all project documentation remains in sync, the following records should be updated during implementation:

- **Architecture Records**: Update `ARCHITECTURE.md` (if exists) to document the new death tracking fields and their relationship to the plant entity
- **PRD Update**: Update the Product Requirements Document to reflect the completed feature
- **API Documentation**: Update any API specification documents to reflect the new endpoints
- **Database Schema Documentation**: Document the new columns in the plants table
- **CLI Command Reference**: Add documentation for the new `mark-dead` command
- **User Guide**: Update any user-facing documentation to include the new functionality

## References

- Original ticket: `knowledge/tickets/PROJ-0013.md`
- Plant domain model: `packages/plant_service/src/plant_service/domain/plant.py:13-106`
- Plant ORM model: `packages/plant_service/src/plant_service/adapters/repository/models/plant_model.py:15-64`
- Alembic initial migration: `alembic/versions/72fff22905dd_initial_migration.py`
- CLI create-plant command: `commands/plant_tracking_cli.py:361-711`
- Plant service interface: `packages/plant_service/src/plant_service/service_layer/plant_service.py:10-35`
- Plant repository: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py:15-101`