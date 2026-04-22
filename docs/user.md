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

## Commands

### `create-plant`

Create a new plant record by entering information from your seed packet. The system generates a unique ID automatically.

```bash
python -m commands.plant_tracking_cli create-plant
```

The interactive prompt is divided into two sections:

**Required fields (needed for label):**
| Field | Example | Description |
|-------|---------|-------------|
| Variety name | Yellow Habanero | Common name of the plant |
| Latin name | Capsicum chinense | Scientific name |
| Planned planting date | 2026-05-01 | Date in YYYY-MM-DD format |

**Optional record fields (not on label):**
| Field | Example | Description |
|-------|---------|-------------|
| Brand | Burpee | Seed company name |
| Days to maturity | 60-75 | Range or single value, days from planting to harvest |
| Germination time | 7-14 days | Expected germination period |
| Planting depth | 0.25 inches | Recommended depth |
| Spacing | 18 inches | Recommended plant spacing |
| Sun requirements | Full sun | Sunlight needs |
| Indoor start time | 8 weeks before last frost | When to start indoors |

The `days_to_maturity` field must be a positive integer. All record fields can be skipped by pressing Enter.

After saving, the output shows the generated plant ID and file path, plus commands to generate and print a label.

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
- `planned_planting_date`, `created_at`, `updated_at`

The `created_at` and `updated_at` fields use ISO 8601 format.

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
