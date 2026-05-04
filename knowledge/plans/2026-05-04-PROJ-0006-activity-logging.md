# Activity Logging Implementation Plan

## Overview

This plan implements activity log tracking for plants in the plant-tracking CLI system. Users will be able to log humidity, watering, fertilizer applications, and notes against individual plants, with all entries stored in a single consolidated YAML-formatted log file. The feature includes a new `plant-tracking log` command with subcommands for each activity type and a list command to view logs.

## Current State Analysis

The plant-tracking CLI currently supports:
- Plant records (`create-plant`)
- Seed packet records (`create-seed-packet`, `list-seed-packets`, `show-seed-packet`)
- Genus records (`create-genus`, `list-genera`, `show-genus`)
- Label generation and printing

All records use a one-file-per-record pattern with YAML frontmatter for structured data storage. There is no existing activity logging functionality.

Key files to reference:
- CLI structure: `commands/plant_tracking_cli.py`
- Data models: `commands/plant_model.py`, `commands/seed_packet_model.py`, `commands/genus_model.py`
- Test patterns: `tests/test_plant_tracking.py`
- Database directory: `database/` (with subdirectories `seed_packets/` and `genera/`)

## Desired End State

After implementation, users will be able to:
1. Log humidity readings: `plant-tracking log <plant-id> humidity --level 6 [--date YYYY-MM-DD]`
2. Log watering events: `plant-tracking log <plant-id> water --amount 4qt [--date YYYY-MM-DD]`
3. Log fertilizer applications: `plant-tracking log <plant-id> fertilizer --type Tomorite --strength 1/2 [--date YYYY-MM-DD]`
4. Log notes: `plant-tracking log <plant-id> note --text "Leaves look yellowish" [--date YYYY-MM-DD]`
5. List all logs for a plant: `plant-tracking log <plant-id> list` (with optional `--type` filter)

All log entries will be stored in `database/logs/plant-activity-log.md` using YAML format with entries containing:
- plant_id
- event_type (humidity, water, fertilizer, note)
- timestamp (ISO 8601)
- event-specific fields
- date (YYYY-MM-DD, defaults to today)

## Key Discoveries

- **CLI Pattern**: The CLI uses argparse with single-level subparsers. Adding nested subcommands requires creating a parent `log` parser with child subparsers for each activity type.
- **Storage Pattern**: All existing models use one-file-per-record with YAML frontmatter. The activity log breaks this pattern by storing multiple entries in a single file.
- **YAML Handling**: PyYAML is already a dependency and used throughout the codebase for frontmatter serialization.
- **Validation**: Existing validation patterns check required fields, ID formats, and date formats.
- **Testing**: Tests use temporary directories with environment variable overrides for isolation.

## What We're NOT Doing

- Edit/delete existing log entries (deferred to future work)
- Database migration (though design is migration-friendly)
- Log aggregation/analytics dashboards
- Notifications or reminders
- CSV export (nice-to-have, deferred)
- Complex filtering beyond basic type filtering

## Implementation Approach

We'll implement the feature in phases:
1. Create the log model and storage mechanism
2. Implement the CLI command structure with nested subparsers
3. Implement each log type handler with validation
4. Implement the list command with optional filtering
5. Add unit tests following existing patterns
6. Update README documentation

## Phase 1: Log Model and Storage

### Overview
Create the data model and storage layer for activity logs, including the consolidated file format and basic CRUD operations.

### Changes Required

#### 1. New Model File: `commands/plant_log_model.py`
**File**: `commands/plant_log_model.py`
**Changes**: Create new model class for handling activity log entries

