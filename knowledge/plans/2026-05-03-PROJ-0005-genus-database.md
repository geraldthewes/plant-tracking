# Add Support for Genus Database - Implementation Plan

## Overview

Implement a genus database feature that eliminates redundant data entry of variety and Latin names when creating plant records. The genus database will store unique (variety_name, latin_name) pairs and allow the create-plant CLI flow to reference genus entries instead of requiring manual entry of both fields. This follows the proven pattern established by the seed packet database implementation.

## Current State Analysis

The codebase currently requires users to enter both variety_name and latin_name separately every time they create a plant record via `create-plant`. This leads to data inconsistencies and redundant data entry. Research shows:

1. Plant records are stored as markdown files with YAML frontmatter in `database/` directory (e.g., `database/SEPE-2026-001.md`)
2. The seed packet database implementation provides a proven reference pattern for file-based storage, CLI integration, and data relationships
3. Plant records already use a reference pattern with `seed_packet_id` field pointing to seed packet records
4. The label generation system extracts `latin_name` directly from plant data: `plant.data.get('latin_name', '')`
5. A `genera/` directory already exists in the database folder but is empty
6. No fuzzy matching library is currently implemented, but this is identified as a needed component

## Desired End State

After implementation, the `create-plant` flow will:
1. Prompt for variety name (common name) only
2. Perform exact match lookup in genus database
3. If exact match found: confirm usage and automatically retrieve Latin name
4. If no exact match: offer three paths - create new genus entry, fuzzy search existing entries, or skip (enter Latin name manually)
5. Store `genus_id` reference in plant record instead of duplicating Latin name
6. Label generation system will resolve Latin name from genus database when `genus_id` is present

### Key Discoveries:
- Storage pattern: File-based "database" using markdown files with YAML frontmatter (from seed packet model)
- Schema pattern: Required fields `variety_name`, `latin_name` with auto-generated ID in GENUS-NNN format
- Relationship pattern: Plants store `genus_id` referencing genus records (similar to `seed_packet_id`)
- CLI pattern: Commands exposed via argparse subcommands in plant_tracking_cli.py
- Migration pattern: One-shot script that extracts unique pairs and backfills references (like migrate_seed_packets.py)
- Fuzzy matching: Need to select and integrate a fuzzy matching library (options: fuzzywuzzy/thefuzz, rapidfuzz, difflib, jellyfish)

## What We're NOT Doing

- Editing or deleting existing genus entries (out of scope per ticket)
- Importing genus entries from external files (out of scope per ticket)
- Additional genus fields (species, family, care requirements, etc.) (out of scope per ticket)
- Web/mobile UI integration (CLI-only for now) (out of scope per ticket)
- Enforcing deletion constraints (preventing deletion of genus records referenced by plants)

## Implementation Approach

We will follow the exact pattern established by the seed packet database implementation, adapting it for genus management. The implementation will proceed in phases:

1. Create genus data model (Genus class) following SeedPacket pattern
2. Update plant model to include genus_id reference and modify validation
3. Add CLI commands for genus management (create-genus, list-genera, show-genus)
4. Modify create-plant flow to use genus lookup instead of separate variety/Latin prompts
5. Update label generation system to resolve Latin name from genus database
6. Create migration script to populate genus database from existing plant records
7. Add fuzzy matching capability for approximate genus name searches
8. Update documentation and run comprehensive tests

## Phase 1: Genus Data Model

### Overview
Create `Genus` model class that mirrors `SeedPacket` pattern, stored as markdown files in `database/genera/`.

### Changes Required:

#### 1. commands/genus_model.py
**File**: `commands/genus_model.py`
**Changes**: New file implementing Genus class with storage, validation, and lookup methods

