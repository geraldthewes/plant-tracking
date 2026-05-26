# Add plant list and show CLI commands Implementation Plan

## Overview

Implement `list-plants` and `show-plant` CLI commands to complete the list/show pattern across all entity types in the plant tracking CLI. These commands will enable users to discover plants before performing operations like logging or labeling, addressing the current limitation where users must know exact plant IDs.

## Current State Analysis

The CLI currently supports:
- `list-seed-packets` and `show-seed-packet` (lines 1099-1155 in plant_tracking_cli.py)
- `list-genera` and `show-genus` (lines 1386-1527 in plant_tracking_cli.py)
- Plant creation via `create-plant` command

The service layer already provides:
- `list_plants()` method returning `Iterator[Plant]` in plant_service.py
- `get_plant()` method returning `Plant | None` in plant_service.py
- Repository implementation in plant_repository.py that correctly implements the service interface

However, the CLI is missing the corresponding command definitions and handler functions for plants.

## Desired End State

After implementation, the CLI will have:
1. `list-plants` command that displays plants in table format (ID, Variety, Latin Name, Planting Date)
2. `show-plant <id>` command that displays all fields of a specific plant
3. Both commands will be registered in the argument parser and accessible via `--help`
4. Empty/error cases will be handled gracefully
5. All existing tests will continue to pass

### Key Discoveries:
- Service layer plant service already implements `list_plants()` and `get_plant()` (plant_service.py:21-23, 17-19)
- Repository correctly implements the service interface (plant_repository.py:62-65, 55-60)
- Existing list commands follow a consistent pattern: table output with ID, name/description columns
- Plant domain model contains all necessary fields for display (plant.py:18-32)

## What We're NOT Doing

- Implementing `update-plant` or `delete-plant` commands (out of scope per ticket)
- Adding filtering or sorting capabilities to list-plants
- Creating API/UI endpoints for plant listing
- Modifying existing plant creation or service logic

## Implementation Approach

We will follow the existing patterns established by `list-seed-packets`/`show-seed-packet` and `list-genera`/`show-genus`:
1. Add argument parser subcommands for `list-plants` and `show-plant`
2. Implement handler functions that use the service layer via unit of work
3. Follow the same table format for list-plants as existing list commands
4. Implement show-plant to display all Plant domain fields similar to show-seed-packet
5. Handle service unavailable fallback to original models and markdown storage
6. Ensure proper error handling for missing plants

## Phase 1: Add list-plants command

### Overview
Implement the `list-plants` command to display all plants in a table format matching the existing list commands.

### Changes Required:

#### 1. CLI Argument Parser
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add subcommand parser for list-plants

```python
    # list-plants subcommand
    subparsers.add_parser("list-plants", help="List all plants")
```

#### 2. Command Handler Function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add list_plants function following the pattern of list_seed_packets

```python
def list_plants(args, db=None):
    """List all plants in a table format."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plants = list(uow.plants.list_plants())
        except Exception:
            # Fallback to original models if service fails
            if db:
                from .models import Plant

                plants = Plant.list_all()
            else:
                from .plant_model import list_all

                plants = list_all()
    elif db:
        # Fallback to original models
        from .models import Plant

        plants = Plant.list_all()
    else:
        # Markdown fallback
        from .plant_model import list_all

        plants = list_all()

    if not plants:
        print("No plants found.")
        return

    header = f"{'ID':<12} {'Variety':<25} {'Latin Name':<25} {'Planting Date':<15}"
    separator = f"{'-' * 12}  {'-' * 25}  {'-' * 25}  {'-' * 15}"
    print(header)
    print(separator)
    for p in plants:
        if db and SERVICE_AVAILABLE:
            pid = p.id
            variety = p.variety_name
            latin = p.latin_name
            planting_date = p.planting_date
        elif db:
            # Fallback to original models
            pid = p.id
            variety = p.variety_name
            latin = p.latin_name
            planting_date = p.planting_date
        else:
            # Markdown fallback
            pid = p.data["id"]
            variety = p.data["variety_name"]
            latin = p.data["latin_name"]
            planting_date = p.data["planting_date"]
        print(
            f"{pid:<12} {variety:<25} {latin:<25} {planting_date:<15}"
        )
```

