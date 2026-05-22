# Plant Tracking Database Specification

## Overview

The Plant Tracking System uses **PostgreSQL as the primary data store**, managed through the `plant_service` package which follows Ports & Adapters (Hexagonal) architecture. Markdown files are written as backups for human-readable access.

The system tracks four entity types:
- **Plants**: Individual growing records with planting dates and IDs
- **Seed Packets**: Reusable variety information records (brand, days to maturity, etc.)
- **Genera**: Unique (variety name, Latin name) pairs that eliminate redundant data entry
- **Plant Log Entries**: Care activity logs (humidity, water, fertilizer, notes)

Plants reference seed packets via `seed_packet_id` and genus records via `genus_id`, eliminating denormalized data across plant records.

### Architecture

```
CLI / FastAPI → plant_service (service layer) → SQLAlchemy repositories → PostgreSQL
                                      ↓
                              Markdown backup files
```

## PostgreSQL Schema

Managed by Alembic migrations. All tables defined in `packages/plant_service/src/plant_service/adapters/repository/models/`.

### Storage Location (Markdown Backups)

- **Plants directory**: `database/` (relative to project root)
- **Plant file naming**: `{plant_id}.md` (e.g., `HABY-2026-001.md`)
- **Seed packets directory**: `database/seed_packets/`
- **Seed packet file naming**: `SPKT-NNN.md` (e.g., `SPKT-001.md`)
- **Genera directory**: `database/genera/`
- **Genus file naming**: `GENUS-NNN.md` (e.g., `GENUS-001.md`)

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
planting_date: "2026-04-15"
  seed_packet_id: "SPKT-001"
genus_id: "GENUS-001"
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
| `planting_date` | string (YYYY-MM-DD) | Yes | Date when the plant was planted |
| `seed_packet_id` | string | No | References a seed packet (`SPKT-NNN`) or `"unknown"` |
| `genus_id` | string | No | References a genus (`GENUS-NNN`) or `"unknown"` |
| `created_at` | string (ISO 8601) | Yes | Timestamp when record was created |
| `updated_at` | string (ISO 8601) | Yes | Timestamp when record was last updated |

The three label fields (`variety_name`, `latin_name`, `planting_date`) are required. Seed packet fields (`brand`, `days_to_maturity`, etc.) are deprecated on plants but retained for backward compatibility during migration.

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

## Genus File Format

Genus records store unique (variety name, Latin name) pairs. Each genus is stored as a markdown file with YAML frontmatter.

### Genus Storage Location

- **Directory**: `database/genera/`
- **File naming**: `GENUS-NNN.md` (zero-padded 3-digit sequence)
- **Same atomic operations and concurrency controls as plant files**

### Frontmatter Schema

```yaml
---
variety_name: Yellow Habanero
latin_name: Capsicum chinense
id: GENUS-001
created_at: '2026-05-03T00:00:00Z'
updated_at: '2026-05-03T00:00:00Z'
---
```

### Genus Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes (auto-generated) | Unique identifier in GENUS-NNN format |
| `variety_name` | string | Yes | Common name of the plant variety |
| `latin_name` | string | Yes | Scientific/Latin name |
| `created_at` | string (ISO 8601) | Yes | Timestamp when record was created |
| `updated_at` | string (ISO 8601) | Yes | Timestamp when record was last updated |

**Unique key**: `(variety_name, latin_name)` — no two genera may share the same variety and Latin name combination.

## Relationship: Plants ↔ Seed Packets

- A plant references a seed packet via `seed_packet_id`
- `seed_packet_id` must match `^SPKT-\d{3}$` or be `"unknown"`
- When `seed_packet_id` is present and valid, the referenced seed packet file must exist (referential integrity)
- A seed packet can be referenced by zero or many plants (one-to-many)

## Relationship: Plants ↔ Genera

- A plant references a genus via `genus_id`
- `genus_id` must match `^GENUS-\d{3}$` or be `"unknown"`
- When `genus_id` is present and valid, the referenced genus file must exist (referential integrity)
- A genus can be referenced by zero or many plants (one-to-many)
- Label generation resolves Latin name from genus database when `genus_id` is present, falling back to direct `latin_name` field for backward compatibility

## Data Integrity Measures

PostgreSQL provides:
1. **ACID Transactions**: Unit of Work pattern ensures atomic operations across tables
2. **Foreign Key Constraints**: `plants.seed_packet_id` → `seed_packets.id`, `plants.genus_id` → `genera.id`
3. **Check Constraints**: Event type validation, humidity range (1-10), required fields per event type
4. **Referential Integrity**: Database-enforced FK relationships
5. **Unique Constraints**: `(variety_name, latin_name)` unique on `seed_packets` and `genera`

Markdown backups provide:
- Human-readable file records for portability
- Fallback access when PostgreSQL is unavailable

## Database Tables

