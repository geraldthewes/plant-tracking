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

## Local development services

When the home-cluster Postgres and S3 (Ceph RGW) endpoints are unavailable, run backing services locally with Docker Compose (PostgreSQL + SeaweedFS S3 gateway).

**Prerequisites:** Docker or Podman with the compose plugin.

**Note:** Compose Postgres listens on host port **5433** to avoid conflicting with a system PostgreSQL on 5432.

```bash
# One-time manual config (templates contain placeholders only — fill in your values)
cp .env.local.template .env.local    # edit <user>, <password>, S3 keys, etc.
cp docker/seaweedfs-s3.json.template docker/seaweedfs-s3.json  # match S3 keys in .env.local
cp .env.local .env

# Start Postgres and SeaweedFS
docker compose up -d

# Create database tables (DATABASE_URL in .env must match docker-compose Postgres)
alembic upgrade head

# Install CLI and API
just install
just api-install
```

**Run the API:**

```bash
just api-run
```

**Smoke-test media upload** (requires an existing plant ID):

```bash
uv run plant-tracking media add-image <plant-id> ./test.jpg --label "dev test"
```

**Stop services:**

```bash
docker compose down          # keep data volumes
docker compose down -v       # wipe Postgres and SeaweedFS data
```

**Ports:**

| Port | Service |
|------|---------|
| 5433 | PostgreSQL (Docker; maps to 5432 in container) |
| 8333 | SeaweedFS S3 API |
| 9333 | SeaweedFS master |
| 8888 | SeaweedFS filer |
| 8080 | SeaweedFS volume |

Create [`docker/seaweedfs-s3.json`](docker/seaweedfs-s3.json) from [`docker/seaweedfs-s3.json.template`](docker/seaweedfs-s3.json.template); S3 keys must match `.env`. Set `S3_FORCE_PATH_STYLE=true` in `.env` when using SeaweedFS.

Convenience targets: `just dev-up`, `just dev-down`, `just dev-setup` (requires `.env` already configured).

## Home cluster configuration

When the home cluster is available (WireGuard `gpucluster` VPN, Consul DNS, Postgres, Ceph RGW):

```bash
cp .env.cluster.template .env.cluster   # edit all <placeholder> values
cp .env.cluster .env
alembic upgrade head
```

See [`.env.cluster.template`](.env.cluster.template). Do not set `S3_FORCE_PATH_STYLE` for Ceph RGW.

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