#### 3. Command Dispatch
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add elif branch in main() function

```python
    elif args.command == "list-plants":
        list_plants(args, db)
```

### Success Criteria:

#### Automated Verification:
- [x] New command appears in `--help` output
- [x] Unit tests pass: `python -m pytest tests/test_plant_tracking.py -v`
- [x] Type checking passes: `mypy commands/plant_tracking_cli.py`
- [x] Linting passes: `flake8 commands/plant_tracking_cli.py`

#### Manual Verification:
- [x] `plant-tracking list-plants` shows table with headers when plants exist
- [x] `plant-tracking list-plants` shows "No plants found." when no plants exist
- [x] Table format matches existing list commands (ID, Variety, Latin Name, Planting Date)
- [x] Data correctly populates from service layer when available

---

## Phase 2: Add show-plant command

### Overview
Implement the `show-plant <id>` command to display all fields of a specific plant.

### Changes Required:

#### 1. CLI Argument Parser
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add subcommand parser for show-plant

```python
    # show-plant subcommand
    show_plant_parser = subparsers.add_parser(
        "show-plant", help="Show plant details"
    )
    show_plant_parser.add_argument("plant_id", help="Plant ID")
```

#### 2. Command Handler Function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add show_plant function following the pattern of show_seed_packet

```python
def show_plant(args, db=None):
    """Show full details of a plant."""
    if db is None:
        db = _get_db()

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                plant = uow.plants.get_plant(args.plant_id)
                if not plant:
                    print(f"✗ Plant not found: {args.plant_id}")
                    sys.exit(1)
                    return

                print(f"=== Plant: {plant.id} ===")
                print()
                fields_to_show = [
                    ("variety_name", "Variety"),
                    ("latin_name", "Latin Name"),
                    ("brand", "Brand"),
                    ("days_to_maturity", "Days to Maturity"),
                    ("germination_time", "Germination Time"),
                    ("planting_depth", "Planting Depth"),
                    ("spacing", "Spacing"),
                    ("sun_requirements", "Sun Requirements"),
                    ("indoor_start_time", "Indoor Start Time"),
                    ("planting_date", "Planting Date"),
                    ("seed_packet_id", "Seed Packet ID"),
                    ("genus_id", "Genus ID"),
                ]
                for field, label in fields_to_show:
                    val = getattr(plant, field, None)
                    if val:
                        print(f"  {label:<22} {val}")
                print()
                if plant.created_at:
                    print(f"  Created: {plant.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
                if plant.updated_at:
                    print(f"  Updated: {plant.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        except Exception as e:
            print(f"✗ Error showing plant: {e}")
            sys.exit(1)
    elif db:
        # Fallback to original models
        from .models import Plant

        with db.get_db() as session:
            plant = session.query(Plant).filter_by(id=args.plant_id).first()

        if not plant:
            print(f"✗ Plant not found: {args.plant_id}")
            sys.exit(1)
            return

        print(f"=== Plant: {plant.id} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
            ("brand", "Brand"),
            ("days_to_maturity", "Days to Maturity"),
            ("germination_time", "Germination Time"),
            ("planting_depth", "Planting Depth"),
            ("spacing", "Spacing"),
            ("sun_requirements", "Sun Requirements"),
            ("indoor_start_time", "Indoor Start Time"),
            ("planting_date", "Planting Date"),
            ("seed_packet_id", "Seed Packet ID"),
            ("genus_id", "Genus ID"),
        ]
        for field, label in fields_to_show:
            val = getattr(plant, field, None)
            if val:
                print(f"  {label:<22} {val}")
        print()
        if plant.created_at:
            print(f"  Created: {plant.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        if plant.updated_at:
            print(f"  Updated: {plant.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    else:
        # Markdown fallback
        from .plant_model import load_plant_from_file

        filepath = get_database_dir() / f"{args.plant_id}.md"
        if not filepath.exists():
            print(f"✗ Plant not found: {args.plant_id}")
            sys.exit(1)
            return

        plant = load_plant_from_file(filepath)
        print(f"=== Plant: {plant.data['id']} ===")
        print()
        fields_to_show = [
            ("variety_name", "Variety"),
            ("latin_name", "Latin Name"),
            ("brand", "Brand"),
            ("days_to_maturity", "Days to Maturity"),
            ("germination_time", "Germination Time"),
            ("planting_depth", "Planting Depth"),
            ("spacing", "Spacing"),
            ("sun_requirements", "Sun Requirements"),
            ("indoor_start_time", "Indoor Start Time"),
            ("planting_date", "Planting Date"),
            ("seed_packet_id", "Seed Packet ID"),
            ("genus_id", "Genus ID"),
        ]
        for field, label in fields_to_show:
            val = plant.data.get(field)
            if val:
                print(f"  {label:<22} {val}")
        print()
        print(f"  Created: {plant.data.get('created_at', 'N/A')}")
        print(f"  Updated: {plant.data.get('updated_at', 'N/A')}")
```

