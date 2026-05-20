---
date: 2026-05-20T22:30:00Z
researcher: Gerald
git_commit: 57e5a29739262b967b4ab8909c1e69409e222b55
branch: main
repository: plant-tracking
topic: "Create python service package"
tags: [research, codebase, python-service, ports-adapters, architecture]
status: complete
last_updated: 2026-05-20
last_updated_by: Gerald
---

# Research: Create python service package

**Date**: 2026-05-20T22:30:00Z  
**Researcher**: Gerald  
**Git Commit**: 57e5a29739262b967b4ab8909c1e69409e222b55  
**Branch**: main  
**Repository**: plant-tracking  

## Research Question
Research all information necessary to implement the ticket PROJ-0008: Create python service package. This involves analyzing the existing codebase, determining what logic can be extracted, researching best practices from software-backend-wiki, and defining the appropriate structure for a Ports & Adapters Python package.

## Summary
The current plant tracking CLI is a monolithic ~1422 line file (`commands/plant_tracking_cli.py`) that mixes business logic with presentation logic and makes direct database calls. To create a proper service package, we need to extract:
1. Domain models (pure Python classes with no infrastructure imports)
2. Service layer (use-case functions that orchestrate business logic)
3. Repository adapter layer (SQLAlchemy 2.0 implementations)
4. Unit of Work pattern for transaction management
5. Label generation and export capabilities (with iterator/streaming pattern)

The service package should follow Ports & Adapters architecture where dependency arrows point inward (adapters import domain, domain never imports adapters), and be structured as an installable package with its own `pyproject.toml`.

## Detailed Findings

### Current Code Organization and Extractable Logic

#### Entrypoint Logic (to remain in commands/)
- CLI argument parsing and user interaction (`argparse` based)
- User prompting and input validation functions
- Markdown backup functionality (for transition period)
- Console output formatting and user feedback

#### Business Logic (to extract to service package)

**Domain Models** (from `commands/models/`):
- `Plant` model with ID generation logic (VARIETY-YYYY-SEQ format)
- `Genus` model with ID generation (GENUS-NNN format) 
- `SeedPacket` model with ID generation (SPKT-NNN format)
- All models include validation logic in `create_from_dict` methods
- Relationships properly defined with foreign keys
- Timestamp mixin for created/updated fields

**Service Layer Functions** (currently embedded in CLI):
- Plant creation with genus lookup/fuzzy matching
- Seed packet creation and matching
- Genus creation
- Label generation logic (in `label_generator.py`, `label_format.py`)
- Printer interface (in `printer.py`)
- Plant logging functions (humidity, water, fertilizer, note)
- Log listing and filtering

**Repository/Adapter Logic** (currently in models and database.py):
- SQLAlchemy model definitions with relationships
- ID generation sequences (queries to find next sequence number)
- Database connection and session management (`database.py`)
- Basic CRUD operations embedded in model methods

**Export Capability** (in `database.py:export_to_markdown()`):
- Current implementation loads all records into memory
- Exports to Markdown files organized by type
- Needs to be refactored to use iterator/streaming pattern

### SQLAlchemy Model Structure Analysis

The current models in `commands/models/` follow good practices:
- Proper inheritance from `Base` and `TimestampMixin`
- Clear table definitions with `__tablename__`
- Appropriate column types and constraints
- Foreign key relationships with `ForeignKey`
- Relationship definitions with proper lazy loading
- ID generation preserves existing formats:
  - Plant: VARIETY-YYYY-SEQ (e.g., YH-2026-001)
  - Genus: GENUS-NNN (e.g., GENUS-001)
  - SeedPacket: SPKT-NNN (e.g., SPKT-001)
- Validation in `create_from_dict` classmethods
- No business logic leakage into model methods (mostly data access)

### Alembic Migration Integration

The existing Alembic setup is properly configured:
- Migrations located in `/alembic/versions/`
- `env.py` correctly points to `commands.models.base.Base` as target metadata
- Database URL sourced from `DATABASE_URL` environment variable
- Supports both offline and online migration modes
- The service package should reference these migrations by:
  1. Keeping the `alembic/` directory in the project root
  2. Ensuring the service package's models have the same metadata
  3. Configuring Alembic to scan the service package's model modules
  4. Maintaining the same `DATABASE_URL` environment variable dependency

### Ports & Adapters Package Structure

