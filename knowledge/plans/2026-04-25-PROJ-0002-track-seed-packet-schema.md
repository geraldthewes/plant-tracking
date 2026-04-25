# Track Seed Packet in Its Own Schema - Implementation Plan

## Overview

Introduce a `seed_packets` data store that holds unique seed packet records. Each plant will reference a seed packet via `seed_packet_id`, eliminating denormalized data. New CLI commands allow standalone seed packet management. A migration populates `seed_packets/` from existing plant records.

## Current State

| Aspect | Detail |
|--------|--------|
| Storage | Markdown files with YAML frontmatter in `database/` (13 plant `.md` files) |
| Model | `commands/plant_model.py` — `Plant` class, 3 required + 7 optional fields |
| CLI | `commands/plant_tracking_cli.py` — `create-plant` prompts for all fields every time |
| Duplication | 5 "Pepper Generic", 3 "Avocado", 3 near-duplicate "Yellow Habanero*" — same packet data re-entered |
| ADR-0006 | MVP phase: markdown storage, migration path to Postgres planned |

## Key Findings

1. **Duplicate data is real**: YEHA-001 and YEHA-002 share variety "Yellow Habanero" but differ in `variety_name` ("Yellow Habanero Pepper" vs "Yellow Habanero"), `brand` ("Gardners Basic" vs "Gardners Basics"), `days_to_maturity` (90 vs 80-100)
2. **Missing data is common**: 5 "Pepper Generic" plants have only required fields — no seed packet info
3. **Dedup key**: `(variety_name, latin_name)` is the natural unique key; `brand` is a secondary differentiator
4. **No existing standalone seed packet creation** — the ticket calls for a dedicated CLI command

## What We're NOT Doing

- Seed packet photo upload (out of scope per ticket)
- Advanced search/filter on seed packets
- Duplicate packet detection heuristics (exact match on variety_name + latin_name)
- Postgres migration (Phase 3)
- Web/mobile UI (future)

---

## Phase 1: Seed Packet Data Model

**Goal**: Create `SeedPacket` model class parallel to `Plant`, stored as markdown files in `database/seed_packets/`.

**New file**: `commands/seed_packet_model.py`

```
SeedPacket fields:
  - id: SPKT-NNN (auto-incremented, e.g., SPKT-001)
  - variety_name: string (required)
  - latin_name: string (required)
  - brand: string (optional)
  - days_to_maturity: string (optional)
  - germination_time: string (optional)
  - planting_depth: string (optional)
  - spacing: string (optional)
  - sun_requirements: string (optional)
  - indoor_start_time: string (optional)
  - created_at, updated_at: ISO timestamps
```

- `SeedPacket` class mirrors `Plant` patterns: `__init__` with validation, `to_markdown()`, `generate_id()` with sequencing, `load_from_file()`
- `find_matching(variety_name, latin_name)` — returns existing packet or None (dedup lookup)
- `list_all()` — returns all seed packets for CLI selection
- Stored as `database/seed_packets/SPKT-NNN.md`

**Tests**: `tests/test_seed_packet.py`
- Creation with valid data
- ID format (SPKT-NNN)
- ID sequencing (incremental)
- Markdown round-trip (save → load → compare)
- `find_matching` returns correct packet / None
- `list_all` returns all packets

**Verification**: `python -m pytest tests/test_seed_packet.py -v`

---

## Phase 2: Update Plant Model for Reference

**Goal**: Plants gain a `seed_packet_id` field that references a seed packet. Seed packet fields on plants become optional (deprecated but kept for migration safety).

**Changes to**: `commands/plant_model.py`

- Add `seed_packet_id` to `ALL_FIELDS`
- `seed_packet_id` is optional (supports "unknown" case)
- `REQUIRED_FIELDS` remains unchanged (`variety_name`, `latin_name`, `planned_planting_date`) — still needed for label generation
- New method: `get_seed_packet()` — loads and returns the referenced `SeedPacket` or None
- New module-level: `load_seed_packet(id)` — convenience loader