#### 3. Command Dispatch
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add elif branch in main() function

```python
    elif args.command == "show-plant":
        show_plant(args, db)
```

### Success Criteria:

#### Automated Verification:
- [x] New command appears in `--help` output
- [x] Unit tests pass: `python -m pytest tests/test_plant_tracking.py -v`
- [x] Type checking passes: `mypy commands/plant_tracking_cli.py`
- [x] Linting passes: `flake8 commands/plant_tracking_cli.py`

#### Manual Verification:
- [x] `plant-tracking show-plant <valid-id>` shows all plant fields
- [x] `plant-tracking show-plant <invalid-id>` shows error message and exits with code 1
- [x] Field labels and values align properly in output
- [x] Timestamps are displayed when available
- [x] Works correctly with service layer, fallback models, and markdown storage

---

## Testing Strategy

### Unit Tests:
- Test list-plants with no plants, single plant, and multiple plants
- Test show-plant with valid plant ID, invalid plant ID
- Test fallback paths when service unavailable
- Verify table formatting matches existing list commands
- Verify field display matches existing show commands

### Integration Tests:
- End-to-end testing of plant creation → listing → showing
- Verify data persistence across storage layers
- Test error conditions and edge cases

### Manual Testing Steps:
1. Create a test plant using `create-plant`
2. Run `plant-tracking list-plants` and verify the plant appears in the table
3. Run `plant-tracking show-plant <plant-id>` and verify all fields display correctly
4. Test with no plants existing - list-plants should show "No plants found."
5. Test with invalid plant ID - show-plant should show error and exit
6. Verify both commands appear in `plant-tracking --help`

## Performance Considerations

- The list-plants command uses iterator pattern via service layer for efficient streaming
- No significant performance impact expected as plant counts are typically small
- Follows same patterns as existing list commands which perform adequately

## Migration Notes

No data migration required as we're only adding read-only commands that use existing service layer methods.

## References

- Original ticket: `knowledge/tickets/PROJ-0009.md`
- List seed packets implementation: `commands/plant_tracking_cli.py:1099-1155`
- List genera implementation: `commands/plant_tracking_cli.py:1386-1442`
- Show seed packet implementation: `commands/plant_tracking_cli.py:1156-1260`
- Show genus implementation: `commands/plant_tracking_cli.py:1445-1527`
- Plant service interface: `packages/plant_service/src/plant_service/service_layer/plant_service.py:21-23`
- Plant repository implementation: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py:62-65`