# Plant Tracking Database Specification

## Overview

This document specifies the database format and storage mechanism for the Plant Tracking System. The system uses local markdown files as the primary data store for the MVP, with a planned migration path to Postgres for Phase 3.

## Storage Location

- **Directory**: `database/` (relative to project root)
- **File Naming Convention**: `{plant_id}.md` (e.g., `HABY-2026-001.md`)
- **Atomic Operations**: All write operations use temporary files + rename to prevent corruption
- **Concurrency Control**: File locking (fcntl) prevents concurrent writes to the same record

## File Format

Each plant record is stored as a markdown file with YAML frontmatter followed by optional observational notes in markdown format.

### Frontmatter Schema

```yaml
---
id: HABY-2026-001
variety_name: Yellow Habanero
latin_name: Capsicum chinense
brand: Burpee
days_to_maturity: 90
germination_time: "7-14 days"
planting_depth: "0.25 inches"
spacing: "18 inches"
sun_requirements: "Full sun"
indoor_start_time: "8 weeks before last frost"
planned_planting_date: "2026-04-15"
created_at: "2026-04-22T10:30:00Z"
updated_at: "2026-04-22T10:30:00Z"
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes (auto-generated) | Unique identifier in VARIETY-YYYY-SEQ format |
| `variety_name` | string | Yes | Common name of the plant variety (e.g., "Yellow Habanero") |
| `latin_name` | string | Yes | Scientific/Latin name (e.g., "Capsicum chinense") |
| `brand` | string | Yes | Seed brand/company name |
| `days_to_maturity` | integer | Yes | Days from planting to harvest |
| `germination_time` | string | Yes | Expected germination period (e.g., "7-14 days") |
| `planting_depth` | string | Yes | Recommended planting depth (e.g., "0.25 inches") |
| `spacing` | string | Yes | Recommended plant spacing (e.g., "18 inches") |
| `sun_requirements` | string | Yes | Sunlight needs (e.g., "Full sun", "Partial shade") |
| `indoor_start_time` | string | Yes | When to start indoors before last frost (e.g., "8 weeks") |
| `planned_planting_date` | string (YYYY-MM-DD) | Yes | Date when planting is planned |
| `created_at` | string (ISO 8601) | Yes | Timestamp when record was created |
| `updated_at` | string (ISO 8601) | Yes | Timestamp when record was last updated |

### Content Section

After the frontmatter, the file may contain observational notes in markdown format:

```markdown
# Plant Record for Yellow Habanero

*ID: HABY-2026-001*

*Created: 2026-04-22*

## Observations

- 2026-04-01: Germination observed
- 2026-04-15: Transplanted to larger containers
- 2026-05-15: First fertilizer application
```

## Data Integrity Measures

1. **Atomic Writes**: All file updates write to a temporary file first, then rename to the target file
2. **File Locking**: Uses `fcntl` advisory locks to prevent concurrent writes to the same record
3. **Read-after-write Consistency**: Immediate data visibility after write operations
4. **Background Flushing**: Periodic `fsync` calls every 5 seconds to flush buffers to disk
5. **Corruption Detection**: File checksum verification on read operations

## Migration Path to Postgres

The markdown storage design includes a clear migration path to Postgres:

1. **Schema Mapping**: Direct mapping of frontmatter fields to database columns
2. **Content Storage**: Observational notes stored in a separate `observations` table or as JSONB
3. **ID Generation**: Database sequences replace file-based sequencing
4. **Backward Compatibility**: Dual-write capability during migration period
5. **Export/Import**: CSV/JSON export/import utilities for data migration

## Validation Rules

1. **Required Fields**: All fields marked as required in the schema must be present
2. **Date Format**: `planned_planting_date` must be valid YYYY-MM-DD
3. **ID Format**: Must match regex `^[A-Z]{2,4}-\d{4}-\d{3}$`
4. **Numeric Values**: `days_to_maturity` must be positive integer
5. **Uniqueness**: `id` must be unique across all records

## Example Complete File

```markdown
---
id: HABY-2026-001
variety_name: Yellow Habanero
latin_name: Capsicum chinense
brand: Burpee
days_to_maturity: 90
germination_time: "7-14 days"
planting_depth: "0.25 inches"
spacing: "18 inches"
sun_requirements: "Full sun"
indoor_start_time: "8 weeks before last frost"
planned_planting_date: "2026-04-15"
created_at: "2026-04-22T10:30:00Z"
updated_at: "2026-04-22T10:30:00Z"
---

# Plant Record for Yellow Habanero

*ID: HABY-2026-001*

*Created: 2026-04-22*

## Observations

- 2026-04-01: Germination observed at 70°F
- 2026-04-15: Transplanted to 4-inch containers
- 2026-05-15: Applied 1/4 strength liquid fertilizer (NPK 5-5-5)
- 2026-06-01: First true leaves visible
- 2026-06-15: Began hardening off process
```

## Backup and Recovery

1. **Manual Backup**: Copy the entire `database/` directory
2. **Export Functionality**: CLI commands to export data to CSV/JSON
3. **Import Functionality**: CLI commands to import data from CSV/JSON
4. **Version Control**: Repository tracks schema changes but not data files (by .gitignore)

## Performance Characteristics

- **Read Latency**: <10ms for typical records
- **Write Latency**: <20ms (including atomic operations and locking)
- **Scalability**: Suitable for hundreds to low thousands of records
- **Concurrent Readers**: Unlimited (read-only file access)
- **Concurrent Writers**: Limited by file locking (serialized per record)

## Limitations (MVP)

1. No built-in search/indexing (linear scan required for listings)
2. No transactional guarantees across multiple records
3. Limited query capabilities (filtered listings via Plant Data Service)
4. Manual backup required (no automated snapshots)

These limitations are addressed in the planned Postgres migration for Phase 3.