**Update tests**: `tests/test_plant_tracking.py`
- Plant with `seed_packet_id` saves/loads correctly
- Plant with `seed_packet_id: unknown` is valid
- `get_seed_packet()` resolves reference correctly

**Verification**: `python -m pytest tests/test_plant_tracking.py -v`

---

## Phase 3: CLI — Standalone Seed Packet Commands

**Goal**: Dedicated CLI commands for managing seed packets independently of plants.

**Changes to**: `commands/plant_tracking_cli.py`

### 3a. `create-seed-packet` Command

Interactive CLI that prompts for all seed packet fields and creates a new `SeedPacket` record.

```
create-seed-packet flow:
  1. Prompt for variety_name (required)
  2. Prompt for latin_name (required)
  3. Check for existing match via find_matching()
     - If match exists: show details, ask to confirm or proceed with new packet
     - If no match: continue
  4. Prompt for brand (optional)
  5. Prompt for days_to_maturity (optional)
  6. Prompt for germination_time (optional)
  7. Prompt for planting_depth (optional)
  8. Prompt for spacing (optional)
  9. Prompt for sun_requirements (optional)
  10. Prompt for indoor_start_time (optional)
  11. Create SeedPacket, save to database/seed_packets/SPKT-NNN.md
  12. Print success message with assigned ID
```

Reuses `_prompt_field` and `_prompt_optional_field` helpers from `create_plant()`.

### 3b. `list-seed-packets` Command

Lists all seed packets in a readable format for reference during plant creation.

```
list-seed-packets output:
  ID          Variety              Latin Name           Brand
  ----------  -------------------  -------------------  ----------------
  SPKT-001    Yellow Habanero      Capsicum chinense    Gardners Basics
  SPKT-002    Avocado              Persea americana
  ...
```

### 3c. `show-seed-packet` Command

Shows full details of a specific seed packet by ID.

```
show-seed-packet <packet_id>
```

**Update tests**: `tests/test_plant_tracking.py`
- `create-seed-packet` subcommand registered and callable
- `list-seed-packets` returns correct count
- `show-seed-packet` resolves and displays packet data
- Duplicate warning works when creating packet with matching variety+latin

**Verification**: `python -m pytest tests/test_plant_tracking.py -v -k SeedPacketCLI`

---

## Phase 4: CLI — Seed Packet Selection During Plant Creation

**Goal**: The `create-plant` flow first asks about seed packet, then only prompts for fields not covered by the selected packet.

**Changes to**: `commands/plant_tracking_cli.py`

New flow for `create-plant`:
1. **Seed packet lookup**: Prompt for `variety_name` + `latin_name`
2. **Match check**: Call `SeedPacket.find_matching()`
3. **If match exists**: Confirm with user, set `seed_packet_id`, skip those packet fields
4. **If no match**: Offer three paths:
   - **(A) Create new seed packet now**: Prompt for all packet fields, create the `SeedPacket`, set `seed_packet_id`
   - **(B) Use existing packet from list**: Show `list-seed-packets`, let user select by ID
   - **(C) Skip ("unknown")**: Set `seed_packet_id: unknown`, enter all fields directly on the plant (current behavior preserved)
5. **Enter remaining plant-specific fields**: `planned_planting_date` (always on plant, never on packet)
6. Save plant as before

**Update tests**: New test class `TestCreatePlantFlow` in `tests/test_plant_tracking.py` using `unittest.mock.patch` on `input()` to simulate user interactions.

**Verification**: `python -m pytest tests/test_plant_tracking.py -v -k CreatePlantFlow`

---

## Phase 5: Migration Script

**Goal**: One-shot migration that extracts unique seed packets from existing plants and backfills `seed_packet_id`.

**New file**: `scripts/migrate_seed_packets.py`

Algorithm:
1. Scan all `database/*.md` plant files
2. Group by `(variety_name, latin_name)` — this is the dedup key
3. For each group:
   - Pick representative values: first non-empty value for each field; for conflicting values, pick the most common
   - Create a `SeedPacket` record in `database/seed_packets/SPKT-NNN.md`
   - Map group → packet ID
