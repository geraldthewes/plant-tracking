# User Documentation

## Installation

Install the CLI and service package:

```bash
pip install .
uv pip install -e packages/plant_service
```

Required Python packages (installed automatically):
- `qrcode[pil]` - QR code generation
- `Pillow` - Image processing
- `PyYAML` - YAML frontmatter parsing
- `sqlalchemy>=2.0` - Database ORM
- `psycopg2-binary>=2.9` - PostgreSQL adapter
- `thefuzz[speedup]>=0.22` - Fuzzy genus matching

## Setup

### PostgreSQL Database (Primary Storage)

Copy the environment template and edit with your credentials:

```bash
cp .env.template .env
# Edit .env with your PostgreSQL connection details
```

Run the database migration to create tables:

```bash
alembic upgrade head
```

### Markdown Backup (Fallback)

A `database/` directory is created automatically in the project root. All plant records are stored in PostgreSQL, with Markdown files written as backups for human-readable access and portability.

### Configuration (`.env` file)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `PLANT_DATABASE_DIR` | No | `database` | Markdown backup directory |

## Seed Packets

A **seed packet** is a reusable record of information from a seed packet — variety name, Latin name, brand, days to maturity, germination time, and more. By storing this information once in a seed packet, you avoid re-entering the same data every time you plant a new seed of the same variety.

**Relationship**: One seed packet → many plants.

When creating a plant record, the system looks for a matching seed packet by variety name and Latin name. If found, it reuses that data instead of asking you to re-enter it.

**"Unknown" case**: If you don't have packet information available (e.g., saved seeds), choose the "unknown" option and the fields are stored directly on the plant record.

## Genus Database

A **genus record** stores a unique (variety name, Latin name) pair. By storing this information once, you eliminate redundant data entry when creating multiple plant records of the same variety. The genus database also provides fuzzy matching to find similar variety names even with typos.

**Relationship**: One genus → many plants.

When creating a plant record, the system looks for a matching genus by variety name and Latin name. If found, it links the plant to that genus via `genus_id`. If no exact match exists, you can create a new genus, select from existing entries, or use fuzzy search.

**"Unknown" case**: If you skip genus lookup, the Latin name is stored directly on the plant record and `genus_id` is set to `"unknown"`.

## Commands

### `create-seed-packet`

Create a standalone seed packet record that can be referenced by multiple plants.

```bash
python -m commands.plant_tracking_cli create-seed-packet
```

The interactive prompt asks for:

**Required fields:**
| Field | Example | Description |
|-------|---------|-------------|
| Variety name | Yellow Habanero | Common name of the plant variety |
| Latin name | Capsicum chinense | Scientific name |

**Optional fields:**
| Field | Example | Description |
|-------|---------|-------------|
| Brand | Burpee | Seed company name |
| Days to maturity | 60-75 | Days from planting to harvest |
| Germination time | 7-14 days | Expected germination period |
| Planting depth | 0.25 inches | Recommended depth |
| Spacing | 18 inches | Recommended plant spacing |
| Sun requirements | Full sun | Sunlight needs |
| Indoor start time | 8 weeks before last frost | When to start indoors |

If a matching seed packet already exists (same variety + Latin name), the system warns you and asks if you want to create a duplicate anyway.

### `list-seed-packets`

Display all seed packets in a table for reference during plant creation.

```bash
python -m commands.plant_tracking_cli list-seed-packets
```

Output:
```
ID           Variety                     Latin Name                  Brand
------------ -------------------------  -------------------------  --------------------
SPKT-001     Yellow Habanero            Capsicum chinense          Gardners Basics
SPKT-002     Avocado                    Persea americana
```

### `show-seed-packet <id>`

Show full details of a specific seed packet.

```bash
python -m commands.plant_tracking_cli show-seed-packet SPKT-001
```

### `create-plant`

Create a new plant record. The system first looks up a matching genus, then asks for remaining plant-specific fields.

```bash
python -m commands.plant_tracking_cli create-plant
```

The interactive prompt flow:

1. **Variety identification**: Enter variety name and Latin name (required for label)
2. **Genus lookup**:
   - **Existing match found**: Confirm to use it (links genus to plant), or choose another option
   - **No match found**: Choose one of:
     - **(A) Create new genus now**: Creates the genus from your variety/Latin name, links it to the plant
     - **(B) Select existing from list**: Pick from `list-genera` output
     - **(C) Skip ("unknown")**: No genus reference; Latin name stored directly on plant
     - **(F) Fuzzy search**: Find similar genus names (tolerates typos)
3. **Plant-specific fields**: Enter planting date (required for label)

After saving, the output shows the generated plant ID, genus ID (if any), file path, and next steps for generating or printing a label.

### `create-genus`

Create a standalone genus record that can be referenced by multiple plants.