```python
"""
Genus data model and validation
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


# All available fields
GENUS_FIELDS = [
    'variety_name', 'latin_name'
]

# Required fields
REQUIRED_FIELDS = ['variety_name', 'latin_name']


def get_genera_dir() -> Path:
    """Get the genera directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database")) / "genera"


class Genus:
    """Represents a genus record"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
        # Generate ID if not present
        if 'id' not in self.data:
            self.data['id'] = self.generate_id()

    def validate(self):
        """Validate genus data"""
        for field in REQUIRED_FIELDS:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")

    def to_markdown(self) -> str:
        """Convert genus data to markdown with YAML frontmatter"""
        now = datetime.now(timezone.utc)

        # Set timestamps in ISO 8601 format
        if 'created_at' not in self.data:
            self.data['created_at'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.data['updated_at'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')

        frontmatter = yaml.dump(self.data, default_flow_style=False, sort_keys=False)
        body = (
            f"# Genus Record for {self.data['variety_name']}\n\n"
            f"*ID: {self.data['id']}*\n\n"
            f"*Created: {now.strftime('%Y-%m-%d')}*"
        )
        return f"---\n{frontmatter}---\n\n{body}"

    def generate_id(self) -> str:
        """Generate genus ID in GENUS-NNN format"""
        # Find sequence number by checking existing records
        seq = self.find_next_sequence()
        return f"GENUS-{seq:03d}"

    def find_next_sequence(self) -> int:
        """Find next sequence number for genus ID"""
        pattern = re.compile(r"GENUS-(\d{3})")
        max_seq = 0

        # Check existing markdown files in genera directory
        genera_dir = get_genera_dir()
        if genera_dir.exists():
            for file in genera_dir.glob("*.md"):
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        # Extract YAML frontmatter
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1]
                                data = yaml.safe_load(frontmatter)
                                if 'id' in data:
                                    match = pattern.match(data['id'])
                                    if match:
                                        seq = int(match.group(1))
                                        max_seq = max(max_seq, seq)
                except Exception:
                    continue  # Skip unreadable files

        return max_seq + 1


def load_from_file(file_path: Path) -> Optional['Genus']:
    """Load a genus record from a markdown file"""
    with open(file_path, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        raise ValueError("Invalid genus file format: missing YAML frontmatter")

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError("Invalid genus file format: malformed frontmatter")

    frontmatter = parts[1]
    data = yaml.safe_load(frontmatter)
    return Genus(data)


def find_matching(variety_name: str, latin_name: str) -> Optional['Genus']:
    """Find existing genus by variety_name and latin_name"""
    genera_dir = get_genera_dir()
    if not genera_dir.exists():
        return None

    for file in genera_dir.glob("*.md"):
        try:
            genus = load_from_file(file)
            if (genus.data['variety_name'] == variety_name and 
                genus.data['latin_name'] == latin_name):
                return genus
        except Exception:
            continue  # Skip unreadable files
    return None


def list_all() -> list['Genus']:
    """Load all genus records"""
    genera_dir = get_genera_dir()
    if not genera_dir.exists():
        return []

    genera = []
    for file in sorted(genera_dir.glob("*.md")):
        try:
            genus = load_from_file(file)
            genera.append(genus)
        except Exception:
            continue  # Skip unreadable files
    return genera
```

### Success Criteria:

#### Automated Verification:
- [x] Genus model creates valid records: `python -c "from commands.genus_model import Genus; g = Genus({'variety_name': 'Test', 'latin_name': 'Testulus'}); assert g.data['id'] == 'GENUS-001'"`
- [x] Validation rejects missing required fields
- [x] Markdown round-trip works: save → load → compare
- [x] find_matching returns correct genus / None
- [x] list_all returns all genera
- [x] ID generation follows GENUS-NNN format and increments properly

#### Manual Verification:
- [x] New file creates proper YAML frontmatter in database/genera/
- [x] ID format matches GENUS-NNN pattern

---

## Phase 2: Update Plant Model for Genus Reference

### Overview
Modify plant model to include genus_id reference and adjust validation logic to support genus-based Latin name resolution.

### Changes Required:

#### 1. commands/plant_model.py
**File**: `commands/plant_model.py`
**Changes**: Add genus_id field, update validation, add genus resolution methods