```python
"""
Activity log data model and storage
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

LOG_FILE_NAME = "plant-activity-log.md"

def get_logs_dir() -> Path:
    """Get the logs directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database")) / "logs"

def get_log_file_path() -> Path:
    """Get the full path to the activity log file."""
    return get_logs_dir() / LOG_FILE_NAME

class PlantLogEntry:
    """Represents a single activity log entry"""
    
    VALID_EVENT_TYPES = {'humidity', 'water', 'fertilizer', 'note'}
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
        if 'timestamp' not in self.data:
            self.data['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def validate(self):
        """Validate log entry data"""
        # Required fields
        required_fields = ['plant_id', 'event_type']
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate event_type
        if self.data['event_type'] not in self.VALID_EVENT_TYPES:
            raise ValueError(f"Invalid event_type: {self.data['event_type']}. Must be one of {self.VALID_EVENT_TYPES}")
        
        # Validate plant_id format (basic check)
        if not isinstance(self.data['plant_id'], str) or not self.data['plant_id']:
            raise ValueError("plant_id must be a non-empty string")
        
        # Validate timestamp format if provided
        if 'timestamp' in self.data and self.data['timestamp']:
            try:
                datetime.strptime(self.data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                raise ValueError("timestamp must be in YYYY-MM-DDTHH:MM:SSZ format")
        
        # Event-specific validation
        event_type = self.data['event_type']
        if event_type == 'humidity':
            if 'level' not in self.data:
                raise ValueError("Missing required field: level for humidity event")
            try:
                level = int(self.data['level'])
                if level < 1 or level > 10:
                    raise ValueError("Humidity level must be between 1 and 10")
            except ValueError:
                raise ValueError("Humidity level must be an integer between 1 and 10")
                
        elif event_type == 'water':
            if 'amount' not in self.data:
                raise ValueError("Missing required field: amount for water event")
            # Amount validation will be handled by normalize_water_amount function
            
        elif event_type == 'fertilizer':
            if 'type' not in self.data:
                raise ValueError("Missing required field: type for fertilizer event")
            if 'strength' not in self.data:
                raise ValueError("Missing required field: strength for fertilizer event")
                
        elif event_type == 'note':
            if 'text' not in self.data:
                raise ValueError("Missing required field: text for note event")
    
    def to_yaml_entry(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for YAML storage"""
        return self.data.copy()

def normalize_water_amount(amount_str: str) -> Dict[str, Any]:
    """
    Normalize water amount string to standard format.
    Returns dict with 'value' (float in ml) and 'unit' (normalized unit string).
    Supports: ml, L, qt, cups, tsp, tbsp, oz, fl oz
    """
    # Parse amount string (e.g., "4qt", "1 L", "500ml")
    match = re.match(r'^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)\s*$', amount_str.strip())
    if not match:
        raise ValueError(f"Invalid water amount format: {amount_str}")
    
    value = float(match.group(1))
    unit = match.group(2).strip().lower()
    
    # Convert to milliliters for storage
    unit_conversion = {
        'ml': 1,
        'milliliter': 1,
        'milliliters': 1,
        'l': 1000,
        'liter': 1000,
        'liters': 1000,
        'qt': 946.353,  # US quart
        'quart': 946.353,
        'quarts': 946.353,
        'cup': 236.588,  # US cup
        'cups': 236.588,
        'tsp': 4.92892,  # US teaspoon
        'teaspoon': 4.92892,
        'teaspoons': 4.92892,
        'tbsp': 14.7868,  # US tablespoon
        'tablespoon': 14.7868,
        'tablespoons': 14.7868,
        'oz': 29.5735,   # US fluid ounce
        'fluid ounce': 29.5735,
        'fluid ounces': 29.5735,
        'fl oz': 29.5735
    }
    
    if unit not in unit_conversion:
        raise ValueError(f"Unsupported water unit: {unit}. Supported units: ml, L, qt, cups, tsp, tbsp, oz, fl oz")
    
    value_ml = value * unit_conversion[unit]
    
    return {
        'value_ml': value_ml,
        'display_value': value,
        'display_unit': unit
    }

def ensure_log_file_exists():
    """Ensure the log file and directory exist"""
    logs_dir = get_logs_dir()
    logs_dir.mkdir(exist_ok=True)
    
    log_file = get_log_file_path()
    if not log_file.exists():
        # Create initial file with header
        with open(log_file, 'w') as f:
            f.write("# Plant Activity Log\n\n*Consolidated log of all plant care activities*\n\n---\n")

def append_log_entry(entry: PlantLogEntry) -> None:
    """Append a log entry to the consolidated log file"""
    ensure_log_file_exists()
    
    log_file = get_log_file_path()
    
    # Read existing content
    if log_file.exists():
        with open(log_file, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Prepare YAML entry
    entry_data = entry.to_yaml_entry()
    yaml_content = yaml.dump(entry_data, default_flow_style=False, sort_keys=False)
    
    # Append to file
    with open(log_file, 'a') as f:
        if content and not content.endswith('\n'):
            f.write('\n')
        f.write(f"---\n{yaml_content}...\n")

def load_log_entries(plant_id: Optional[str] = None, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load log entries from the consolidated log file.
    Optionally filter by plant_id and/or event_type.
    """
    log_file = get_log_file_path()
    if not log_file.exists():
        return []
    
    with open(log_file, 'r') as f:
        content = f.read()
    
    # Split by document separator
    # Format: ---\nENTRY1...\n---\nENTRY2...\n---
    if not content.strip():
        return []
    
    # Find all YAML documents (between --- and ...)
    entries = []
    parts = content.split('---\n')
    
    for part in parts[1:]:  # Skip first part (header before first ---)
        if not part.strip():
            continue
            
        # Extract YAML content (up to the ... or end)
        if '...\n' in part:
            yaml_str = part.split('...\n')[0]
        else:
            yaml_str = part
        
        try:
            entry_data = yaml.safe_load(yaml_str)
            if entry_data:  # Check if not None/empty
                # Apply filters
                if plant_id and entry_data.get('plant_id') != plant_id:
                    continue
                if event_type and entry_data.get('event_type') != event_type:
                    continue
                entries.append(entry_data)
        except yaml.YAMLError:
            # Skip invalid YAML entries
            continue
    
    # Sort by timestamp (oldest first)
    entries.sort(key=lambda x: x.get('timestamp', ''))
    return entries

def delete_log_file() -> None:
    """Delete the log file (for testing)"""
    log_file = get_log_file_path()
    if log_file.exists():
        log_file.unlink()
```