4. For each plant:
   - Add `seed_packet_id: SPKT-NNN` to frontmatter
   - **Do NOT remove** seed packet fields from plants yet (safety: migration is reversible)
   - Update `updated_at` timestamp
5. Plants with only required fields (no packet data) get `seed_packet_id: unknown`
6. Print summary: N packets created, M plants updated

Expected output with current data (~7 unique packets):
| variety_name | latin_name | plants | packet_id |
|---|---|---|---|
| Avocado | Persea americana | 3 | SPKT-001 |
| Jimmy Nardello | Capsicum annuum | 1 | SPKT-002 |
| Lemon Verbana | Aloysia citrodora | 1 | SPKT-003 |
| Pepper Generic | Capsicum xxx | 5 | unknown |
| Serrano Pepper | Capsicum annuum | 1 | SPKT-004 |
| Trinidad Scorpion | Capsicum chinense | 1 | SPKT-005 |
| Yellow Habanero Pepper | Capsicum chinense | 1 | SPKT-006 |
| Yellow Habanero | Capsicum chinense | 2 | SPKT-007 |

*Note: "Yellow Habanero Pepper" and "Yellow Habanero" have different `variety_name` values → 2 separate groups. User can manually merge post-migration.*

**Verification**:
- Dry run: `python scripts/migrate_seed_packets.py --dry-run` → prints what would change
- Execute: `python scripts/migrate_seed_packets.py` → applies changes
- Post-check: all plants have `seed_packet_id`, all `seed_packets/SPKT-*.md` files exist
- Run full test suite: `python -m pytest tests/ -v`

---

## Phase 6: Integration Tests

**Goal**: End-to-end verification that the full flow works.

**Changes to**: `tests/test_plant_tracking.py`

- Test creating a seed packet, then creating a plant that references it
- Test loading a plant and resolving its seed packet
- Test the "unknown" path (plant with no packet data)
- Test that seed packet fields are no longer required on plants when `seed_packet_id` is present
- Test `list-seed-packets` and `show-seed-packet` commands

**Verification**: `python -m pytest tests/ -v` — all tests pass

---

## Phase 7: Documentation Updates

**Goal**: Update all user-facing and technical documentation to reflect the new seed packet model, CLI commands, and data structures.

### 7a. `docs/user.md` — User Documentation

**Updates required:**

1. **Add seed packet concepts section** (before Commands section):
   - Explain what a seed packet record is and why it exists (eliminates redundant data entry)
   - Explain the relationship: one seed packet → many plants
   - Explain the "unknown" case (no packet info available)

2. **New command docs** (add to Commands section):
   - `create-seed-packet`: full field table (9 fields), duplicate warning behavior, output format
   - `list-seed-packets`: output format, use case (reference during plant creation)
   - `show-seed-packet <id>`: output format

3. **Update `create-plant` docs**:
   - Describe the new three-phase prompt flow: (1) variety/latin lookup → (2) packet selection/create/skip → (3) remaining fields
   - Explain the three paths: use existing packet, create new packet inline, or "unknown"
   - Update field tables: required fields are now just variety_name, latin_name, planned_planting_date; the 7 packet fields are entered via seed packet, not directly
   - Note that `seed_packet_id` is stored on the plant record

4. **Update File Storage section**:
   - Document `database/seed_packets/SPKT-NNN.md` directory and format
   - Document `seed_packet_id` field in plant frontmatter
   - Show example plant file with `seed_packet_id` reference

5. **Update Plant ID Format section** (no changes needed — plant IDs unchanged)

6. **Update Database Directory Customization section** (no changes — `PLANT_DATABASE_DIR` still applies)

### 7b. `docs/specs/database.md` — Database Specification

**Updates required:**

1. **Update Overview**:
   - Mention two entity types: plants and seed packets
   - Explain the reference relationship between them

2. **Add Seed Packet Storage Location section**:
   - Directory: `database/seed_packets/`
   - File naming: `SPKT-NNN.md`
   - Same atomic operations and concurrency controls as plants