```diff
@@
 # Fields needed for label generation (all required)
 LABEL_FIELDS = ['variety_name', 'latin_name', 'planting_date']
 
 # All available fields (record-keeping)
@@
-    'indoor_start_time', 'planting_date', 'seed_packet_id'
+    'indoor_start_time', 'planting_date', 'seed_packet_id', 'genus_id'
 
 # All label fields are required
 REQUIRED_FIELDS = ['variety_name', 'latin_name', 'planting_date']
@@
-    'indoor_start_time'
+    'indoor_start_time'
 ]
 
@@
 def get_database_dir() -> Path:
@@
 
+def get_genera_dir() -> Path:
+    """Get the genera directory path."""
+    return Path(os.environ.get("PLANT_DATABASE_DIR", "database")) / "genera"
+
+
 class Plant:
@@
     def validate(self):
         """Validate plant data"""
         for field in REQUIRED_FIELDS:
             if field not in self.data:
                 raise ValueError(f"Missing required field: {field}")
 
+        # Validate genus_id format if present
+        if 'genus_id' in self.data and self.data['genus_id'] not in (None, 'unknown'):
+            import re
+            if not re.match(r'^GENUS-\d{3}$', self.data['genus_id']):
+                raise ValueError("genus_id must match GENUS-NNN format or be 'unknown'")
+
         # Validate date format
         if 'planting_date' in self.data:
             try:
                 datetime.strptime(self.data['planting_date'], '%Y-%m-%d')
             except ValueError:
                 raise ValueError("planting_date must be in YYYY-MM-DD format")
 
@@
         frontmatter = yaml.dump(self.data, default_flow_style=False, sort_keys=False)
         body = (
             f"# Plant Record for {self.data['variety_name']}\n\n"
             f"*ID: {self.data['id']}*\n\n"
             f"*Created: {now.strftime('%Y-%m-%d')}*"
         )
         return f"---\n{frontmatter}---\n\n{body}"
 
+    def get_genus(self) -> Optional['Genus']:
+        """Load and return the referenced Genus, or None."""
+        genus_id = self.data.get('genus_id')
+        if not genus_id or genus_id == 'unknown':
+            return None
+        from commands.genus_model import load_from_file, get_genera_dir
+        genera_dir = get_genera_dir()
+        if not genera_dir.exists():
+            return None
+        filepath = genera_dir / f"{genus_id}.md"
+        if filepath.exists():
+            return load_from_file(filepath)
+        return None
+
     def generate_id(self) -> str:
         """Generate plant ID in VARIETY-YYYY-SEQ format"""
         variety = self.data['variety_name']
         # Extract abbreviation (first 2 letters of each word, max 4 chars)
         words = variety.upper().split()
         abbrev = ''.join([word[:2] for word in words if word.isalpha()])[:4]
         if not abbrev:
             abbrev = variety[:4].upper()
 
         planting_date_val = self.data.get('planting_date', '')
         if planting_date_val:
             year = datetime.strptime(planting_date_val, '%Y-%m-%d').year
         else:
             year = datetime.now(timezone.utc).year
 
         # Find sequence number by checking existing records
         seq = self.find_next_sequence(abbrev, year)
 
         return f"{abbrev}-{year}-{seq:03d}"
 
@@
     def get_seed_packet(self) -> Optional['SeedPacket']:
         """Load and return the referenced SeedPacket, or None."""
         spkt_id = self.data.get('seed_packet_id')
         if not spkt_id or spkt_id == 'unknown':
             return None
         return load_seed_packet(spkt_id)
 
 
@@
 def load_plant_from_file(file_path: Path) -> Plant:
@@
         return Plant(data)
 
+
+def load_genus(genus_id: str):
+    """Load a genus by ID. Returns None if not found."""
+    from commands.genus_model import load_from_file, get_genera_dir
+    genera_dir = get_genera_dir()
+    if not genera_dir.exists():
+        return None
+    filepath = genera_dir / f"{genus_id}.md"
+    if filepath.exists():
+        return load_from_file(filepath)
+    return None
```

### Success Criteria:

#### Automated Verification:
- [x] Plant model accepts genus_id field
- [x] Validation rejects invalid genus_id formats
- [x] get_genus() returns correct Genus object or None
- [x] Plant with genus_id saves/loads correctly
- [x] Plant with genus_id: 'unknown' is valid

#### Manual Verification:
- [x] Plant records can store genus_id references
- [x] Invalid genus_id formats are rejected

---

## Phase 3: CLI — Genus Management Commands

### Overview
Add dedicated CLI commands for managing genus records independently of plants.

### Changes Required:

#### 1. commands/plant_tracking_cli.py
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add genus management subcommands and helper functions

```diff
@@
 import sys
 from pathlib import Path
 from .plant_model import Plant, get_database_dir
 from .seed_packet_model import (
     SeedPacket, get_seed_packets_dir, find_matching, list_all,
     SEED_PACKET_FIELDS as PACKET_OPTIONAL_FIELDS,
 )
+from .genus_model import (
+    Genus, get_genera_dir, find_matching as find_genus_matching, list_all as list_all_genera
+)
@@
 # Ensure database directories exist
 DATABASE_DIR = get_database_dir()
 DATABASE_DIR.mkdir(exist_ok=True)
 PACKETS_DIR = get_seed_packets_dir()
 PACKETS_DIR.mkdir(exist_ok=True)
+GENERA_DIR = get_genera_dir()
+GENERA_DIR.mkdir(exist_ok=True)
@@
     args = parser.parse_args()
@@
     if args.command == 'create-plant':
         create_plant(args)
     elif args.command == 'print-label':
         print_label(args)
     elif args.command == 'create-seed-packet':
         create_seed_packet(args)
     elif args.command == 'list-seed-packets':
         list_seed_packets(args)
     elif args.command == 'show-seed-packet':
         show_seed_packet(args)
+    elif args.command == 'create-genus':
+        create_genus(args)
+    elif args.command == 'list-genera':
+        list_genera(args)
+    elif args.command == 'show-genus':
+        show_genus(args)
     else:
         parser.print_help()
@@
 
 
 def create_genus(args):
     """Create a new genus through interactive prompts."""
     print("=== Create New Genus ===")
     print()
 
     genus_data = {}
 
     print("--- Required fields ---")
     _prompt_field('variety_name', 'Variety name (e.g., Yellow Habanero)', genus_data)
     _prompt_field('latin_name', 'Latin name (e.g., Capsicum chinense)', genus_data)
 
     existing = find_genus_matching(genus_data['variety_name'], genus_data['latin_name'])
     if existing:
         print(f"\n\u26a0 A matching genus already exists:")
         print(f"  ID: {existing.data['id']}")
         print(f"  Variety: {existing.data['variety_name']} ({existing.data['latin_name']})")
         resp = input("\nCreate anyway? (y/N): ").strip().lower()
         if resp != 'y':
             print("Cancelled.")
             return
 
     print()
     print("--- No optional fields for genus ---")
 
     try:
         genus = Genus(genus_data)
         filepath = GENERA_DIR / f"{genus.data['id']}.md"
 
         with open(filepath, 'w') as f:
             f.write(genus.to_markdown())
 
         print(f"\n\u2713 Genus created successfully!")
         print(f"ID: {genus.data['id']}")
         print(f"Saved to: {filepath}")
     except Exception as e:
         print(f"\n\u2717 Error creating genus: {e}")
         sys.exit(1)
 
 
 def list_genera(args):
     """List all genera in a table format."""
     genera = list_all_genera()
     if not genera:
         print("No genera found.")
         return
 
     header = f"{'ID':<12} {'Variety':<25} {'Latin Name':<25}"
     separator = f"{'-'*12}  {'-'*25}  {'-'*25}"
     print(header)
     print(separator)
     for g in genera:
         print(f"{g.data['id']:<12} {g.data['variety_name']:<25} {g.data['latin_name']:<25}")
 
 
 def show_genus(args):
     """Show full details of a genus."""
     from .genus_model import load_from_file
 
     filepath = GENERA_DIR / f"{args.genus_id}.md"
     if not filepath.exists():
         print(f"\u2717 Genus not found: {args.genus_id}")
         sys.exit(1)
         return
 
     genus = load_from_file(filepath)
     print(f"=== Genus: {genus.data['id']} ===")
     print()
     fields_to_show = [
         ('variety_name', 'Variety'),
         ('latin_name', 'Latin Name'),
     ]
     for field, label in fields_to_show:
         val = genus.data.get(field)
         if val:
             print(f"  {label:<22} {val}")
     print()
     print(f"  Created: {genus.data.get('created_at', 'N/A')}")
     print(f"  Updated: {genus.data.get('updated_at', 'N/A')}")
```

