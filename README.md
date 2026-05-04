# Plant Tracking CLI

CLI tool for tracking plants, seed packets, and genera with automatic QR code label generation for thermal label printers.

## Features

- Track plants with unique IDs, planting dates, and metadata
- Manage seed packets with fuzzy-matching search
- Organize plants by genus
- Generate QR code labels for Phomemo M120 thermal label printer
- Fuzzy matching for plant and seed packet lookups

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [just](https://github.com/casey/just) (for build commands)
- Phomemo M120 printer (optional, for label printing)

## Installation

```bash
# Quick install
just install

# Install with test dependencies
just install-test
```

Or manually with uv:

```bash
uv pip install -e ".[test]"
```

## Usage

```bash
# Via uv run
uv run plant-tracking --help

# Or after installation
plant-tracking --help
```

### Commands

- `plant-tracking create-plant` — Create a new plant record
- `plant-tracking print-label` — Generate QR code labels for printing
- `plant-tracking create-seed-packet` — Create a new seed packet record
- `plant-tracking list-seed-packets` — List all seed packets
- `plant-tracking show-seed-packet` — Show seed packet details
- `plant-tracking create-genus` — Create a new genus record
- `plant-tracking list-genera` — List all genera
- `plant-tracking show-genus` — Show genus details
- `plant-tracking log` — Log plant care activities

### Activity Logging

Track plant care activities with the `log` command:

```bash
# Log humidity reading
plant-tracking log <plant-id> humidity --level 6 [--date YYYY-MM-DD]

# Log watering event
plant-tracking log <plant-id> water --amount 4qt [--date YYYY-MM-DD]

# Log fertilizer application
plant-tracking log <plant-id> fertilizer --type Tomorite --strength 1/2 [--date YYYY-MM-DD]

# Log a note
plant-tracking log <plant-id> note --text "Leaves look yellowish" [--date YYYY-MM-DD]

# List all logs for a plant
plant-tracking log <plant-id> list [--type humidity|water|fertilizer|note|all]
```

**Examples:**
```bash
# Log today's humidity reading
plant-tracking log YEHA-2026-001 humidity --level 6

# Log yesterday's watering
plant-tracking log YEHA-2026-001 water --amount 2L --date 2026-05-03

# Log fertilizer with fraction strength
plant-tracking log YEHA-2026-001 fertilizer --type Tomorite --strength 1/2

# List all humidity logs for a plant
plant-tracking log YEHA-2026-001 list --type humidity

# List all logs for a plant
plant-tracking log YEHA-2026-001 list
```

**Supported water units:** ml, L, qt, cups, tsp, tbsp, oz, fl oz
**Humidity level:** Integer from 1-10
**Date format:** YYYY-MM-DD (defaults to today if omitted)

## Development

```bash
# Run all checks (lint, format, type-check, security, tests)
just check

# Individual checks
just lint          # Ruff linter
just format        # Black formatter
just type-check    # MyPy type checking
just security-scan # Bandit security scan
just test          # Pytest
just clean         # Remove caches
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `qrcode[pil]` | QR code generation |
| `Pillow` | Image processing |
| `PyYAML` | Configuration files |
| `pyusb` | USB printer communication |
| `thefuzz[speedup]` | Fuzzy string matching |
| `pytest` | Testing (optional) |

## Project Structure

```
.
├── commands/              # CLI application code
│   ├── plant_tracking_cli.py   # Main entry point
│   ├── plant_model.py      # Plant data model
│   ├── plant_log_model.py  # Activity log data model
│   ├── seed_packet_model.py  # Seed packet data model
│   ├── genus_model.py      # Genus data model
│   ├── label_generator.py  # QR code label generation
│   ├── label_format.py     # Label formatting
│   └── printer.py          # Printer interface
├── database/              # Plant records and generated labels
├── phomemo-tools/         # Phomemo CUPS driver (third-party)
├── scripts/               # Data migration scripts
├── tests/                 # Test suite
├── Justfile               # Build commands
└── pyproject.toml         # Project metadata and dependencies
```

## Phomemo M120 Printer Setup

See [docs/PRINTER_SETUP.md](docs/PRINTER_SETUP.md) for detailed CUPS driver installation and printer configuration.

Quick summary:
1. Install `phomemo-tools` CUPS driver from the `phomemo-tools/` directory
2. Configure CUPS with the M120 PPD
3. Generate and print labels with `plant-tracking label`

## License

MIT