### Success Criteria:

#### Automated Verification:
- [x] PlantLogEntry validates required fields and data types
- [x] Water amount normalization works for all supported units
- [x] Log file is created when first entry is added
- [x] Log entries are properly appended to file
- [x] Log entries can be loaded and filtered correctly
- [x] Invalid data raises appropriate validation errors

#### Manual Verification:
- [ ] Log file is created in `database/logs/` directory
- [ ] Entries are stored in readable YAML format
- [ ] Different event types store correct data

---

## Phase 2: CLI Command Structure

### Overview
Add the new `log` command with nested subparsers for each activity type and implement the command dispatch logic.

### Changes Required

#### 1. Updated CLI File: `commands/plant_tracking_cli.py`
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add log command registration and handler functions

Add after existing subparser registrations (around line 70):

```python
    # log subcommand
    log_parser = subparsers.add_parser('log', help='Log plant observations')
    log_subparsers = log_parser.add_subparsers(dest='log_command', help='Log subcommands')

    # log humidity
    log_humidity_parser = log_subparsers.add_parser('humidity', help='Log humidity reading')
    log_humidity_parser.add_argument('plant_id', help='Plant ID')
    log_humidity_parser.add_argument('--level', '-l', type=int, required=True, help='Humidity level (1-10)')
    log_humidity_parser.add_argument('--date', '-d', help='Date (YYYY-MM-DD, default: today)')

    # log water
    log_water_parser = log_subparsers.add_parser('water', help='Log watering event')
    log_water_parser.add_argument('plant_id', help='Plant ID')
    log_water_parser.add_argument('--amount', '-a', required=True, help='Amount (e.g., 4qt, 1L, 500ml)')
    log_water_parser.add_argument('--date', '-d', help='Date (YYYY-MM-DD, default: today)')

    # log fertilizer
    log_fertilizer_parser = log_subparsers.add_parser('fertilizer', help='Log fertilization')
    log_fertilizer_parser.add_argument('plant_id', help='Plant ID')
    log_fertilizer_parser.add_argument('--type', '-t', required=True, help='Fertilizer type/brand')
    log_fertilizer_parser.add_argument('--strength', '-s', required=True, help='Strength/concentration (e.g., 1/2)')
    log_fertilizer_parser.add_argument('--date', '-d', help='Date (YYYY-MM-DD, default: today)')

    # log note
    log_note_parser = log_subparsers.add_parser('note', help='Log a note')
    log_note_parser.add_argument('plant_id', help='Plant ID')
    log_note_parser.add_argument('--text', '-t', required=True, help='Note text')
    log_note_parser.add_argument('--date', '-d', help='Date (YYYY-MM-DD, default: today)')

    # log list
    log_list_parser = log_subparsers.add_parser('list', help='List all logs for a plant')
    log_list_parser.add_argument('plant_id', help='Plant ID')
    log_list_parser.add_argument('--type', choices=['humidity', 'water', 'fertilizer', 'note', 'all'], 
                                default='all', help='Filter by log type')
```

