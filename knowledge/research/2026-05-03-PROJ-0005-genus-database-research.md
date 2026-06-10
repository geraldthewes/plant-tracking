---
date: 2026-05-03T15:38:00Z
researcher: Gerald
git_commit: 0a0c2874d751a51dd57ee58aae0902d9e7a90894
branch: main
repository: plant-tracking
topic: "Add support for genus database - research findings for PROJ-0005"
tags: [research, codebase, genus-database, seed-packet, cli-flow, label-generation]
status: complete
last_updated: 2026-05-03
last_updated_by: Gerald
---

# Research: Add support for genus database - research findings for PROJ-0005

**Date**: 2026-05-03T15:38:00Z  
**Researcher**: Gerald  
**Git Commit**: 0a0c2874d751a51dd57ee58aae0902d9e7a90894  
**Branch**: main  
**Repository**: plant-tracking  

## Research Question
Research the necessary elements needed to implement the genus database feature as described in PROJ-0005, including analyzing the seed packet database implementation, current create-plant CLI flow, label generation system, and identifying gaps that need to be addressed.

## Summary
Based on the research of the plant-tracking codebase, implementing the genus database feature (PROJ-0005) can leverage the existing seed packet database implementation as a reference pattern. The seed packet system provides a proven model for persistent storage, CLI integration, and data relationships that can be adapted for genus management. Key findings show that the codebase uses a file-based "database" approach with YAML frontmatter in markdown files, and the genus database would follow similar patterns. The current create-plant flow already prompts for variety and Latin names separately, which needs to be modified to reference genus entries. The label generation system already extracts Latin names from plant records, so integrating genus lookup would require modifying the data loading phase to resolve genus references. No fuzzy matching library is currently implemented, but this is identified as a needed component for the feature.

## Detailed Findings

### Seed Packet Database Implementation (Reference Pattern)
The seed packet database implementation provides the exact pattern to mimic for the genus database:

**Storage Format**: 
- File-based "database" using markdown files with YAML frontmatter
- Stored in `database/seed_packets/` directory
- Files named `SPKT-NNN.md` with auto-incremented IDs
- Example format seen in `database/seed_packets/SPKT-001.md`

**Schema** (from `commands/seed_packet_model.py` and `knowledge/specs/database.md`):
- Required fields: `variety_name`, `latin_name` (matching genus DB requirements)
- Auto-generated fields: `id` (SPKT-NNN format), `created_at`, `updated_at`
- Optional fields: `brand`, `days_to_maturity`, `germination_time`, etc.
- Unique constraint: `(variety_name, latin_name)` enforced at CLI layer

**CRUD Operations** (in `commands/plant_tracking_cli.py` and `commands/seed_packet_model.py`):
- Create: `create_seed_packet()` function with interactive prompts and duplicate checking
- Read: `find_matching()` for exact lookups, `list_all()` for listing, `load_from_file()` for individual records
- Update: Implicit via `to_markdown()` refreshing `updated_at` timestamp
- Delete: Not implemented (consistent with genus DB out-of-scope items)

**Plant Relationship Pattern**:
- Plants store `seed_packet_id` referencing seed packet records
- Resolution via `Plant.get_seed_packet()` → `load_seed_packet(id)` → `load_from_file()`
- This same pattern would apply for genus references in plant records

### Current Create-Plant CLI Flow
The current `create-plant` flow in `commands/plant_tracking_cli.py` (lines 80-147) operates in two phases:

**Phase 1 - Variety Identification** (lines 88-119):
- Prompts separately for `variety_name` and `latin_name`
- Calls `find_matching()` to check for existing seed packet
- Presents options to create/select/skip seed packet if no match

**Phase 2 - Plant-Specific Fields** (lines 121-147):
- Prompts for required `planting_date`
- Constructs and persists `Plant` object with `seed_packet_id` field

**Key Helper Functions**:
- `_prompt_field()` and `_prompt_optional_field()` for input handling
- `_create_packet_inline()` for inline seed packet creation during plant flow
- `_select_existing_packet()` for selecting from existing packets

This flow needs modification to:
1. Replace separate variety/Latin name prompts with genus selection/creation
2. Automatically retrieve Latin name from genus database after selection
3. Maintain the three-path workflow: exact match, fuzzy search, or create new genus

### Label Generation System
The label generation system (in `commands/label_generator.py`) currently:
1. Loads plant data via `Plant.load_plant_from_file()` 
2. Extracts `latin_name` directly from plant data: `plant.data.get('latin_name', '')`
3. Renders the Latin text onto the label image at a configured position