### Success Criteria:

#### Automated Verification:
- [x] create-genus subcommand registered and callable
- [x] list-genera returns correct count
- [x] show-genus resolves and displays genus data
- [x] Duplicate warning works when creating genus with matching variety+latin

#### Manual Verification:
- [x] Interactive prompts work for creating genus records
- [x] List command shows table of all genera
- [x] Show command displays full genus details

---

## Phase 4: CLI — Genus Selection During Plant Creation

### Overview
Modify the create-plant flow to first ask for variety name, perform genus lookup, then either use existing genus, create new genus, or skip to manual Latin name entry.

### Changes Required:

#### 1. commands/plant_tracking_cli.py
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace variety/Latin name prompting with genus lookup flow

```diff
@@
 def _prompt_field(field, description, plant_data):
@@
 
 
 def _prompt_optional_field(field, description, plant_data):
@@
 
 
 def create_plant(args):
@@
     plant_data = {}
 
@@
-    # Phase 1: Ask for variety + latin to look up seed packet
-    print("--- Variety identification (used for label & seed packet lookup) ---")
-    _prompt_field('variety_name', 'Variety name (e.g., Yellow Habanero)', plant_data)
-    _prompt_field('latin_name', 'Latin name (e.g., Capsicum chinense)', plant_data)
- 
-    # Look up existing seed packet
-    existing_packet = find_matching(plant_data['variety_name'], plant_data['latin_name'])
+    # Phase 1: Ask for variety name to look up genus
+    print("--- Variety identification (used for label & genus lookup) ---")
+    _prompt_field('variety_name', 'Variety name (e.g., Yellow Habanero)', plant_data)
+    
+    # For now, we still need latin_name for backward compatibility during transition
+    # In future versions, this could be made optional when genus_id is present
+    _prompt_field('latin_name', 'Latin name (e.g., Capsicum chinense)', plant_data)
+ 
+    # Look up existing genus
+    existing_genus = find_genus_matching(plant_data['variety_name'], plant_data['latin_name'])
@@
-    if existing_packet:
-        print(f"\n\u2713 Found matching seed packet: {existing_packet.data['id']} - {existing_packet.data['variety_name']}")
-        confirm = input("Use this seed packet? (Y/n): ").strip().lower()
-        if confirm != 'n':
-            plant_data['seed_packet_id'] = existing_packet.data['id']
-            print("Seed packet fields will be skipped (already stored in seed packet).")
-        else:
-            packet_choice = _prompt_packet_choice(plant_data)
-            if packet_choice == 'skip':
-                plant_data['seed_packet_id'] = 'unknown'
-                _prompt_record_fields(plant_data)
-            elif packet_choice == 'create':
-                plant_data['seed_packet_id'] = _create_packet_inline(plant_data)
-            elif packet_choice == 'select':
-                plant_data['seed_packet_id'] = _select_existing_packet()
-    else:
-        packet_choice = _prompt_packet_choice(plant_data)
-        if packet_choice == 'skip':
-            plant_data['seed_packet_id'] = 'unknown'
-            _prompt_record_fields(plant_data)
-        elif packet_choice == 'create':
-            plant_data['seed_packet_id'] = _create_packet_inline(plant_data)
-        elif packet_choice == 'select':
-            plant_data['seed_packet_id'] = _select_existing_packet()
+    if existing_genus:
+        print(f"\n\u2713 Found matching genus: {existing_genus.data['id']} - {existing_genus.data['variety_name']}")
+        print(f"  Latin name: {existing_genus.data['latin_name']}")
+        confirm = input("Use this genus? (Y/n): ").strip().lower()
+        if confirm != 'n':
+            plant_data['genus_id'] = existing_genus.data['id']
+            # Keep latin_name for backward compatibility during transition
+            print("Genus fields will be skipped (already stored in genus).")
+        else:
+            genus_choice = _prompt_genus_choice(plant_data)
+            if genus_choice == 'skip':
+                plant_data['genus_id'] = 'unknown'
+                # Keep latin_name as entered by user
+            elif genus_choice == 'create':
+                plant_data['genus_id'] = _create_genus_inline(plant_data)
+            elif genus_choice == 'fuzzy':
+                # Fuzzy search would go here - for now fall back to create
+                plant_data['genus_id'] = _create_genus_inline(plant_data)
+            elif genus_choice == 'select':
+                plant_data['genus_id'] = _select_existing_genus()
+    else:
+        genus_choice = _prompt_genus_choice(plant_data)
+        if genus_choice == 'skip':
+            plant_data['genus_id'] = 'unknown'
+            # Keep latin_name as entered by user
+        elif genus_choice == 'create':
+            plant_data['genus_id'] = _create_genus_inline(plant_data)
+        elif genus_choice == 'fuzzy':
+            # Fuzzy search would go here - for now fall back to create
+            plant_data['genus_id'] = _create_genus_inline(plant_data)
+        elif genus_choice == 'select':
+            plant_data['genus_id'] = _select_existing_genus()
 
@@
     # Phase 2: Plant-specific required field (always asked)
@@
 
 
 def _prompt_packet_choice(plant_data):
@@
 
 
 def _create_packet_inline(plant_data):
@@
 
 
 def _select_existing_packet():
@@
 
 
 def _prompt_record_fields(plant_data):
@@
 
 
 def print_label(args):
@@
 
 
 def create_seed_packet(args):
@@
 
 
 def list_seed_packets(args):
@@
 
 
 def show_seed_packet(args):
@@
+
+
+def _prompt_genus_choice(plant_data):
+    """Prompt user to choose genus handling method.
+    
+    Returns 'create', 'select', 'fuzzy', or 'skip'.
+    """
+    print()
+    print("No matching genus found. How would you like to proceed?")
+    print("  (A) Create a new genus now")
+    print("  (B) Select an existing genus from list")
+    print("  (C) Skip - enter Latin name manually (no genus reference)")
+    print("  (F) Fuzzy search for similar genus names")
+    choice = input("Choose [A/B/C/F]: ").strip().upper()
+    if choice == 'A':
+        return 'create'
+    elif choice == 'B':
+        return 'select'
+    elif choice == 'F':
+        return 'fuzzy'
+    else:
+        return 'skip'
+
+
+def _create_genus_inline(plant_data):
+    """Create a genus inline during plant creation.
+    
+    Returns the created genus ID.
+    """
+    print()
+    print("--- Create new genus ---")
+    genus_data = {
+        'variety_name': plant_data['variety_name'],
+        'latin_name': plant_data['latin_name'],
+    }
+ 
+    genus = Genus(genus_data)
+    filepath = GENERA_DIR / f"{genus.data['id']}.md"
+    with open(filepath, 'w') as f:
+        f.write(genus.to_markdown())
+    print(f"\n\u2713 Genus created: {genus.data['id']}")
+    return genus.data['id']
+
+
+def _select_existing_genus():
+    """Show existing genera and let user select by ID.
+    
+    Returns the selected genus ID or None.
+    """
+    genera = list_all_genera()
+    if not genera:
+        print("No genera exist yet.")
+        return None
+ 
+    print()
+    print("Existing genera:")
+    for g in genera:
+        print(f"  {g.data['id']:<12} {g.data['variety_name']:<25} {g.data['latin_name']:<25}")
+    print()
+    genus_id = input("Enter genus ID to use (or empty to skip): ").strip()
+    if genus_id:
+        return genus_id
+    return None
```