### `plants`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | VARCHAR(20) | PK, application-generated (VARIETY-YYYY-SEQ) |
| `variety_name` | VARCHAR(100) | NOT NULL |
| `latin_name` | VARCHAR(100) | NOT NULL |
| `brand` | VARCHAR(100) | nullable |
| `days_to_maturity` | VARCHAR(20) | nullable |
| `germination_time` | VARCHAR(20) | nullable |
| `planting_depth` | VARCHAR(20) | nullable |
| `spacing` | VARCHAR(20) | nullable |
| `sun_requirements` | VARCHAR(50) | nullable |
| `indoor_start_time` | VARCHAR(50) | nullable |
| `planting_date` | VARCHAR(10) | NOT NULL (YYYY-MM-DD) |
| `seed_packet_id` | VARCHAR(10) | FK → `seed_packets.id`, nullable |
| `genus_id` | VARCHAR(10) | FK → `genera.id`, nullable |
| `created_at` | TIMESTAMP | server_default now() |
| `updated_at` | TIMESTAMP | server_default now(), onupdate now() |

### `seed_packets`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | VARCHAR(10) | PK, application-generated (SPKT-NNN) |
| `variety_name` | VARCHAR(100) | NOT NULL |
| `latin_name` | VARCHAR(100) | NOT NULL |
| `brand` | VARCHAR(100) | nullable |
| `days_to_maturity` | VARCHAR(20) | nullable |
| `germination_time` | VARCHAR(20) | nullable |
| `planting_depth` | VARCHAR(20) | nullable |
| `spacing` | VARCHAR(20) | nullable |
| `sun_requirements` | VARCHAR(50) | nullable |
| `indoor_start_time` | VARCHAR(50) | nullable |
| `created_at` | TIMESTAMP | server_default now() |
| `updated_at` | TIMESTAMP | server_default now(), onupdate now() |

### `genera`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | VARCHAR(10) | PK, application-generated (GENUS-NNN) |
| `variety_name` | VARCHAR(100) | NOT NULL |
| `latin_name` | VARCHAR(100) | NOT NULL |
| `created_at` | TIMESTAMP | server_default now() |
| `updated_at` | TIMESTAMP | server_default now(), onupdate now() |

### `plant_log_entries`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PK, autoincrement |
| `plant_id` | VARCHAR(20) | FK → `plants.id`, NOT NULL |
| `event_type` | VARCHAR(20) | NOT NULL, CHECK IN ('humidity', 'water', 'fertilizer', 'note') |
| `timestamp` | VARCHAR(20) | NOT NULL (ISO 8601) |
| `level` | INTEGER | nullable, CHECK (1-10 for humidity) |
| `amount_ml` | INTEGER | nullable (required for water) |
| `fertilizer_type` | VARCHAR(50) | nullable |
| `fertilizer_strength` | VARCHAR(20) | nullable |
| `text` | VARCHAR(500) | nullable (required for note) |
| `created_at` | TIMESTAMP | server_default now() |
| `updated_at` | TIMESTAMP | server_default now(), onupdate now() |

**Check constraints**:
- Event type fields: `(event_type, level/amount_ml/fertilizer_type/fertilizer_strength/text)` must match event type
- Humidity level: `1-10` range

## Validation Rules

1. **Required Fields**: All fields marked as required in the schema must be present
2. **Date Format**: `planting_date` must be valid YYYY-MM-DD
3. **ID Format (Plants)**: Must match regex `^[A-Z]{2,4}-\d{4}-\d{3}$`
4. **ID Format (Seed Packets)**: Must match regex `^SPKT-\d{3}$`
5. **Numeric Values**: `days_to_maturity` must be positive integer
6. **Uniqueness**: `id` must be unique across all records of the same type
7. **Seed Packet Uniqueness**: `(variety_name, latin_name)` must be unique across all seed packets
8. **Referential Integrity**: `seed_packet_id` on plants must resolve to an existing seed packet file (or be `"unknown"`)
9. **ID Format (Genera)**: Must match regex `^GENUS-\d{3}$`
10. **Genus Uniqueness**: `(variety_name, latin_name)` must be unique across all genera
11. **Referential Integrity**: `genus_id` on plants must resolve to an existing genus file (or be `"unknown"`)

## Example Complete File — Plant

```markdown
---
id: HABY-2026-001
variety_name: Yellow Habanero
latin_name: Capsicum chinense
planting_date: "2026-04-15"
seed_packet_id: "SPKT-001"
genus_id: "GENUS-001"
created_at: "2026-04-22T10:30:00Z"
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

## Example Complete File — Genus

```markdown
---
variety_name: Yellow Habanero
latin_name: Capsicum chinense
id: GENUS-001
created_at: '2026-05-03T00:00:00Z'
updated_at: '2026-05-03T00:00:00Z'
---

# Genus Record for Yellow Habanero

*ID: GENUS-001*

*Created: 2026-05-03*
```

## Backup and Recovery

1. **Manual Backup**: Copy the entire `database/` directory (includes `database/*.md`, `database/seed_packets/*.md`, and `database/genera/*.md`)
2. **Export Functionality**: CLI commands to export data to CSV/JSON
3. **Import Functionality**: CLI commands to import data from CSV/JSON
4. **Version Control**: Repository tracks schema changes but not data files (by .gitignore)

## Backup and Recovery

1. **PostgreSQL Backup**: Standard `pg_dump` for full database backup
2. **Markdown Export**: Export service streams data to Markdown files
3. **Version Control**: Repository tracks schema changes; data files excluded via `.gitignore`