Based on software-backend-wiki research and the C2 container diagram, the appropriate structure is:

```
packages/
  plant_service/
    src/
      plant_service/
        domain/                    # Pure Python; no infrastructure imports
          plant.py                 # Plant entity with validation
          genus.py                 # Genus entity
          seed_packet.py           # Seed packet entity
          plant_log.py             # Plant log entry
          exceptions.py            # Domain-specific exceptions
          __init__.py
        service_layer/             # Use-case orchestration
          plant_service.py         # Plant-related use cases
          genus_service.py         # Genus-related use cases  
          seed_packet_service.py   # Seed packet use cases
          log_service.py           # Logging use cases
          export_service.py        # Export/use-case functions
          unit_of_work.py          # AbstractUnitOfWork protocol + SQLAlchemy impl
          message_bus.py           # For event-driven architecture (future)
          __init__.py
        adapters/                  # Infrastructure implementations
          repository/
            plant_repository.py    # SQLAlchemy implementation of plant port
            genus_repository.py    # SQLAlchemy implementation of genus port
            seed_packet_repository.py  # SQLAlchemy implementation of seed packet port
            log_repository.py      # SQLAlchemy implementation of log port
          orm.py                   # Classical ORM mapping if needed
          __init__.py
        entrypoints/               # Will remain in commands/ for now
          # CLI entrypoint will be refactored to call service layer
          # FastAPI entrypoint will be created separately
        config.py                  # Configuration loading
        bootstrap.py               # Composition root - wires everything
        __init__.py
    tests/
      unit/                        # Domain-only tests; no DB
        test_plant_model.py
        test_plant_service.py
        # ... etc
      integration/                 # Repository + UoW tests against real DB
        test_plant_repository.py
        test_export_service.py
        # ... etc
      # e2e/ would be for full stack via HTTP (future)
    pyproject.toml                 # Package configuration
    README.md
    .env.template                  # For local development
```

### Iterator/Export Pattern Design for Streaming

To satisfy the requirement that "Export returns iterator, not full in-memory collection":

1. **Current Problem**: `export_to_markdown()` in `database.py` uses `.all()` which loads entire result sets into memory
2. **Solution**: Use SQLAlchemy's yield_per() or server-side cursors for streaming
3. **Implementation Approach**:
   - Create export functions in service layer that return generators/iterators
   - Use `session.query(Model).yield_per(batch_size)` for streaming database results
   - Process and yield records one batch at a time instead of collecting all
   - For file exports, write to temporary files in batches rather than accumulating in memory

Example pattern:
```python
def export_plants_streaming(session, batch_size=100):
    """Stream plant records in batches to avoid memory overload"""
    query = session.query(Plant)
    
    for plant in query.yield_per(batch_size):
        # Convert to export format and yield
        yield {
            "id": plant.id,
            "variety_name": plant.variety_name,
            "latin_name": plant.latin_name,
            # ... other fields
        }
```

### Testing Infrastructure Recommendations

From software-backend-wiki:
- **pytest** as the test runner with rich plugin ecosystem
- Tests split by type:
  - `unit/` - Domain-only tests; no database required (fast)
  - `integration/` - Repository + Unit of Work tests against real database
  - `e2e/` - Full stack via HTTP (for future FastAPI implementation)
- Testing approach:
  - Unit tests use fake/mock repositories (no database)
  - Integration tests use real PostgreSQL database
  - Follow the `src/myapp/` test tree structure mirroring source
- Additional tools:
  - `ruff` for linting and formatting
  - `mypy` for static type checking with `--strict`
  - `bandit` for security vulnerability scanning
  - `pip-audit` for dependency vulnerability checking

### Error Handling Structure

From software-backend-wiki and existing code analysis:
- **Exception Hierarchy**: Domain-specific exceptions that map to HTTP status codes
- **Base Exception**: `PlantTrackingServiceException`
- **Specific Exceptions**:
  - `ValidationException` → HTTP 400
  - `PlantNotFoundException` → HTTP 404  
  - `SeedPacketNotFoundException` → HTTP 404
  - `GenusNotFoundException` → HTTP 404
  - `DatabaseUnavailableError` → HTTP 503
  - `ExportError` → HTTP 500
- **Error Mapping Layer**: In entrypoints (CLI/FastAPI) that converts service exceptions to appropriate user responses
- **CLI Mapping**: Service exceptions → stderr messages + appropriate exit codes
- **FastAPI Mapping**: Service exceptions → HTTPException with proper status codes