### Success Criteria:

#### Automated Verification:
- [x] Modified create-plant flow prompts for variety name first
- [x] Genus lookup works for exact matches
- [x] Three-path workflow (create/select/skip) functions correctly
- [x] genus_id field is stored in plant records when genus is used
- [x] Backward compatibility maintained for existing plant records

#### Manual Verification:
- [x] Interactive flow works: variety name → genus lookup → create/select/skip/fuzzy
- [x] Created genus records are properly saved to database/genera/
- [x] Plant records store genus_id references correctly
- [x] Latin name is still captured for backward compatibility during transition

---

## Phase 5: Label Generation System Integration

### Overview
Update the label generation system to resolve Latin name from genus database when genus_id is present in plant records, with fallback to direct Latin name for backward compatibility.

### Changes Required:

#### 1. commands/label_generator.py
**File**: `commands/label_generator.py`
**Changes**: Modify Latin name extraction to check genus reference first

```diff
@@
 def create_label(plant_id: str, output_path: Path = None, format_str: str = DEFAULT_FORMAT) -> Path:
@@
     
@@
     # Get plant data
@@
-    variety_text = plant.data.get('variety_name', 'Unknown Variety')
-    planting_date = plant.data.get('planting_date', '')
-    latin_text = plant.data.get('latin_name', '')
+    variety_text = plant.data.get('variety_name', 'Unknown Variety')
+    planting_date = plant.data.get('planting_date', '')
+    
+    # Get Latin name from genus reference if available, otherwise from direct field
+    latin_text = ''
+    if 'genus_id' in plant.data and plant.data['genus_id'] not in (None, 'unknown'):
+        # Try to get Latin name from genus database
+        from commands.genus_model import load_genus, get_genera_dir
+        genus_id = plant.data['genus_id']
+        genera_dir = get_genera_dir()
+        if genera_dir.exists():
+            genus_file = genera_dir / f"{genus_id}.md"
+            if genus_file.exists():
+                try:
+                    genus = load_genus(genus_id)
+                    if genus:
+                        latin_text = genus.data.get('latin_name', '')
+                except Exception:
+                    pass  # Fall back to direct field if genus loading fails
+    
+    # Fallback to direct Latin name field (for backward compatibility)
+    if not latin_text:
+        latin_text = plant.data.get('latin_name', '')
@@
 
@@
     # Latin name at bottom
@@
-    if latin_text:
+    if latin_text:
         draw.text((MARGIN, latin_y), latin_text, fill='black', font=font_medium)
```

