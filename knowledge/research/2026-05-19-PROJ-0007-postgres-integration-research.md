---
date: 2026-05-19T22:30:00Z
researcher: opencode
git_commit: dfed235 feat: add PROJ-0007 ticket for Postgres migration
branch: main
repository: plant-tracking
topic: "Migrate from Markdown file storage to PostgreSQL"
tags: [research, codebase, postgresql, sqlalchemy, migration, cli, architecture]
status: complete
last_updated: 2026-05-19
last_updated_by: opencode
---

# Research: Migrate from Markdown file storage to PostgreSQL

**Date**: 2026-05-19T22:30:00Z  
**Researcher**: opencode  
**Git Commit**: dfed235 feat: add PROJ-0007 ticket for Postgres migration  
**Branch**: main  
**Repository**: plant-tracking  

## Research Question
How to best integrate the PostgreSQL migration feature for the plant tracking system after reviewing the PRD (@_bmad-output/prd.md), architecture (@knowledge/architecture/), and best practices at https://github.com/geraldthewes/software-backend-wiki?

## Summary
The migration from Markdown file storage to PostgreSQL should follow a phased approach using SQLAlchemy ORM with proper connection pooling for CLI context. The existing data model and relationships must be preserved while implementing Alembic for schema migrations. Key considerations include maintaining the current ID generation patterns (VARIETY-YYYY-SEQ, SPKT-NNN, GENUS-NNN), handling the consolidated log file appropriately, and ensuring zero data loss during migration.

## Detailed Findings

### Component/Area 1: Existing Data Model Analysis
- **Plant Model** (`commands/plant_model.py`): Stores core plant data with ID format VARIETY-YYYY-SEQ, references to SeedPacket and Genus, and record-keeping fields
- **SeedPacket Model** (`commands/seed_packet_model.py`): Stores seed packet metadata with ID format SPKT-NNN, used for deduplication by variety_name+latin_name
- **Genus Model** (`commands/genus_model.py`): Stores genus taxonomy with ID format GENUS-NNN, used for auto-resolving latin_name
- **PlantLog Model** (`commands/plant_log_model.py`): Consolidated activity log in single file `database/logs/plant-activity-log.md` with YAML-delimited entries

### Component/Area 2: Architecture Analysis
- **Database Container** (`knowledge/architecture/database/c2-container.md`): Specifies PostgreSQL 15 as primary data store with connection pooling (min=2, max=20), migration safeguards, and ACID compliance
- **Architecture Decisions** (`knowledge/architecture/architecture-decisions.md`): Sprint 5 ADRs confirm PostgreSQL 15 with connection pooling and migration tooling (Flyway-style mentioned)
- **Data Persistence Strategy**: Phased approach from markdown to PostgreSQL with clear migration path (ADR-0006)

### Component/Area 3: CLI-Specific SQLAlchemy Best Practices
From technical research on software-backend-wiki patterns and codebase analysis:

1. **ORM Selection**: SQLAlchemy 2.0 DeclarativeBase with Mapped generics for type safety
2. **Connection Pooling**: SingletonThreadPool (one connection per CLI process, auto-closed on exit) 
3. **Session Management**: Per-command Session context manager (`with Session(engine) as session:`)
4. **Relationship Loading**: lazy="selectin" default to avoid N+1 queries and detached instance errors
5. **ID Preservation**: Keep application-generated IDs (VARIETY-YYYY-SEQ, etc.) as string primary keys
6. **Log Entry Handling**: Sparse columns pattern for polymorphic PlantLogEntry fields

### Component/Area 4: Migration Strategy
1. **Schema Generation**: Use Alembic `--autogenerate` from SQLAlchemy models
2. **Data Migration**: Custom Alembic operation to parse existing markdown files and insert into PostgreSQL
3. **Validation**: Automated verification that all CLI commands work against Postgres backend
4. **Rollback**: Alembic downgrade capability with export-to-markdown option

### Component/Area 5: Key Research Questions Addressed
From PROJ-0007 ticket research questions:
- **SQLAlchemy sync vs async**: Sync preferred for CLI context (no async benefits in synchronous CLI)
- **Connection/session management**: Per-command Session with SingletonThreadPool
- **Database migration tooling**: Alembic for schema versioning (matches architecture specs)
- **Schema design**: Preserve all existing fields, relationships, and validation logic
- **Import job architecture**: Parsing strategy with error handling and idempotency mechanism
- **Database directory handling**: Keep as backup during transition, deprecate after verification
- **DATABASE_URL**: Environment variable configuration as specified in architecture
- **PlantLogEntry modeling**: Relational table with sparse columns for event-type specific fields
- **ID generation**: Preserve VARIETY-YYYY-SEQ pattern in DB vs file-based approach
- **Connection pooling**: Align with architecture specs (min=2, max=20 via SingletonThreadPool adaptation)
- **find_next_sequence**: Replace filesystem scan with efficient SQL query using string functions

## Code References
- `commands/plant_model.py:48-50` - get_database_dir() function for directory configuration
- `commands/plant_model.py:103-121` - generate_id() and find_next_sequence() for ID generation logic
- `commands/plant_log_model.py:174-215` - load_log_entries() for consolidated log parsing
- `commands/plant_tracking_cli.py:35-43` - Directory creation and environment variable handling
- `knowledge/architecture/database/c2-container.md:121-125` - Database connection string format and pooling specs
- `knowledge/architecture/architecture-decisions.md:48-76` - Sprint 5 Database + Knowledge Base container specs

## Architecture Insights
1. **Phased Migration Approach**: Architecture specifies "Phased approach from markdown to PostgreSQL" as data persistence strategy
2. **Connection Pooling**: Architecture specifies min=2, max=20 connections - adapt SingletonThreadPool for CLI context
3. **Migration Safeguards**: Architecture mentions "migration safeguards" and references Flyway-style migrations (implemented via Alembic)
4. **Environment Variable**: Architecture specifies `DATABASE_URL` for configuration
5. **Backward Compatibility**: Markdown export preserved as write path during transition

## Historical Context (from knowledge/)
- `knowledge/tickets/PROJ-0007.md` - Defines the migration requirements and success criteria
- `knowledge/architecture/database/c2-container.md` - Specifies PostgreSQL 15 as primary data store
- `knowledge/architecture/architecture-decisions.md` - Sprint 5 ADRs confirm database container approach
- `_bmad-output/prd.md:308` - FR51: "Users can migrate data from markdown to Postgres database format"

## Related Research
- `knowledge/research/2026-05-19-PROJ-0007-postgres-integration-research.md` - This document
- `knowledge/plans/2026-04-25-PROJ-0002-track-seed-packet-schema.md` - Related schema work

## Open Questions
1. Should we implement automatic datetime timezone handling for created_at/updated_at fields?
2. What specific Alembic version should be standardized for the project?
3. Should we add database connection health check CLI command as nice-to-have feature?
4. How should we handle the transition period where both markdown and PostgreSQL are used?
5. What level of logging should be implemented for database operations in CLI context?