Update the dispatch logic (around line 90):

```python
    elif args.command == 'log':
        if args.log_command == 'humidity':
            log_humidity(args)
        elif args.log_command == 'water':
            log_water(args)
        elif args.log_command == 'fertilizer':
            log_fertilizer(args)
        elif args.log_command == 'note':
            log_note(args)
        elif args.log_command == 'list':
            log_list(args)
        else:
            log_parser.print_help()
```

Add handler functions at the end of the file:

```python
def log_humidity(args):
    """Log a humidity reading for a plant."""
    from .plant_log_model import PlantLogEntry, get_log_file_path
    from .plant_model import load_plant_from_file, get_database_dir
    
    # Validate plant exists
    plant_file = get_database_dir() / f"{args.plant_id}.md"
    if not plant_file.exists():
        print(f"\u2717 Error: Plant ID '{args.plant_id}' not found")
        return
    
    # Create log entry
    entry_data = {
        'plant_id': args.plant_id,
        'event_type': 'humidity',
        'level': args.level
    }
    
    if args.date:
        entry_data['date'] = args.date
    
    try:
        entry = PlantLogEntry(entry_data)
        append_log_entry(entry)
        print(f"\u2713 Humidity logged for plant {args.plant_id}")
    except ValueError as e:
        print(f"\u2717 Error: {e}")

def log_water(args):
    """Log a watering event."""
    from .plant_log_model import PlantLogEntry, normalize_water_amount, get_log_file_path
    from .plant_model import load_plant_from_file, get_database_dir
    
    # Validate plant exists
    plant_file = get_database_dir() / f"{args.plant_id}.md"
    if not plant_file.exists():
        print(f"\u2717 Error: Plant ID '{args.plant_id}' not found")
        return
    
    # Normalize water amount
    try:
        water_data = normalize_water_amount(args.amount)
    except ValueError as e:
        print(f"\u2717 Error: Invalid water amount: {e}")
        return
    
    # Create log entry
    entry_data = {
        'plant_id': args.plant_id,
        'event_type': 'water',
        'amount_ml': water_data['value_ml'],
        'amount_display': f"{water_data['display_value']} {water_data['display_unit']}"
    }
    
    if args.date:
        entry_data['date'] = args.date
    
    try:
        entry = PlantLogEntry(entry_data)
        append_log_entry(entry)
        print(f"\u2713 Watering logged for plant {args.plant_id}")
    except ValueError as e:
        print(f"\u2717 Error: {e}")

def log_fertilizer(args):
    """Log a fertilization event."""
    from .plant_log_model import PlantLogEntry, get_log_file_path
    from .plant_model import load_plant_from_file, get_database_dir
    
    # Validate plant exists
    plant_file = get_database_dir() / f"{args.plant_id}.md"
    if not plant_file.exists():
        print(f"\u2717 Error: Plant ID '{args.plant_id}' not found")
        return
    
    # Create log entry
    entry_data = {
        'plant_id': args.plant_id,
        'event_type': 'fertilizer',
        'type': args.type,
        'strength': args.strength
    }
    
    if args.date:
        entry_data['date'] = args.date
    
    try:
        entry = PlantLogEntry(entry_data)
        append_log_entry(entry)
        print(f"\u2713 Fertilizer logged for plant {args.plant_id}")
    except ValueError as e:
        print(f"\u2717 Error: {e}")

def log_note(args):
    """Log a note for a plant."""
    from .plant_log_model import PlantLogEntry, get_log_file_path
    from .plant_model import load_plant_from_file, get_database_dir
    
    # Validate plant exists
    plant_file = get_database_dir() / f"{args.plant_id}.md"
    if not plant_file.exists():
        print(f"\u2717 Error: Plant ID '{args.plant_id}' not found")
        return
    
    # Create log entry
    entry_data = {
        'plant_id': args.plant_id,
        'event_type': 'note',
        'text': args.text
    }
    
    if args.date:
        entry_data['date'] = args.date
    
    try:
        entry = PlantLogEntry(entry_data)
        append_log_entry(entry)
        print(f"\u2713 Note logged for plant {args.plant_id}")
    except ValueError as e:
        print(f"\u2717 Error: {e}")

def log_list(args):
    """List all log entries for a plant."""
    from .plant_log_model import load_log_entries, get_log_file_path
    from .plant_model import load_plant_from_file, get_database_dir
    
    # Validate plant exists
    plant_file = get_database_dir() / f"{args.plant_id}.md"
    if not plant_file.exists():
        print(f"\u2717 Error: Plant ID '{args.plant_id}' not found")
        return
    
    # Determine filter
    event_type = None if args.type == 'all' else args.type
    
    # Load entries
    entries = load_log_entries(plant_id=args.plant_id, event_type=event_type)
    
    if not entries:
        print(f"No log entries found for plant {args.plant_id}")
        return
    
    # Print header
    print(f"\nLog entries for plant {args.plant_id}:")
    print("-" * 80)
    
    # Print each entry
    for entry in entries:
        timestamp = entry.get('timestamp', 'Unknown')
        # Format timestamp for display (just date part)
        display_date = timestamp.split('T')[0] if 'T' in timestamp else timestamp
        
        event_type = entry.get('event_type', 'unknown')
        date_str = f" [{entry.get('date', 'today')}]" if entry.get('date') else ""
        
        if event_type == 'humidity':
            level = entry.get('level', 'N/A')
            print(f"{display_date}{date_str} | Humidity: {level}/10")
        elif event_type == 'water':
            amount = entry.get('amount_display', 'N/A')
            print(f"{display_date}{date_str} | Water: {amount}")
        elif event_type == 'fertilizer':
            ftype = entry.get('type', 'N/A')
            strength = entry.get('strength', 'N/A')
            print(f"{display_date}{date_str} | Fertilizer: {ftype} ({strength})")
        elif event_type == 'note':
            text = entry.get('text', 'N/A')
            # Truncate long notes for display
            display_text = text[:50] + "..." if len(text) > 50 else text
            print(f"{display_date}{date_str} | Note: {display_text}")
    
    print("-" * 80)
    print(f"Total entries: {len(entries)}")
```