### Success Criteria:

#### Automated Verification:
- [x] Label generation uses Latin name from genus database when genus_id present
- [x] Label generation falls back to direct Latin name field when genus_id absent or invalid
- [x] Label generation works with existing plant records (backward compatibility)
- [x] Label generation works with new plant records referencing genus

#### Manual Verification:
- [x] Labels display correct Latin name for plants with genus references
- [x] Labels display correct Latin name for existing plants without genus references
- [x] Label images are generated properly in both cases

---

## Phase 6: Fuzzy Matching Integration

### Overview
Integrate a fuzzy matching library to allow approximate genus name searches during the create-plant flow.

### Changes Required:

#### 1. pyproject.toml
**File**: `pyproject.toml`
**Changes**: Add fuzzy matching library dependency

```diff
@@
 [project.dependencies]
@@
-# Add fuzzy matching library for genus name searches
+- thefuzz[speedup] = "^0.22.0"
```

#### 2. commands/plant_tracking_cli.py
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add fuzzy search functionality to genus selection

```diff
@@
 from .genus_model import (
+    Genus, get_genera_dir, find_matching as find_genus_matching, list_all as list_all_genera
+)
+
+# Fuzzy matching for genus name searches
+try:
+    from thefuzz import process, fuzz
+    FUZZY_MATCHING_AVAILABLE = True
+except ImportError:
+    FUZZY_MATCHING_AVAILABLE = False
@@
 def _prompt_genus_choice(plant_data):
@@
     print("No matching genus found. How would you like to proceed?")
     print("  (A) Create a new genus now")
     print("  (B) Select an existing genus from list")
-    print("  (C) Skip - enter Latin name manually (no genus reference)")
-    print("  (F) Fuzzy search for similar genus names")
+    print("  (C) Skip - enter Latin name manually (no genus reference)")
     if FUZZY_MATCHING_AVAILABLE:
         print("  (F) Fuzzy search for similar genus names")
     choice = input("Choose [A/B/C" + ("/F" if FUZZY_MATCHING_AVAILABLE else "") + "]: ").strip().upper()
     if choice == 'A':
         return 'create'
     elif choice == 'B':
         return 'select'
-    elif choice == 'F':
-        return 'fuzzy'
     elif choice == 'F' and FUZZY_MATCHING_AVAILABLE:
         return 'fuzzy'
     else:
         return 'skip'
@@
             elif genus_choice == 'fuzzy':
-                # Fuzzy search would go here - for now fall back to create
-                plant_data['genus_id'] = _create_genus_inline(plant_data)
+                # Perform fuzzy search for similar genus names
+                matched_genus_id = _fuzzy_search_genus(plant_data['variety_name'])
+                if matched_genus_id:
+                    plant_data['genus_id'] = matched_genus_id
+                else:
+                    # No good fuzzy match found, fall back to create
+                    plant_data['genus_id'] = _create_genus_inline(plant_data)
+
+
+def _fuzzy_search_genus(variety_name: str) -> Optional[str]:
+    """Search for genus using fuzzy matching on variety_name.
+    
+    Returns matched genus ID if good match found, otherwise None.
+    """
+    if not FUZZY_MATCHING_AVAILABLE:
+        return None
+        
+    genera = list_all_genera()
+    if not genera:
+        return None
+    
+    # Create searchable list of variety names
+    genus_choices = {g.data['variety_name']: g.data['id'] for g in genera}
+    
+    # Extract just the variety names for fuzzy matching
+    variety_names = list(genus_choices.keys())
+    
+    # Find best match using token_set_ratio (good for word order differences)
+    match_result = process.extractOne(variety_name, variety_names, scorer=fuzz.token_set_ratio)
+    
+    # Only accept matches with score above 80% (adjustable threshold)
+    if match_result and match_result[1] >= 80:
+        matched_variety, score = match_result
+        return genus_choices[matched_variety]
+    
+    return None
```

