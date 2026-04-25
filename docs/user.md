# User Documentation

## Installation

Install the plant tracking CLI and its dependencies:

```bash
pip install .
```

Required Python packages (installed automatically):
- `qrcode[pil]` - QR code generation
- `Pillow` - Image processing
- `PyYAML` - YAML frontmatter parsing

## Setup

The first time you run any command, a `database/` directory is created automatically in the project root. This is where all plant records are stored as individual markdown files.

## Seed Packets

A **seed packet** is a reusable record of information from a seed packet — variety name, Latin name, brand, days to maturity, germination time, and more. By storing this information once in a seed packet, you avoid re-entering the same data every time you plant a new seed of the same variety.

**Relationship**: One seed packet → many plants.

When creating a plant record, the system looks for a matching seed packet by variety name and Latin name. If found, it reuses that data instead of asking you to re-enter it.

**"Unknown" case**: If you don't have packet information available (e.g., saved seeds), choose the "unknown" option and the fields are stored directly on the plant record.

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

Create a new plant record. The system first looks up a matching seed packet, then asks for remaining plant-specific fields.

```bash
python -m commands.plant_tracking_cli create-plant
```

The interactive prompt flow:

1. **Variety identification**: Enter variety name and Latin name (required for label)
2. **Seed packet lookup**:
   - **Existing match found**: Confirm to use it (skips packet fields), or choose another option
   - **No match found**: Choose one of:
     - **(A) Create new seed packet now**: Enter packet fields, creates the packet, links it to the plant
     - **(B) Select existing from list**: Pick from `list-seed-packets` output
     - **(C) Skip ("unknown")**: No packet info available; enter fields directly on the plant
3. **Plant-specific fields**: Enter planned planting date (required for label)

After saving, the output shows the generated plant ID, seed packet ID (if any), file path, and commands to generate and print a label.

### `create-label`

Generate a 40x30mm PNG label with a QR code encoding the plant ID.

```bash
python -m commands.plant_tracking_cli create-label <plant_id>
```

Example:
```bash
python -m commands.plant_tracking_cli create-label YEHA-2026-001
```

The label is saved to `database/<plant_id>_label.png` and contains:
- **Left side**: variety name, Latin name, and planned planting date
- **Right side**: QR code encoding the plant ID
- **Bottom**: variety name and planting date

### `print-label`

Send a label to the Phomemo M120 Bluetooth printer via the phomemo-tools pipeline.

```bash
# Generate label and print in one step
python -m commands.plant_tracking_cli print-label <plant_id>

# Print an existing label file
python -m commands.plant_tracking_cli print-label database/YEHA-2026-001_label.png
```

The command accepts either a plant ID (generates the label first) or a direct path to a label PNG file.

## Plant ID Format

IDs follow the pattern `VARIETY-YYYY-SEQ`:
- **VARIETY**: First 2 letters of each word in the variety name, up to 4 characters (e.g., "Yellow Habanero" → "YEHA")
- **YYYY**: Current year
- **SEQ**: Zero-padded 3-digit sequence number (001, 002, ...)

Example: `YEHA-2026-001`

The system scans existing records in `database/` to ensure unique sequence numbers per variety per year.

## File Storage

Plant records are stored as markdown files with YAML frontmatter:

**Location**: `database/<plant_id>.md`

**Frontmatter fields**:
- `id`, `variety_name`, `latin_name`, `brand`
- `days_to_maturity`, `germination_time`, `planting_depth`
- `spacing`, `sun_requirements`, `indoor_start_time`
- `planned_planting_date`, `created_at`, `updated_at`, `seed_packet_id`

The `created_at` and `updated_at` fields use ISO 8601 format. The `seed_packet_id` field references a seed packet record (or `"unknown"` if no packet is linked).

### Seed Packet Storage

Seed packet records are stored in a separate subdirectory:

**Location**: `database/seed_packets/SPKT-NNN.md`

**Example plant file with seed packet reference**:
```yaml
---
variety_name: Yellow Habanero
latin_name: Capsicum chinense
planned_planting_date: '2025-05-01'
seed_packet_id: SPKT-003
id: YEHA-2026-002
created_at: '2026-04-24T12:05:30Z'
updated_at: '2026-04-25T14:30:02Z'
---
```

## Database Directory Customization

By default, records are stored in `database/` relative to the project root. Override with the `PLANT_DATABASE_DIR` environment variable:

```bash
PLANT_DATABASE_DIR=/path/to/db python -m commands.plant_tracking_cli create-plant
```

This is useful for testing or organizing records across projects.

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
