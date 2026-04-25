# Plant Tracking Database Specification

## Overview

This document specifies the database format and storage mechanism for the Plant Tracking System. The system uses local markdown files as the primary data store for the MVP, with a planned migration path to Postgres for Phase 3.

The system tracks two entity types:
- **Plants**: Individual growing records with planting dates and IDs
- **Seed Packets**: Reusable variety information records (brand, days to maturity, etc.)

Plants reference seed packets via `seed_packet_id`, eliminating denormalized data across plant records.

## Storage Location

- **Plants directory**: `database/` (relative to project root)
- **Plant file naming**: `{plant_id}.md` (e.g., `HABY-2026-001.md`)
- **Seed packets directory**: `database/seed_packets/`
- **Seed packet file naming**: `SPKT-NNN.md` (e.g., `SPKT-001.md`)
- **Atomic Operations**: All write operations use temporary files + rename to prevent corruption
- **Concurrency Control**: File locking (fcntl) prevents concurrent writes to the same record

## Plant File Format

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
seed_packet_id: "SPKT-001"
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
| `brand` | string | No | Seed brand/company name *(deprecated on plants — use seed packet)* |
| `days_to_maturity` | integer | No | Days from planting to harvest *(deprecated on plants — use seed packet)* |
| `germination_time` | string | No | Expected germination period *(deprecated on plants — use seed packet)* |
| `planting_depth` | string | No | Recommended planting depth *(deprecated on plants — use seed packet)* |
| `spacing` | string | No | Recommended plant spacing *(deprecated on plants — use seed packet)* |
| `sun_requirements` | string | No | Sunlight needs *(deprecated on plants — use seed packet)* |
| `indoor_start_time` | string | No | When to start indoors *(deprecated on plants — use seed packet)* |
| `planned_planting_date` | string (YYYY-MM-DD) | Yes | Date when planting is planned |
| `seed_packet_id` | string | No | References a seed packet (`SPKT-NNN`) or `"unknown"` |
| `created_at` | string (ISO 8601) | Yes | Timestamp when record was created |
| `updated_at` | string (ISO 8601) | Yes | Timestamp when record was last updated |

The three label fields (`variety_name`, `latin_name`, `planned_planting_date`) are required. Seed packet fields (`brand`, `days_to_maturity`, etc.) are deprecated on plants but retained for backward compatibility during migration.

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

## Seed Packet File Format

Seed packet records store reusable variety information. Each packet is stored as a markdown file with YAML frontmatter.

### Seed Packet Storage Location

- **Directory**: `database/seed_packets/`
- **File naming**: `SPKT-NNN.md` (zero-padded 3-digit sequence)
- **Same atomic operations and concurrency controls as plant files**

### Frontmatter Schema

```yaml
---
id: SPKT-001
variety_name: Yellow Habanero
latin_name: Capsicum chinense
brand: Gardners Basics
days_to_maturity: 80-100
germination_time: 7-21
planting_depth: '0.25'
spacing: 12-18
sun_requirements: Full Sun
indoor_start_time: 8-10 weeks before last frost
created_at: '2026-04-25T00:00:00Z'
updated_at: '2026-04-25T00:00:00Z'
---
```

### Seed Packet Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes (auto-generated) | Unique identifier in SPKT-NNN format |
| `variety_name` | string | Yes | Common name of the plant variety |
| `latin_name` | string | Yes | Scientific/Latin name |
| `brand` | string | No | Seed brand/company name |
| `days_to_maturity` | string | No | Days from planting to harvest (range or single value) |
| `germination_time` | string | No | Expected germination period |
| `planting_depth` | string | No | Recommended planting depth |
| `spacing` | string | No | Recommended plant spacing |
| `sun_requirements` | string | No | Sunlight needs |
| `indoor_start_time` | string | No | When to start indoors before last frost |
| `created_at` | string (ISO 8601) | Yes | Timestamp when record was created |
| `updated_at` | string (ISO 8601) | Yes | Timestamp when record was last updated |

**Unique key**: `(variety_name, latin_name)` — no two packets may share the same variety and Latin name combination.

## Relationship: Plants ↔ Seed Packets

- A plant references a seed packet via `seed_packet_id`
- `seed_packet_id` must match `^SPKT-\d{3}$` or be `"unknown"`
- When `seed_packet_id` is present and valid, the referenced seed packet file must exist (referential integrity)
- A seed packet can be referenced by zero or many plants (one-to-many)

## Data Integrity Measures

1. **Atomic Writes**: All file updates write to a temporary file first, then rename to the target file
2. **File Locking**: Uses `fcntl` advisory locks to prevent concurrent writes to the same record
3. **Read-after-write Consistency**: Immediate data visibility after write operations
4. **Background Flushing**: Periodic `fsync` calls every 5 seconds to flush buffers to disk
5. **Corruption Detection**: File checksum verification on read operations

## Migration Path to Postgres

The markdown storage design includes a clear migration path to Postgres:

1. **Schema Mapping**: Direct mapping of frontmatter fields to database columns
2. **Seed Packets Table**: `seed_packets` table with columns matching the seed packet schema
3. **Plants Table**: Gains a `seed_packet_id` foreign key column referencing `seed_packets`
4. **Content Storage**: Observational notes stored in a separate `observations` table or as JSONB
5. **ID Generation**: Database sequences replace file-based sequencing
6. **Backward Compatibility**: Dual-write capability during migration period
7. **Export/Import**: CSV/JSON export/import utilities for data migration

## Validation Rules

1. **Required Fields**: All fields marked as required in the schema must be present
2. **Date Format**: `planned_planting_date` must be valid YYYY-MM-DD
3. **ID Format (Plants)**: Must match regex `^[A-Z]{2,4}-\d{4}-\d{3}$`
4. **ID Format (Seed Packets)**: Must match regex `^SPKT-\d{3}$`
5. **Numeric Values**: `days_to_maturity` must be positive integer
6. **Uniqueness**: `id` must be unique across all records of the same type
7. **Seed Packet Uniqueness**: `(variety_name, latin_name)` must be unique across all seed packets
8. **Referential Integrity**: `seed_packet_id` on plants must resolve to an existing seed packet file (or be `"unknown"`)

## Example Complete File — Plant

```markdown
---
id: HABY-2026-001
variety_name: Yellow Habanero
latin_name: Capsicum chinense
planned_planting_date: "2026-04-15"
seed_packet_id: "SPKT-001"
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

## Example Complete File — Seed Packet

```markdown
---
id: SPKT-001
variety_name: Yellow Habanero
latin_name: Capsicum chinense
brand: Gardners Basics
days_to_maturity: 80-100
germination_time: 7-21
planting_depth: '0.25'
spacing: 12-18
sun_requirements: Full Sun
indoor_start_time: 8-10 weeks before last frost
created_at: '2026-04-25T00:00:00Z'
updated_at: '2026-04-25T00:00:00Z'
---

# Seed Packet: Yellow Habanero

*ID: SPKT-001*

*Created: 2026-04-25*
```

## Backup and Recovery

1. **Manual Backup**: Copy the entire `database/` directory (includes both `database/*.md` and `database/seed_packets/*.md`)
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