### Success Criteria:

#### Automated Verification:
- [x] Log command appears in help output
- [x] All subcommands (humidity, water, fertilizer, note, list) are accessible
- [x] Invalid plant IDs are rejected with clear error messages
- [x] Missing required arguments trigger appropriate error messages
- [x] Date defaults to current date when not provided
- [x] Water amount normalization works correctly

#### Manual Verification:
- [ ] `plant-tracking log` shows help for log subcommands
- [ ] Each subcommand shows its specific help when called with `--help`
- [ ] Commands work correctly with valid inputs

---

## Phase 3: Unit Tests

### Overview
Create comprehensive unit tests following the existing test patterns in `tests/test_plant_tracking.py`.

### Changes Required

#### 1. Updated Test File: `tests/test_plant_tracking.py`
**File**: `tests/test_plant_tracking.py`
**Changes**: Add test class for plant log functionality

Add at the end of the file:

```python
class TestPlantLogModel(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_logs_dir = self.test_db / "logs"
        
        # Save original and set test database
        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)
        
        # Import after setting env var so modules pick up the test dir
        from commands.plant_log_model import (
            PlantLogEntry, normalize_water_amount, ensure_log_file_exists,
            append_log_entry, load_log_entries, get_log_file_path
        )
        self.PlantLogEntry = PlantLogEntry
        self.normalize_water_amount = normalize_water_amount
        self.ensure_log_file_exists = ensure_log_file_exists
        self.append_log_entry = append_log_entry
        self.load_log_entries = load_log_entries
        self.get_log_file_path = get_log_file_path

    def tearDown(self):
        # Restore original database dir
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        
        # Clean up test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_water_amount_normalization(self):
        """Test water amount normalization to milliliters"""
        test_cases = [
            ("4qt", 3785.412),  # 4 * 946.353
            ("1L", 1000),
            ("500ml", 500),
            ("1 cup", 236.588),
            ("2 tbsp", 29.5736),  # 2 * 14.7868
            ("1 tsp", 4.92892),
            ("8 oz", 236.588),   # 8 * 29.5735
            ("1 fl oz", 29.5735),
        ]
        
        for amount_str, expected_ml in test_cases:
            with self.subTest(amount=amount_str):
                result = self.normalize_water_amount(amount_str)
                self.assertAlmostEqual(result['value_ml'], expected_ml, places=4)
                self.assertEqual(result['display_value'], float(amount_str.split()[0]) if ' ' in amount_str[:-2] else float(re.match(r'^\d+(?:\.\d+)?', amount_str).group()))
    
    def test_water_amount_normalization_invalid(self):
        """Test that invalid water amounts raise ValueError"""
        invalid_amounts = ["invalid", "4 xyz", "100", ""]
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.normalize_water_amount(amount)

    def test_plant_log_entry_creation(self):
        """Test creating valid log entries"""
        # Humidity entry
        humidity_data = {
            'plant_id': 'TEST-2026-001',
            'event_type': 'humidity',
            'level': 6
        }
        humidity_entry = self.PlantLogEntry(humidity_data)
        self.assertEqual(humidity_entry.data['plant_id'], 'TEST-2026-001')
        self.assertEqual(humidity_entry.data['event_type'], 'humidity')
        self.assertEqual(humidity_entry.data['level'], 6)
        
        # Water entry
        water_data = {
            'plant_id': 'TEST-2026-001',
            'event_type': 'water',
            'amount_ml': 500,
            'amount_display': '500 ml'
        }
        water_entry = self.PlantLogEntry(water_data)
        self.assertEqual(water_entry.data['event_type'], 'water')
        
        # Fertilizer entry
        fert_data = {
            'plant_id': 'TEST-2026-001',
            'event_type': 'fertilizer',
            'type': 'Tomorite',
            'strength': '1/2'
        }
        fert_entry = self.PlantLogEntry(fert_data)
        self.assertEqual(fert_entry.data['event_type'], 'fertilizer')
        self.assertEqual(fert_entry.data['type'], 'Tomorite')
        
        # Note entry
        note_data = {
            'plant_id': 'TEST-2026-001',
            'event_type': 'note',
            'text': 'Leaves look yellowish'
        }
        note_entry = self.PlantLogEntry(note_data)
        self.assertEqual(note_entry.data['event_type'], 'note')
        self.assertEqual(note_entry.data['text'], 'Leaves look yellowish')

    def test_plant_log_entry_validation(self):
        """Test validation of log entries"""
        # Missing plant_id
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'event_type': 'humidity', 'level': 5})
        self.assertIn('Missing required field: plant_id', str(ctx.exception))
        
        # Missing event_type
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'level': 5})
        self.assertIn('Missing required field: event_type', str(ctx.exception))
        
        # Invalid event_type
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'event_type': 'invalid', 'level': 5})
        self.assertIn('Invalid event_type', str(ctx.exception))
        
        # Invalid humidity level
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'event_type': 'humidity', 'level': 15})
        self.assertIn('Humidity level must be between 1 and 10', str(ctx.exception))
        
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'event_type': 'humidity', 'level': 'invalid'})
        self.assertIn('Humidity level must be an integer', str(ctx.exception))
        
        # Missing water amount
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'event_type': 'water'})
        self.assertIn('Missing required field: amount', str(ctx.exception))
        
        # Missing fertilizer fields
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'event_type': 'fertilizer', 'type': 'Tomorite'})
        self.assertIn('Missing required field: strength', str(ctx.exception))
        
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'event_type': 'fertilizer', 'strength': '1/2'})
        self.assertIn('Missing required field: type', str(ctx.exception))
        
        # Missing note text
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({'plant_id': 'TEST-2026-001', 'event_type': 'note'})
        self.assertIn('Missing required field: text', str(ctx.exception))

    def test_log_file_creation_and_appending(self):
        """Test that log file is created and entries are appended"""
        # Ensure clean state
        log_file = self.get_log_file_path()
        if log_file.exists():
            log_file.unlink()
        
        # Create and append first entry
        entry1_data = {
            'plant_id': 'TEST-2026-001',
            'event_type': 'humidity',
            'level': 6,
            'date': '2026-05-04'
        }
        entry1 = self.PlantLogEntry(entry1_data)
        self.append_log_entry(entry1)
        
        # Verify file exists and has content
        self.assertTrue(log_file.exists())
        with open(log_file, 'r') as f:
            content = f.read()
        self.assertIn('Plant Activity Log', content)
        self.assertIn('TEST-2026-001', content)
        self.assertIn('humidity', content)
        self.assertIn('2026-05-04', content)
        
        # Append second entry
        entry2_data = {
            'plant_id': 'TEST-2026-001',
            'event_type': 'water',
            'amount_ml': 500,
            'amount_display': '500 ml',
            'date': '2026-05-05'
        }
        entry2 = self.PlantLogEntry(entry2_data)
        self.append_log_entry(entry2)
        
        # Verify both entries are present
        with open(log_file, 'r') as f:
            content = f.read()
        # Should have two entries (separated by ---)
        self.assertEqual(content.count('---'), 3)  # Header + 2 entries
        self.assertIn('2026-05-04', content)
        self.assertIn('2026-05-05', content)

    def test_load_log_entries(self):
        """Test loading log entries with filtering"""
        # Ensure clean state
        log_file = self.get_log_file_path()
        if log_file.exists():
            log_file.unlink()
        
        # Create test entries
        entries_data = [
            {
                'plant_id': 'TEST-2026-001',
                'event_type': 'humidity',
                'level': 6,
                'date': '2026-05-01',
                'timestamp': '2026-05-01T10:00:00Z'
            },
            {
                'plant_id': 'TEST-2026-001',
                'event_type': 'water',
                'amount_ml': 500,
                'amount_display': '500 ml',
                'date': '2026-05-02',
                'timestamp': '2026-05-02T10:00:00Z'
            },
            {
                'plant_id': 'TEST-2026-001',
                'event_type': 'humidity',
                'level': 8,
                'date': '2026-05-03',
                'timestamp': '2026-05-03T10:00:00Z'
            },
            {
                'plant_id': 'TEST-2026-002',  # Different plant
                'event_type': 'humidity',
                'level': 5,
                'date': '2026-05-03',
                'timestamp': '2026-05-03T11:00:00Z'
            }
        ]
        
        for entry_data in entries_data:
            entry = self.PlantLogEntry(entry_data)
            # Override timestamp to ensure consistent ordering
            entry.data['timestamp'] = entry_data['timestamp']
            self.append_log_entry(entry)
        
        # Load all entries for plant TEST-2026-001
        entries = self.load_log_entries(plant_id='TEST-2026-001')
        self.assertEqual(len(entries), 3)  # Should have 3 entries for this plant
        
        # Load only humidity entries for plant TEST-2026-001
        humidity_entries = self.load_log_entries(plant_id='TEST-2026-001', event_type='humidity')
        self.assertEqual(len(humidity_entries), 2)  # Should have 2 humidity entries
        
        # Load entries for non-existent plant
        no_entries = self.load_log_entries(plant_id='NONEXISTENT')
        self.assertEqual(len(no_entries), 0)
        
        # Load all entries (no plant filter)
        all_entries = self.load_log_entries()
        self.assertEqual(len(all_entries), 4)  # Should have all 4 entries
        
        # Verify ordering (chronological)
        timestamps = [e['timestamp'] for e in entries]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_integration_with_plant_model(self):
        """Test that log entries work with existing plant records"""
        from commands.plant_model import Plant
        
        # Create a test plant
        plant_data = {
            'variety_name': 'Test Plant',
            'latin_name': 'Testus plantus',
            'planting_date': '2026-05-01'
        }
        plant = Plant(plant_data)
        plant_id = plant.data['id']
        
        # Save plant to test database
        from commands.plant_model import get_database_dir
        db_dir = get_database_dir()
        plant_file = db_dir / f"{plant.data['id']}.md"
        with open(plant_file, 'w') as f:
            f.write(plant.to_markdown())
        
        # Now create a log entry for this plant
        entry_data = {
            'plant_id': plant_id,
            'event_type': 'humidity',
            'level': 7
        }
        entry = self.PlantLogEntry(entry_data)
        self.append_log_entry(entry)
        
        # Verify we can load the entry
        entries = self.load_log_entries(plant_id=plant_id)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['plant_id'], plant_id)
        self.assertEqual(entries[0]['event_type'], 'humidity')
        self.assertEqual(entries[0]['level'], 7)
```