```bash
python -m commands.plant_tracking_cli create-genus
```

The interactive prompt asks for:

| Field | Example | Description |
|-------|---------|-------------|
| Variety name | Yellow Habanero | Common name of the plant variety |
| Latin name | Capsicum chinense | Scientific name |

If a matching genus already exists (same variety + Latin name), the system warns you and asks if you want to create a duplicate anyway.

### `list-genera`

Display all genus records in a table for reference during plant creation.

```bash
python -m commands.plant_tracking_cli list-genera
```

Output:
```
ID           Variety                     Latin Name
------------ -------------------------  -------------------------
GENUS-001    Yellow Habanero            Capsicum chinense
GENUS-002    Avocado                    Persea americana
```

### `show-genus <id>`

Show full details of a specific genus record.

```bash
python -m commands.plant_tracking_cli show-genus GENUS-001
```

### `print-label`

Generate and/or print a label for a plant. This command replaces the former `create-label` and `print-label` commands.

```bash
# Generate and print in one step (default: 40x30mm)
python -m commands.plant_tracking_cli print-label <plant_id>

# Generate label image only (no printing)
python -m commands.plant_tracking_cli print-label <plant_id> --no-print

# Use a different label format
python -m commands.plant_tracking_cli print-label <plant_id> --format 50x70mm

# Print an existing label file
python -m commands.plant_tracking_cli print-label database/YEHA-2026-001_label.png
```

**Options:**

| Option | Description |
|--------|-------------|
| `--format`, `-f` | Label format: `40x30mm` (default) or `50x70mm` |
| `--no-print` | Generate the label image file without sending it to the printer |

**Supported formats:**

| Format | Dimensions | Orientation |
|--------|-----------|-------------|
| `40x30mm` | 40mm × 30mm | Landscape (width along roll) |
| `50x70mm` | 50mm × 70mm | Portrait (height along roll) |

**Label layout:**

The generated label is saved to `database/<plant_id>_label.png` and contains:
- **Text column (left)**: variety name at top, plant ID and planting date in middle, Latin name at bottom
- **QR code (right)**: encodes the plant ID for scanning

The command accepts either a plant ID (generates the label first) or a direct path to an existing label PNG file.

## Plant ID Format

IDs follow the pattern `VARIETY-YYYY-SEQ`:
- **VARIETY**: First 2 letters of each word in the variety name, up to 4 characters (e.g., "Yellow Habanero" → "YEHA")
- **YYYY**: Year from planting_date
- **SEQ**: Zero-padded 3-digit sequence number (001, 002, ...)

Example: `YEHA-2026-001`

The system scans existing records in `database/` to ensure unique sequence numbers per variety per year.

## Storage Architecture

### Primary Storage: PostgreSQL

All data is stored in PostgreSQL tables managed by the `plant_service` package:

| Table | Description |
|-------|-------------|
| `plants` | Individual growing records |
| `seed_packets` | Reusable variety information |
| `genera` | Unique (variety name, Latin name) pairs |
| `plant_log_entries` | Care activity logs (humidity, water, fertilizer, notes) |

### Markdown Backup

Markdown files are automatically written as backups alongside PostgreSQL for human-readable access:

- **Plants**: `database/<plant_id>.md`
- **Seed packets**: `database/seed_packets/SPKT-NNN.md`
- **Genera**: `database/genera/GENUS-NNN.md`

**Example plant backup file**:
```yaml
---
variety_name: Yellow Habanero
latin_name: Capsicum chinense
planting_date: '2025-05-01'
seed_packet_id: SPKT-003
id: YEHA-2026-002
created_at: '2026-04-24T12:05:30Z'
updated_at: '2026-04-25T14:30:02Z'
---
```

## Database Directory Customization

Set `PLANT_DATABASE_DIR` in your `.env` file to change the Markdown backup location. This is useful for testing or organizing records across projects.

## Error Handling

The CLI provides helpful error messages:

- **Missing plant**: Shows the plant record not found message with a reminder to run `create-plant` first
- **Missing printer**: Indicates that phomemo-tools is not available in the expected location
- **Invalid input**: Re-prompts for required fields with specific guidance (e.g., "Please enter a positive number" for days to maturity)

## Troubleshooting

### QR code not scanning

Ensure the label PNG was generated without errors. The QR code encodes the plant ID, which can be verified by checking the `database/<plant_id>.md` file.

### Font rendering issues

Labels use DejaVu Sans fonts. If not found, the system falls back to the default PIL font. Install fonts for better rendering:

```bash
sudo apt-get install fonts-dejavu-core
```

### Printer not connecting

The print command requires phomemo-tools to be available at `phomemo-tools/tools/phomemo-filter.py`. Verify the path and ensure the Bluetooth printer is paired and connected.
