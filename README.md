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

- `plant-tracking plant` — Manage individual plants
- `plant-tracking packet` — Manage seed packets
- `plant-tracking genus` — Manage genera
- `plant-tracking label` — Generate QR code labels for printing

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