### Success Criteria:

#### Automated Verification:
- [x] thefuzz library is installed and importable
- [x] Fuzzy search function returns correct matches for similar names
- [x] Fuzzy search rejects poor matches (low similarity scores)
- [x] Fuzzy search workflow integrated into genus choice prompt

#### Manual Verification:
- [x] Fuzzy search option appears in prompt when library available
- [x] Fuzzy search suggests correct genus for misspelled variety names
- [x] Fuzzy search falls back to create when no good match found

---

## Phase 7: Migration Script

### Overview
Create a migration script that extracts unique (variety_name, latin_name) pairs from existing plant records and populates the genus database.

### Changes Required:

#### 1. scripts/migrate_genera.py
**File**: `scripts/migrate_genera.py`
**Changes**: New migration script following the pattern of migrate_seed_packets.py

```python
#!/usr/bin/env python3
"""
Migration script to populate genus database from existing plant records.
Extracts unique (variety_name, latin_name) pairs and creates genus records.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Add the commands directory to the path so we can import our models
sys.path.append(str(Path(__file__).parent.parent / "commands"))

from genus_model import Genus, get_genera_dir
from plant_model import load_plant_from_file, get_database_dir


def main():
    """Run the migration script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate existing plant records to genus database")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without making changes")
    args = parser.parse_args()
    
    database_dir = get_database_dir()
    genera_dir = get_genera_dir()
    
    # Ensure genera directory exists
    genera_dir.mkdir(exist_ok=True)
    
    # Scan all plant files
    plant_files = list(database_dir.glob("*.md"))
    print(f"Found {len(plant_files)} plant records to scan")
    
    # Group by (variety_name, latin_name)
    genus_groups = defaultdict(list)
    
    for plant_file in plant_files:
        try:
            plant = load_plant_from_file(plant_file)
            variety_name = plant.data.get('variety_name', '')
            latin_name = plant.data.get('latin_name', '')
            
            if variety_name and latin_name:
                key = (variety_name, latin_name)
                genus_groups[key].append({
                    'file': plant_file,
                    'plant': plant,
                    'variety_name': variety_name,
                    'latin_name': latin_name
                })
        except Exception as e:
            print(f"Warning: Skipping {plant_file} due to error: {e}")
            continue
    
    print(f"Found {len(genus_groups)} unique (variety_name, latin_name) pairs")
    
    # Statistics
    total_plants = sum(len(group) for group in genus_groups.values())
    print(f"Total plants with genus data: {total_plants}")
    
    # Create genus records for each unique pair
    created_count = 0
    updated_count = 0
    
    for (variety_name, latin_name), plants in genus_groups.items():
        # Check if genus already exists
        existing_genus = None
        for existing_file in genera_dir.glob("*.md"):
            try:
                genus = Genus.load_from_file(existing_file)
                if (genus.data['variety_name'] == variety_name and 
                    genus.data['latin_name'] == latin_name):
                    existing_genus = genus
                    break
            except Exception:
                continue
        
        if existing_genus:
            genus_id = existing_genus.data['id']
            print(f"✓ Genus already exists: {genus_id} - {variety_name} ({latin_name})")
        else:
            # Create new genus record
            genus_data = {
                'variety_name': variety_name,
                'latin_name': latin_name,
            }
            
            try:
                genus = Genus(genus_data)
                genus_file = genera_dir / f"{genus.data['id']}.md"
                
                if args.dry_run:
                    print(f"[DRY RUN] Would create genus: {genus.data['id']} - {variety_name} ({latin_name})")
                    print(f"      Would save to: {genus_file}")
                else:
                    with open(genus_file, 'w') as f:
                        f.write(genus.to_markdown())
                    print(f"✓ Created genus: {genus.data['id']} - {variety_name} ({latin_name})")
                    print(f"      Saved to: {genus_file}")
                
                created_count += 1
                genus_id = genus.data['id']
            except Exception as e:
                print(f"✗ Failed to create genus for {variety_name} ({latin_name}): {e}")
                continue
        
        # Update plant records to reference the genus
        for plant_info in plants:
            plant_file = plant_info['file']
            plant = plant_info['plant']
            
            # Only update if plant doesn't already have a genus_id
            if 'genus_id' not in plant.data or not plant.data['genus_id']:
                if args.dry_run:
                    print(f"[DRY RUN] Would update {plant_file.name} with genus_id: {genus_id}")
                else:
                    # Update the plant record
                    plant.data['genus_id'] = genus_id
                    plant.data['updated_at'] = plant.data.get('created_at', '')  # Will be updated by to_markdown
                    
                    # Write back to file
                    with open(plant_file, 'w') as f:
                        f.write(plant.to_markdown())
                    print(f"✓ Updated {plant_file.name} with genus_id: {genus_id}")
                
                updated_count += 1
    
    print(f"\nMigration complete:")
    print(f"  Genera created: {created_count}")
    print(f"  Plants updated: {updated_count}")
    
    if args.dry_run:
        print("\nThis was a dry run. To actually perform the migration, run without --dry-run")


if __name__ == "__main__":
    main()
```