### Linting/Type-Checking Toolchain

From software-backend-wiki:
- **ruff** - Fast linter and formatter; replaces flake8 + isort + pyupgrade
- **mypy** - Static type checker; run with `--strict` in CI
- **Additional Tools**:
  - `bandit` - Security vulnerability scanner
  - `pip-audit` - Dependency vulnerability scanning (pre-push checklist)
- **Configuration**: 
  - `ruff` configuration in `pyproject.toml` or `.ruff.toml`
  - `mypy` configuration in `pyproject.toml` or `mypy.ini`
  - Pre-commit hooks for automated checking

## Code References

- `/home/gerald/repos/plant-tracking/commands/plant_tracking_cli.py:1-1422` - Monolithic CLI containing mixed business and presentation logic
- `/home/gerald/repos/plant-tracking/commands/models/plant.py:16-124` - SQLAlchemy Plant model with ID generation and validation
- `/home/gerald/repos/plant-tracking/commands/models/genus.py:14-122` - SQLAlchemy Genus model  
- `/home/gerald/repos/plant-tracking/commands/models/seed_packet.py:14-115` - SQLAlchemy SeedPacket model
- `/home/gerald/repos/plant-tracking/commands/database.py:70-185` - Current export function loading full datasets
- `/home/gerald/repos/plant-tracking/commands/database.py:47-58` - Database session management
- `/home/gerald/repos/plant-tracking/knowledge/architecture/backend/c2-container.md` - Ports & Adapters architecture definition
- `/home/gerald/repos/plant-tracking/alembic/env.py` - Alembic configuration referencing current models

## Architecture Insights

1. **Clean Separation Achievable**: The current code shows good separation concerns with models already defined properly, making extraction feasible.

2. **Dependency Direction**: Current models import from `commands.database` which violates Ports & Adapters (domain should not import infrastructure). The service package needs to invert this dependency.

3. **ID Generation Logic**: The application-generated ID formats (VARIETY-YYYY-SEQ, GENUS-NNN, SPKT-NNN) are business rules that belong in the domain layer.

4. **Validation Centralization**: Validation logic in `create_from_dict` methods should remain in domain models as pure validation.

5. **Export Streaming Necessity**: Current export implementation violates the architectural requirement to avoid loading full datasets across API boundaries.

6. **Entry Point Refactoring**: CLI entrypoint will become a thin shell that parses arguments and calls service functions, preserving user experience while removing business logic.

## Historical Context (from knowledge/)

- `knowledge/architecture/backend/c2-container.md` - Defines the target Ports & Adapters architecture with clear layer responsibilities
- `knowledge/architecture/decisions/ADR-0005-backend-technology-stack.md` - Confirms Python 3.9+, SQLAlchemy 2.0, PostgreSQL stack
- `knowledge/architecture/decisions/ADR-0008-architecture-refinement-ports-and-adapters.md** - Mandates Ports & Adopters pattern adherence
- Existing successful implementations of similar patterns in other services in the cluster

## Related Research

No existing research documents found in `knowledge/research/` for this specific topic.

## Open Questions

1. **Migration Strategy**: Should we refactor the CLI to consume the service package incrementally or via big-bang replacement?
2. **Backward Compatibility**: How to handle existing Markdown-based backup during transition period?
3. **Configuration Management**: Should the service package have its own configuration or reuse existing environment variables?
4. **Testing Database**: Should integration tests use a temporary PostgreSQL database or the existing development database?
5. **Eventual Consistency**: Should we implement domain events and message bus now or defer to later iteration?
6. **Packaging Details**: Should we use hatchling, poetry, or standard setuptools for the package build system?

## Next Steps for Implementation

1. Create the `packages/plant_service/` directory structure
2. Implement domain models in `src/plant_service/domain/` 
3. Create service layer interfaces and implementations
4. Build repository adapters using SQLAlchemy 2.0
5. Implement Unit of Work pattern
6. Create export functions with iterator/streaming pattern
7. Configure `pyproject.toml` with proper dependencies
8. Set up testing infrastructure (pytest, fixtures)
9. Configure linting/type-checking toolchain (ruff, mypy)
10. Refactor CLI to consume service package as thin entrypoint
11. Verify Alembic migrations work with new package structure