For genus database integration, this system would need to:
1. Check if plant record has a `genus_id` reference instead of direct Latin name
2. If genus reference exists, load the genus record to retrieve Latin name
3. Fall back to direct Latin name for existing records during migration period

### Plant Record Data Format
Plant records are stored as markdown files with YAML frontmatter in the `database/` directory (e.g., `database/SEPE-2026-001.md`):

```yaml
---
variety_name: Serrano Pepper
latin_name: Capsicum annuum
brand: Gardners Basics
days_to_maturity: '80'
...
id: SEPE-2026-001
created_at: '2026-04-24T11:50:48Z'
updated_at: '2026-04-26T13:31:26Z'
seed_packet_id: SPKT-002
planting_date: '2024-09-01'
---
```

For genus database implementation:
- Add `genus_id` field to store reference to genus database entry
- Keep `latin_name` field for backward compatibility during migration
- Migration script would populate genus database and update plant records with `genus_id`

### Fuzzy Matching Status
Research confirms:
- No fuzzy matching library is currently installed (checked `pyproject.toml`)
- No fuzzy matching implementation exists in any Python source files
- Only incidental reference is in `node_modules/commander/lib/suggestSimilar.js` (third-party CLI utility)
- PROJ-0005 identifies fuzzy matching as a research question needing decision:
  - Options: fuzzywuzzy, thefuzz, rapidfuzz, difflib, or jellyfish
  - Library selection needed during planning phase

### Data Analysis Needs
To complete implementation planning, the following data questions from PROJ-0005 need investigation:

1. **Unique genus pairs count**: Run migration script in dry-run mode to count unique (variety_name, latin_name) pairs
2. **Edge case analysis**: Examine existing Latin name data for empty fields, duplicates, typos
3. **Migration validation**: Ensure script extracts all unique pairs with no data loss

## Code References
- `commands/seed_packet_model.py:18` - SeedPacket.REQUIRED_FIELDS showing variety_name, latin_name requirement
- `commands/seed_packet_model.py:89` - find_matching() method for exact lookups
- `commands/seed_packet_model.py:110` - list_all() method for listing all records
- `commands/seed_packet_model.py:126` - load_from_file() for reading individual records
- `commands/plant_tracking_cli.py:259` - create_seed_packet() CLI function
- `commands/plant_tracking_cli.py:80-147` - create_plant() main flow showing current variety/Latin name prompting
- `commands/label_generator.py:43` - Latin name extraction: plant.data.get('latin_name', '')
- `database/seed_packets/SPKT-001.md` - Example seed packet record format
- `database/SEPE-2026-001.md` - Example plant record showing seed_packet_id reference pattern
- `scripts/migrate_seed_packets.py` - Migration script pattern for backfilling references

## Architecture Insights
1. **File-Based Database Pattern**: The codebase consistently uses markdown files with YAML frontmatter as a lightweight database solution, avoiding external dependencies. This pattern should be continued for the genus database.

2. **Reference-Based Relationships**: Plant records reference seed packets via `seed_packet_id`, establishing a clear pattern for how the genus database should integrate - plants would store `genus_id` referencing genus database entries.

3. **CLI-First Implementation**: All database operations are exposed through CLI commands (`create_seed_packet`, `list_seed_packets`, etc.), maintaining consistency with the existing user experience.

4. **Migration-First Approach**: The existing `migrate_seed_packets.py` script demonstrates the pattern for safely migrating existing data to new database structures, which should be replicated for genus database implementation.

5. **Validation Enforcement**: Both Plant and SeedPacket models enforce required field validation, ensuring data integrity - genus database records would need similar validation for variety_name and latin_name fields.

## Historical Context (from knowledge/)
- `knowledge/tickets/PROJ-0005.md` - Original feature request detailing the problem of redundant data entry and proposed solution
- `knowledge/plans/2026-04-25-PROJ-0002-track-seed-packet-schema.md` - Shows the detailed implementation approach used for seed packets that should be mirrored for genus DB
- `knowledge/tickets/PROJ-0002.md` - Original seed packet ticket showing similar requirements that were implemented

## Related Research
- No existing research documents found specifically for genus database implementation
- Seed packet implementation research would be directly applicable as reference

## Open Questions
1. **Fuzzy Library Selection**: Which fuzzy matching library should be adopted (fuzzywuzzy/thefuzz, rapidfuzz, difflib, or jellyfish)?
2. **Migration Timing**: Should genus database migration run automatically on first use or via explicit CLI command?
3. **Backward Compatibility**: How long should the system support reading Latin name directly from plant records during transition period?
4. **CLI UX**: What specific wording and flow should the three-path genus selection UI use?
5. **Error Handling**: How should the system handle cases where genus references become invalid (deleted genus records)?