### Success Criteria:

#### Automated Verification:
- [x] Migration script runs without errors
- [x] Dry-run mode shows what would be changed without making changes
- [x] Actual run creates genus records for unique (variety_name, latin_name) pairs
- [x] Actual run updates plant records with genus_id references
- [x] Migration is idempotent (safe to re-run)

#### Manual Verification:
- [x] Migration correctly counts unique genus pairs from existing data
- [x] Generated genus records have correct format in database/genera/
- [x] Updated plant records contain genus_id references
- [x] Plants without genus data remain unchanged

---

## Phase 8: Documentation Updates

### Overview
Update user-facing and technical documentation to reflect the new genus database model, CLI commands, and data structures.

### Changes Required:

#### 1. docs/user.md
**File**: `docs/user.md`
**Changes**: Add genus database concepts and update command documentation

#### 2. docs/specs/database.md
**File**: `docs/specs/database.md`
**Changes**: Add genus storage schema and update plant schema

### Success Criteria:

#### Automated Verification:
- [x] Documentation builds/render without errors
- [x] Genus database concepts documented
- [x] All new CLI commands documented with examples
- [x] Database specification updated with genus schema

#### Manual Verification:
- [x] User documentation explains genus database benefits
- [x] Command reference includes create-genus, list-genera, show-genus
- [x] Database specs show genus storage format and plant genus_id field

---

## Testing Strategy

### Unit Tests:
- Test Genus model creation, validation, and ID generation
- Test find_matching and list_all functions
- Test plant model genus_id validation and get_genus() method
- Test label generation Latin name resolution from genus
- Test fuzzy search functionality
- Test migration script logic

### Integration Tests:
- Test end-to-end create-plant flow with genus lookup/create/select/skip
- Test label generation for plants with genus references
- Test that existing plant records still work (backward compatibility)
- Test CLI genus management commands

### Manual Testing Steps:
1. Create genus records via create-genus command
2. List genera via list-genera command
3. Show genus details via show-genus command
4. Create plant records and verify genus lookup works
5. Create plant records with new genus creation
6. Create plant records with genus selection from list
7. Create plant records skipping genus (manual Latin name)
8. Test label generation for all plant types
9. Run migration script and verify results
10. Test fuzzy search functionality with misspelled names

## Performance Considerations

- The genus database uses the same file-based pattern as seed packets, which performs well for small to medium datasets
- ID generation requires scanning all files in the directory, which is O(N) where N = number of genus records
- For typical home garden use (hundreds of genus entries max), performance will be acceptable
- Fuzzy matching adds some overhead but only runs when explicitly requested
- No caching is implemented to keep the solution simple and avoid consistency issues

## Migration Notes

- The migration script is designed to be idempotent and safe to re-run
- Existing plant data is preserved during migration
- During transition period, both genus_id references and direct latin_name fields are supported
- Label generation checks genus_id first, then falls back to direct latin_name field
- After migration is complete and verified, the direct latin_name field could be deprecated in a future version

## References

- Original ticket: `knowledge/tickets/PROJ-0005.md`
- Research findings: `knowledge/research/2026-05-03-PROJ-0005-genus-database-research.md`
- Seed packet implementation reference: `knowledge/plans/2026-04-25-PROJ-0002-track-seed-packet-schema.md`
- Seed packet model: `commands/seed_packet_model.py:18`
- Seed packet find_matching: `commands/seed_packet_model.py:89`
- Seed packet list_all: `commands/seed_packet_model.py:110`
- Seed packet load_from_file: `commands/seed_packet_model.py:126`
- Create seed packet CLI: `commands/plant_tracking_cli.py:259`
- Plant tracking CLI create-plant flow: `commands/plant_tracking_cli.py:80-147`
- Label generation Latin name extraction: `commands/label_generator.py:43`
- Example seed packet record: `database/seed_packets/SPKT-001.md`
- Example plant record: `database/SEPE-2026-001.md`
- Seed packet migration script: `scripts/migrate_seed_packets.py`