### Success Criteria:

#### Automated Verification:
- [x] All new unit tests pass (`pytest tests/test_plant_tracking.py::TestPlantLogModel`)
- [x] Water amount normalization handles all supported units correctly
- [x] Log entry validation rejects invalid data with appropriate messages
- [x] Log file creation and appending works correctly
- [x] Log loading and filtering returns correct entries
- [x] Integration with existing plant model works

#### Manual Verification:
- [ ] Tests run successfully and cover all new functionality

---

## Phase 4: Documentation Update

### Overview
Update the README.md to document the new log command and its usage.

### Changes Required

#### 1. Updated Documentation: `README.md`
**File**: `README.md`
**Changes**: Add documentation for the new log command

Add to the Commands section:

```markdown
## Commands

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
```

### Success Criteria:

#### Automated Verification:
- [x] README.md is updated with log command documentation
- [x] Documentation matches the actual command interface

#### Manual Verification:
- [ ] Documentation is clear and easy to understand
- [ ] Examples match actual command usage

---

## Testing Strategy

### Unit Tests:
- Test plant log model validation for all event types
- Test water amount normalization for all supported units
- Test log entry creation, storage, and retrieval
- Test filtering by plant ID and event type
- Test integration with existing plant model
- Test CLI command handlers with valid and invalid inputs