3. **Add Seed Packet Frontmatter Schema section**:
   - Full YAML example with all 9 packet fields + id, created_at, updated_at
   - Field definitions table (parallel to plant field definitions)
   - Required fields: `variety_name`, `latin_name`
   - Unique key: `(variety_name, latin_name)`

4. **Update Plant Frontmatter Schema**:
   - Add `seed_packet_id` field to schema example
   - Update field definitions table to include `seed_packet_id` (string, optional, references seed packet or "unknown")
   - Note that packet fields (`brand`, `days_to_maturity`, etc.) are now deprecated on plants but retained for backward compatibility

5. **Update Validation Rules**:
   - Add: `seed_packet_id` must match `^SPKT-\d{3}$` or be `"unknown"`
   - Add: `seed_packet_id` reference must resolve to an existing file (referential integrity)
   - Add: Seed packet uniqueness constraint on `(variety_name, latin_name)`

6. **Update Example Complete File**:
   - Show a plant record with `seed_packet_id: SPKT-001`
   - Show a corresponding seed packet record example

7. **Update Migration Path to Postgres**:
   - Mention that seed packets map to a `seed_packets` table
   - Plants table gains a `seed_packet_id` foreign key column

8. **Update Backup and Recovery**:
   - Note that `database/seed_packets/` is part of the backup scope

### 7c. `docs/specs/database.md` — New Seed Packet Example

Add a complete seed packet file example alongside the existing plant example:

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

**Verification**:
- Docs build/render without errors (no broken links, valid markdown)
- `docs/user.md` covers all 3 new CLI commands with examples
- `docs/specs/database.md` contains both entity schemas and their relationship
- Example files match actual output format from code

---

## File Summary

| File | Action | Purpose |
|------|--------|---------|
| `commands/seed_packet_model.py` | **New** | `SeedPacket` model, storage, dedup lookup |
| `commands/plant_model.py` | **Modify** | Add `seed_packet_id`, `get_seed_packet()` |
| `commands/plant_tracking_cli.py` | **Modify** | New commands + packet selection in `create-plant` |
| `scripts/migrate_seed_packets.py` | **New** | One-shot migration from existing plants |
| `tests/test_seed_packet.py` | **New** | Seed packet model tests |
| `tests/test_plant_tracking.py` | **Modify** | Plant reference tests, CLI flow tests |
| `docs/user.md` | **Modify** | Document seed packets, 3 new CLI commands, updated `create-plant` flow |
| `docs/specs/database.md` | **Modify** | Add seed packet schema, update plant schema, add relationship docs |

## New CLI Commands Summary

| Command | Purpose |
|---------|---------|
| `create-seed-packet` | Interactive prompts to create a new seed packet record |
| `list-seed-packets` | Tabular list of all seed packets for reference |
| `show-seed-packet <id>` | Full details of a specific seed packet |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Yellow Habanero / Yellow Habanero Pepper treated as separate packets | Migration uses exact match; user can merge post-migration. Document in migration output. |
| Migration is irreversible if we delete fields from plants | Phase 5 does NOT delete fields — only adds `seed_packet_id`. Field removal is a separate future step. |
| CLI flow is confusing with too many prompts | Two-phase prompt: first ask variety/latin for lookup, then branch. "unknown" path is one keystroke. |
| Creating duplicate packets accidentally | `create-seed-packet` warns on match and requires explicit confirmation to proceed. |

## Success Criteria Mapping

- [x] Seed packet data model created, tested, follows existing patterns
- [x] `create-seed-packet` CLI command for standalone seed packet creation
- [x] `list-seed-packets` and `show-seed-packet` commands for reference
- [x] Plant creation flow supports selecting an existing seed packet
- [x] Plant creation flow supports "unknown" option
- [x] Migration script with dry-run, populates seed_packets from existing plants
- [x] All automated tests pass
- [x] No data loss — migration only adds fields, never removes
- [x] `docs/user.md` updated with seed packet concepts, new CLI commands, revised `create-plant` flow
- [x] `docs/specs/database.md` updated with seed packet schema, plant `seed_packet_id` field, relationship docs, examples