### Integration Tests:
- Test end-to-end command execution from CLI to storage
- Test that log entries persist correctly between command invocations
- Test error handling for non-existent plants

### Manual Testing Steps:
1. Create a test plant: `plant-tracking create-plant`
2. Log a humidity reading: `plant-tracking log <plant-id> humidity --level 6`
3. Log a watering event: `plant-tracking log <plant-id> water --amount 2qt`
4. Log a fertilizer application: `plant-tracking log <plant-id> fertilizer --type Tomorite --strength 1/2`
5. Log a note: `plant-tracking log <plant-id> note --text "New leaves emerging"`
6. List all logs: `plant-tracking log <plant-id> list`
7. List filtered logs: `plant-tracking log <plant-id> list --type water`
8. Verify entries appear correctly in the log file
9. Test date defaulting by omitting `--date` flag
10. Test invalid inputs produce appropriate error messages

## Performance Considerations

- Log file reading/writing could become slow with very large numbers of entries
- Current implementation loads entire file for each list operation
- Future optimization could include indexing or database migration
- For typical home gardening use (hundreds of entries per year), performance should be acceptable
- The single-file approach was chosen specifically to ease future database migration

## Migration Notes

The design is database-migration friendly because:
- Each log entry is a discrete YAML document
- Event type is explicitly stored for querying
- Timestamps are stored in ISO 8601 format
- Plant IDs reference existing records
- Water amounts are normalized to milliliters for consistent querying
- When migrating to a database, each YAML document can become a row in a table

## References

- Original ticket: `knowledge/tickets/PROJ-0006.md`
- Plant model reference: `commands/plant_model.py`
- Seed packet model reference: `commands/seed_packet_model.py`
- CLI pattern reference: `commands/plant_tracking_cli.py`
- Test patterns: `tests/test_plant_tracking.py`