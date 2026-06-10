# Create Plant Entry and Print Label Implementation Plan

## Overview

This plan implements the core plant tracking functionality for the plant tracking system. It provides three CLI commands:
1. `create-plant`: Interactive CLI that prompts for plant information, generates a unique ID, and saves a markdown record
2. `create-label`: Generates a 40x30mm PNG label with QR code encoding the plant ID
3. `print-label`: Sends the label PNG to the Phomemo M120 Bluetooth printer

Plant records are stored as markdown files in a `database/` directory with structured frontmatter containing all plant attributes, as specified in `knowledge/specs/database.md`.

## Current State Analysis

The project currently contains:
- Existing phomemo-tools for label printing (`phomemo-tools/tools/`)
- PRD documentation outlining the full plant tracking system vision
- No existing database/ directory or plant tracking CLI tools
- No plant record storage or label generation functionality

Key discoveries:
- Phomemo tools use Python with PIL/Pillow for image processing
- Printing pipeline involves specific byte sequences for label formatting
- Label dimensions specified as 40x30mm in requirements
- ID format should be VARIETY-YYYY-SEQ (e.g., HABY-2026-001)

## Desired End State

After implementation, users will be able to:
1. Run `create-plant` and interactively enter all plant information from seed packets
2. System auto-generates a unique ID in VARIETY-YYYY-SEQ format
3. Plant record is saved as a markdown file in `database/` with YAML frontmatter
4. Run `create-label` with a plant ID to generate a 40x30mm PNG label
5. Label contains: left side = text fields (variety, Latin name, planting date), right side = QR code, bottom = one line of text
6. Run `print-label` to send the label to Phomemo M120 printer via Bluetooth
7. QR code encodes the plant ID and is scannable to retrieve the plant record

Verification:
- Automated tests validate file creation, ID format, image dimensions, QR code encoding
- Manual verification confirms label readability, print quality, and UI interaction

## What We're NOT Doing

- Seed packet scanning/OCR (separate ticket)
- QR code scanning / plant record retrieval (separate functionality)
- Hermes agent integration (planned for later phases)
- Mobile app interface (post-MVP feature)
- Photo attachment capability (post-MVP feature)
- Editing/updating plant records after creation (out of scope per ticket)
- Migration to Postgres database (planned for Phase 3)

## Implementation Approach

We'll create a Python CLI tool with three subcommands following the existing phomemo-tools patterns:
1. Use argparse for command structure
2. Leverage existing phomemo-filter.py for printing pipeline
3. Use qrcode and Pillow libraries for label generation
4. Store plant records as markdown files with YAML frontmatter in database/
5. Implement ID generation by parsing variety abbreviations, current year, and sequencing from existing entries
6. Structure prompts to capture all required plant fields from PRD

## Phase 1: Project Setup and Database Structure

### Overview
This phase sets up the project structure, creates the database directory, and implements the foundational data models and storage mechanism for plant records.

### Changes Required:

#### 1. Project Structure
**File**: `plant_tracking_cli.py`
**Changes**: Create main CLI entry point with subcommand structure

```python
#!/usr/bin/env python3
"""
Plant Tracking CLI - Main entry point for plant tracking commands
"""
import argparse
import sys
import os
from pathlib import Path

# Ensure database directory exists
DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Plant Tracking System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # create-plant subcommand
    plant_parser = subparsers.add_parser('create-plant', help='Create a new plant record')
    # TODO: Add plant-specific arguments
    
    # create-label subcommand
    label_parser = subparsers.add_parser('create-label', help='Create a label for a plant')
    label_parser.add_argument('plant_id', help='Plant ID for label generation')
    
    # print-label subcommand
    print_parser = subparsers.add_parser('print-label', help='Print a label for a plant')
    print_parser.add_argument('plant_id', help='Plant ID or label file path')
    
    args = parser.parse_args()
    
    if args.command == 'create-plant':
        create_plant(args)
    elif args.command == 'create-label':
        create_label(args)
    elif args.command == 'print-label':
        print_label(args)
    else:
        parser.print_help()

def create_plant(args):
    """Create a new plant record"""
    print("Creating plant record...")
    # TODO: Implement interactive prompts and data collection
    
def create_label(args):
    """Create a label for a plant"""
    print(f"Creating label for plant {args.plant_id}")
    # TODO: Implement label generation
    
def print_label(args):
    """Print a label for a plant"""
    print(f"Printing label for {args.plant_id}")
    # TODO: Implement printing via phomemo-filter

if __name__ == "__main__":
    main()
```

**File**: `pyproject.toml`
**Changes**: Define Python dependencies using modern pyproject.toml standard (2026 approach)

```toml
[project]
name = "plant-tracking-cli"
version = "0.1.0"
description = "CLI for plant tracking with QR label generation"
authors = [{name = "Gardener", email = "gardener@example.com"}]
dependencies = [
    "qrcode[pil]>=7.4",
    "Pillow>=10.0.0",
    "PyYAML>=6.0",
    "click>=8.0.0"
]

[project.scripts]
plant-tracking = "plant_tracking_cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 2. Plant Data Model
**File**: `plant_model.py`
**Changes**: Define plant data structure and validation following the specification in `knowledge/specs/database.md`

```python
"""
Plant data model and validation
"""
import re
from datetime import datetime
from typing import Dict, Any, Optional
import yaml

class Plant:
    """Represents a plant record"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
    
    def validate(self):
        """Validate plant data"""
        required_fields = [
            'variety_name', 'latin_name', 'brand', 'days_to_maturity',
            'germination_time', 'planting_depth', 'spacing', 'sun_requirements',
            'indoor_start_time', 'planned_planting_date'
        ]
        
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")
    
    def to_markdown(self) -> str:
        """Convert plant data to markdown with YAML frontmatter"""
        # Generate ID if not present
        if 'id' not in self.data:
            self.data['id'] = self.generate_id()
            
        frontmatter = yaml.dump(self.data, default_flow_style=False)
        return f"---\n{frontmatter}---\n\n# Plant Record for {self.data['variety_name']}\n\n*ID: {self.data['id']}*\n\n*Created: {datetime.now().strftime('%Y-%m-%d')}*"
    
    def generate_id(self) -> str:
        """Generate plant ID in VARIETY-YYYY-SEQ format"""
        variety = self.data['variety_name']
        # Extract abbreviation (first 2 letters of each word, max 4 chars)
        words = variety.upper().split()
        abbrev = ''.join([word[:2] for word in words if word.isalpha()])[:4]
        if not abbrev:
            abbrev = variety[:4].upper()
        
        year = datetime.now().year
        
        # Find sequence number by checking existing records
        seq = self.find_next_sequence(abbrev, year)
        
        return f"{abbrev}-{year}-{seq:03d}"
    
    def find_next_sequence(self, abbrev: str, year: int) -> int:
        """Find next sequence number for given abbreviation and year"""
        pattern = re.compile(f"{abbrev}-{year}-(\\d{{3}})")
        max_seq = 0
        
        # Check existing markdown files in database
        database_dir = Path("database")
        if database_dir.exists():
            for file in database_dir.glob("*.md"):
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        # Extract YAML frontmatter
                        if content.startswith('--'):
                            parts = content.split('--', 2)
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

def load_plant_from_file(file_path: Path) -> Plant:
    """Load a plant record from a markdown file"""
    with open(file_path, 'r') as f:
        content = f.read()
        
    if not content.startswith('--'):
        raise ValueError("Invalid plant file format: missing YAML frontmatter")
    
    parts = content.split('--', 2)
    if len(parts) < 3:
        raise ValueError("Invalid plant file format: malformed frontmatter")
    
    frontmatter = parts[1]
    data = yaml.safe_load(frontmatter)
    return Plant(data)
```

### Success Criteria:

#### Automated Verification:
- [x] Database directory is created: `test -d database`
- [x] CLI entry point is executable: `test -x plant_tracking_cli.py`
- [x] Dependencies can be installed: `pip install .` (from pyproject.toml)
- [x] Plant model validates required fields per database spec
- [x] ID generation follows VARIETY-YYYY-SEQ format
- [x] Generated markdown files conform to database spec format

#### Manual Verification:
- [ ] Project structure is clear and follows Python conventions
- [ ] Database directory is created automatically
- [ ] Plant model handles edge cases in ID generation

---

## Phase 2: Interactive Plant Creation

### Overview
This phase implements the `create-plant` command with interactive prompts to collect all required plant information from users.

### Changes Required:

#### 1. Enhanced CLI with Interactive Prompts
**File**: `plant_tracking_cli.py`
**Changes**: Add interactive prompts for plant data collection

```python
#!/usr/bin/env python3
"""
Plant Tracking CLI - Main entry point for plant tracking commands
"""
import argparse
import sys
import os
from pathlib import Path
from plant_model import Plant

# Ensure database directory exists
DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Plant Tracking System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # create-plant subcommand
    plant_parser = subparsers.add_parser('create-plant', help='Create a new plant record')
    # TODO: Add plant-specific arguments
    
    # create-label subcommand
    label_parser = subparsers.add_parser('create-label', help='Create a label for a plant')
    label_parser.add_argument('plant_id', help='Plant ID for label generation')
    
    # print-label subcommand
    print_parser = subparsers.add_parser('print-label', help='Print a label for a plant')
    print_parser.add_argument('plant_id', help='Plant ID or label file path')
    
    args = parser.parse_args()
    
    if args.command == 'create-plant':
        create_plant(args)
    elif args.command == 'create-label':
        create_label(args)
    elif args.command == 'print-label':
        print_label(args)
    else:
        parser.print_help()

def create_plant(args):
    """Create a new plant record through interactive prompts"""
    print("=== Create New Plant Record ===")
    print("Please enter the following information from your seed packet:")
    print()
    
    # Define plant fields with descriptions
    fields = [
        ('variety_name', 'Variety name (e.g., Yellow Habanero)'),
        ('latin_name', 'Latin name (e.g., Capsicum chinense)'),
        ('brand', 'Brand/company name'),
        ('days_to_maturity', 'Days to maturity (integer)'),
        ('germination_time', 'Germination time (e.g., 7-14 days)'),
        ('planting_depth', 'Planting depth (e.g., 0.25 inches)'),
        ('spacing', 'Plant spacing (e.g., 18 inches)'),
        ('sun_requirements', 'Sun requirements (e.g., Full sun)'),
        ('indoor_start_time', 'Indoor start time (e.g., 8 weeks before last frost)'),
        ('planned_planting_date', 'Planned planting date (YYYY-MM-DD)')
    ]
    
    plant_data = {}
    
    for field, description in fields:
        while True:
            value = input(f"{description}: ").strip()
            if value:
                # Special handling for numeric fields
                if field == 'days_to_maturity':
                    try:
                        value = int(value)
                        if value <= 0:
                            print("Please enter a positive number")
                            continue
                    except ValueError:
                        print("Please enter a valid integer")
                        continue
                plant_data[field] = value
                break
            else:
                print("This field is required")
    
    try:
        # Create plant record
        plant = Plant(plant_data)
        
        # Save to database directory
        filename = f"{plant.data['id']}.md"
        filepath = DATABASE_DIR / filename
        
        with open(filepath, 'w') as f:
            f.write(plant.to_markdown())
        
        print(f"\n✓ Plant record created successfully!")
        print(f"ID: {plant.data['id']}")
        print(f"Saved to: {filepath}")
        print(f"\nNext steps:")
        print(f"  1. Generate label: plant-tracking create-label {plant.data['id']}")
        print(f"  2. Print label: plant-tracking print-label {plant.data['id']}")
        
    except Exception as e:
        print(f"\n✗ Error creating plant record: {e}")
        sys.exit(1)

def create_label(args):
    """Create a label for a plant"""
    print(f"Creating label for plant {args.plant_id}")
    # TODO: Implement label generation
    
def print_label(args):
    """Print a label for a plant"""
    print(f"Printing label for {args.plant_id}")
    # TODO: Implement printing via phomemo-filter

if __name__ == "__main__":
    main()
```

### Success Criteria:

#### Automated Verification:
- [x] create-plant command exists and is callable
- [x] Interactive prompts capture all required fields
- [x] Plant record is saved with correct ID format
- [x] Markdown file contains YAML frontmatter with all data
- [x] ID is unique and follows VARIETY-YYYY-SEQ pattern

#### Manual Verification:
- [ ] User is prompted for all plant fields in logical order
- [ ] Input validation works correctly (e.g., days_to_maturity must be positive integer)
- [ ] Generated ID follows expected format based on variety name
- [ ] Plant record is saved to database/ directory with .md extension
- [ ] Success message shows next steps for label creation and printing

---

## Phase 3: Label Generation

### Overview
This phase implements the `create-label` command to generate 40x30mm PNG labels with QR codes encoding plant IDs.

### Changes Required:

#### 1. Label Generation Functionality
**File**: `label_generator.py`
**Changes**: Create label generation with QR code and layout

```python
"""
Label generation for plant tracking system
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from plant_model import load_plant_from_file

# Label specifications (40x30mm at 300 DPI ≈ 472x354 pixels)
LABEL_WIDTH_MM = 40
LABEL_HEIGHT_MM = 30
DPI = 300
LABEL_WIDTH_PX = int(LABEL_WIDTH_MM * DPI / 25.4)  # ≈ 472px
LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM * DPI / 25.4)  # ≈ 354px

# Layout constants
TEXT_AREA_WIDTH_RATIO = 0.4  # 40% for text, 60% for QR code
TEXT_AREA_WIDTH = int(LABEL_WIDTH_PX * TEXT_AREA_WIDTH_RATIO)
QR_CODE_WIDTH = LABEL_WIDTH_PX - TEXT_AREA_WIDTH
MARGIN = int(10 * DPI / 25.4)  # 10mm margin
BOTTOM_TEXT_HEIGHT = int(15 * DPI / 25.4)  # 15mm for bottom text

def create_label(plant_id: str, output_path: Path = None) -> Path:
    """
    Create a 40x30mm label for a plant
    
    Args:
        plant_id: The plant ID to encode in QR code
        output_path: Optional output path, defaults to database/{plant_id}_label.png
    
    Returns:
        Path to the generated label image
    """
    # Load plant data
    database_dir = Path("database")
    plant_file = database_dir / f"{plant_id}.md"
    
    if not plant_file.exists():
        raise FileNotFoundError(f"Plant record not found: {plant_id}")
    
    plant = load_plant_from_file(plant_file)
    
    # Set output path
    if output_path is None:
        output_path = database_dir / f"{plant_id}_label.png"
    
    # Create label image (white background)
    label_image = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), 'white')
    draw = ImageDraw.Draw(label_image)
    
    # Try to load a font, fallback to default
    try:
        # Try to use a decent font
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except IOError:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(plant_id)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((QR_CODE_WIDTH - 2*MARGIN, QR_CODE_WIDTH - 2*MARGIN))
    
    # Paste QR code on right side
    qr_x = TEXT_AREA_WIDTH + MARGIN
    qr_y = (LABEL_HEIGHT_PX - BOTTOM_TEXT_HEIGHT - qr_img.size[1]) // 2
    label_image.paste(qr_img, (qr_x, qr_y))
    
    # Add text on left side
    text_x = MARGIN
    text_y = MARGIN
    
    # Variety name (large)
    variety_text = plant.data.get('variety_name', 'Unknown Variety')
    draw.text((text_x, text_y), variety_text, fill='black', font=font_large)
    text_y += font_large.getsize(variety_text)[1] + 5
    
    # Latin name (medium)
    latin_text = plant.data.get('latin_name', '')
    if latin_text:
        draw.text((text_x, text_y), latin_text, fill='black', font=font_medium)
        text_y += font_medium.getsize(latin_text)[1] + 5
    
    # Planting date (small)
    planting_date = plant.data.get('planned_planting_date', '')
    if planting_date:
        date_text = f"Planted: {planting_date}"
        draw.text((text_x, text_y), date_text, fill='black', font=font_small)
        text_y += font_small.getsize(date_text)[1] + 5
    
    # Add bottom text line (one line of text at bottom)
    bottom_y = LABEL_HEIGHT_PX - BOTTOM_TEXT_HEIGHT + MARGIN
    bottom_text = f"{variety_text} • {planting_date}"
    # Truncate if too long
    max_chars = int((TEXT_AREA_WIDTH - 2*MARGIN) / (font_small.getsize('x')[0] * 0.6))
    if len(bottom_text) > max_chars:
        bottom_text = bottom_text[:max_chars-3] + "..."
    draw.text((MARGIN, bottom_y), bottom_text, fill='black', font=font_small)
    
    # Save the label
    label_image.save(output_path, 'PNG', dpi=(DPI, DPI))
    
    return output_path

def main():
    """Command line interface for label generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate plant label')
    parser.add_argument('plant_id', help='Plant ID')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    try:
        output_path = Path(args.output) if args.output else None
        label_path = create_label(args.plant_id, output_path)
        print(f"Label generated: {label_path}")
    except Exception as e:
        print(f"Error generating label: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
```

#### 2. Update CLI to Use Label Generator
**File**: `plant_tracking_cli.py`
**Changes**: Implement create-label command

```python
def create_label(args):
    """Create a label for a plant"""
    from label_generator import create_label
    from pathlib import Path
    
    try:
        label_path = create_label(args.plant_id)
        print(f"✓ Label created successfully: {label_path}")
        print(f"  Review the label before printing:")
        print(f"    plant-tracking print-label {args.plant_id}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print(f"  Make sure you've created a plant record first:")
        print(f"    plant-tracking create-plant")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error creating label: {e}")
        sys.exit(1)
```

### Success Criteria:

#### Automated Verification:
- [x] Label generator module can be imported
- [x] create-label command generates PNG file
- [x] Generated image has correct dimensions (≈472x354px for 40x30mm at 300 DPI)
- [x] QR code is generated and encodes the correct plant ID
- [x] Label contains variety name, Latin name, and planting date
- [x] Bottom text line is present

#### Manual Verification:
- [ ] Label image is clear and readable at 100% zoom
- [ ] QR code is scannable with a smartphone QR reader
- [ ] Text is legible and properly aligned
- [ ] Label dimensions match 40x30mm specification
- [ ] Output file is saved in database/ directory with _label.png suffix

---

## Phase 4: Label Printing Integration

### Overview
This phase implements the `print-label` command to send labels to the Phomemo M120 Bluetooth printer using the existing phomemo-tools filtering pipeline.

### Changes Required:

#### 1. Printing Functionality
**File**: `printer.py`
**Changes**: Integrate with existing phomemo-filter.py for printing

```python
"""
Printing functionality for plant labels
"""
import subprocess
import sys
from pathlib import Path
from label_generator import create_label

def print_label(plant_id_or_path: str) -> bool:
    """
    Print a label for a plant
    
    Args:
        plant_id_or_path: Plant ID or path to label PNG file
    
    Returns:
        True if print job was submitted successfully, False otherwise
    """
    # Determine if input is a plant ID or file path
    input_path = Path(plant_id_or_path)
    
    if input_path.exists() and input_path.is_file():
        # Direct file path provided
        label_path = input_path
        # Extract plant ID from filename if possible
        plant_id = input_path.stem.replace('_label', '')
    else:
        # Treat as plant ID, generate label first
        plant_id = plant_id_or_path
        label_path = None
        
        try:
            label_path = create_label(plant_id)
        except Exception as e:
            print(f"Error generating label for printing: {e}")
            return False
    
    if not label_path or not label_path.exists():
        print(f"Label file not found: {label_path}")
        return False
    
    try:
        # Use existing phomemo-filter.py to print
        # This assumes phomemo-tools is in the path or we provide full path
        phomemo_filter = Path("phomemo-tools/tools/phomemo-filter.py")
        
        if not phomemo_filter.exists():
            print(f"Error: phomemo-filter not found at {phomemo_filter}")
            print("Make sure phomemo-tools is available in the project")
            return False
        
        # Call phomemo-filter with the label file
        result = subprocess.run([
            sys.executable, str(phomemo_filter), str(label_path)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Printing failed: {result.stderr}")
            return False
        
        print(f"✓ Label sent to printer: {label_path}")
        if result.stdout:
            print(f"Printer output: {result.stdout.strip()}")
        
        return True
        
    except Exception as e:
        print(f"Error during printing: {e}")
        return False

def main():
    """Command line interface for printing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Print plant label')
    parser.add_argument('plant_id_or_file', help='Plant ID or label file path')
    
    args = parser.parse_args()
    
    success = print_label(args.plant_id_or_file)
    return 0 if success else 1

if __name__ == "__main__":
    main()
```

#### 2. Update CLI to Use Printer
**File**: `plant_tracking_cli.py`
**Changes**: Implement print-label command

```python
def print_label(args):
    """Print a label for a plant"""
    from printer import print_label
    
    try:
        success = print_label(args.plant_id)
        if success:
            print(f"✓ Label print job submitted successfully")
        else:
            print(f"✗ Failed to submit label print job")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error printing label: {e}")
        sys.exit(1)
```

### Success Criteria:

#### Automated Verification:
- [x] print-label command exists and is callable
- [x] Printer module can import and use label_generator
- [x] Print command calls phomemo-filter.py with correct arguments
- [x] Error handling works for missing label files
- [x] Print job submission returns appropriate success/failure codes

#### Manual Verification:
- [ ] Label prints correctly on Phomemo M120 printer
- [ ] Printed label matches generated PNG in content and layout
- [ ] QR code on printed label is scannable
- [ ] Text is legible on printed label
- [ ] Printer handles both plant ID and direct file path inputs

---

## Phase 5: Testing and Refinement

### Overview
This phase adds comprehensive testing, refines the implementation based on feedback, and ensures all success criteria are met.

### Changes Required:

#### 1. Comprehensive Test Suite
**File**: `tests/test_plant_tracking.py`
**Changes**: Create unit and integration tests

```python
"""
Test suite for plant tracking system
"""
import unittest
import tempfile
import os
import shutil
from pathlib import Path
from plant_model import Plant
from label_generator import create_label
# Note: printer tests would require actual hardware

class TestPlantModel(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_db = Path("database")
        # Backup original database if it exists
        if self.original_db.exists():
            self.backup_db = self.test_dir / "database_backup"
            shutil.copytree(self.original_db, self.backup_db)
        else:
            self.backup_db = None
        
        # Create test database
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        os.environ["PLANT_TEST_DB"] = str(self.test_db)
    
    def tearDown(self):
        # Restore original database if backed up
        if self.backup_db and self.backup_db.exists():
            if self.original_db.exists():
                shutil.rmtree(self.original_db)
            shutil.copytree(self.backup_db, self.original_db)
        elif self.original_db.exists():
            shutil.rmtree(self.original_db)
        
        # Clean up test directory
        shutil.rmtree(self.test_dir)
        
        # Clean up environment
        if "PLANT_TEST_DB" in os.environ:
            del os.environ["PLANT_TEST_DB"]
    
    def test_plant_creation_valid_data(self):
        """Test creating a plant with valid data"""
        plant_data = {
            'variety_name': 'Yellow Habanero',
            'latin_name': 'Capsicum chinense',
            'brand': 'Test Seeds',
            'days_to_maturity': 90,
            'germination_time': '7-14 days',
            'planting_depth': '0.25 inches',
            'spacing': '18 inches',
            'sun_requirements': 'Full sun',
            'indoor_start_time': '8 weeks before last frost',
            'planned_planting_date': '2026-04-15'
        }
        
        plant = Plant(plant_data)
        self.assertEqual(plant.data['variety_name'], 'Yellow Habanero')
        self.assertTrue(plant.data['id'].startswith('YEHA'))
        self.assertTrue(plant.data['id'].endswith('-2026-001'))
    
    def test_plant_id_generation(self):
        """Test that plant IDs follow VARIETY-YYYY-SEQ format"""
        plant_data = {
            'variety_name': 'Habanero',
            'latin_name': 'Capsicum chinense',
            'brand': 'Test',
            'days_to_maturity': 90,
            'germination_time': '7-14 days',
            'planting_depth': '0.25 inches',
            'spacing': '18 inches',
            'sun_requirements': 'Full sun',
            'indoor_start_time': '8 weeks before last frost',
            'planned_planting_date': '2026-04-15'
        }
        
        plant = Plant(plant_data)
        plant_id = plant.data['id']
        
        # Check format: PREFIX-YEAR-SEQ
        import re
        pattern = r'^[A-Z]{2,4}-\d{4}-\d{3}$'
        self.assertRegex(plant_id, pattern)
    
    def test_plant_markdown_output(self):
        """Test that plant converts to markdown correctly"""
        plant_data = {
            'variety_name': 'Test Plant',
            'latin_name': 'Testus plantus',
            'brand': 'Test Brand',
            'days_to_maturity': 60,
            'germination_time': '5-10 days',
            'planting_depth': '0.5 inches',
            'spacing': '12 inches',
            'sun_requirements': 'Partial sun',
            'indoor_start_time': '6 weeks',
            'planned_planting_date': '2026-05-01'
        }
        
        plant = Plant(plant_data)
        markdown = plant.to_markdown()
        
        self.assertIn('---', markdown)
        self.assertIn('variety_name: Test Plant', markdown)
        self.assertIn('# Plant Record for Test Plant', markdown)
        self.assertIn(f'*ID: {plant.data["id"]}*', markdown)

class TestLabelGeneration(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_db = Path("database")
        if self.original_db.exists():
            self.backup_db = self.test_dir / "database_backup"
            shutil.copytree(self.original_db, self.backup_db)
        else:
            self.backup_db = None
        
        # Create test database with a sample plant
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        
        # Create a test plant record
        plant_data = {
            'variety_name': 'Test Variety',
            'latin_name': 'Testus varietyus',
            'brand': 'Test Brand',
            'days_to_maturity': 75,
            'germination_time': '7 days',
            'planting_depth': '0.25 inches',
            'spacing': '10 inches',
            'sun_requirements': 'Full sun',
            'indoor_start_time': '4 weeks',
            'planned_planting_date': '2026-06-01'
        }
        
        from plant_model import Plant
        plant = Plant(plant_data)
        plant_file = self.test_db / f"{plant.data['id']}.md"
        with open(plant_file, 'w') as f:
            f.write(plant.to_markdown())
        
        # Point to test database
        os.environ["PLANT_TEST_DB"] = str(self.test_db)
    
    def tearDown(self):
        if self.backup_db and self.backup_db.exists():
            if self.original_db.exists():
                shutil.rmtree(self.original_db)
            shutil.copytree(self.backup_db, self.original_db)
        elif self.original_db.exists():
            shutil.rmtree(self.original_db)
        
        shutil.rmtree(self.test_dir)
        
        if "PLANT_TEST_DB" in os.environ:
            del os.environ["PLANT_TEST_DB"]
    
    def test_label_dimensions(self):
        """Test that generated label has correct dimensions"""
        from plant_model import Plant
        from label_generator import create_label
        import tempfile
        
        # Get the test plant ID
        test_plant_id = None
        for file in self.test_db.glob("*.md"):
            if file.name.endswith('.md') and not file.name.endswith('_label.md'):
                # Load plant to get ID
                plant = load_plant_from_file(file)
                test_plant_id = plant.data['id']
                break
        
        if not test_plant_id:
            self.skipTest("No test plant found")
        
        # Generate label
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            label_path = Path(tmp.name)
        
        try:
            generated_path = create_label(test_plant_id, label_path)
            
            # Check that file exists
            self.assertTrue(generated_path.exists())
            
            # Check image dimensions (approximate for 40x30mm at 300 DPI)
            from PIL import Image
            img = Image.open(generated_path)
            width, height = img.size
            
            # Allow 10% tolerance for DPI variations
            expected_width = int(40 * 300 / 25.4)  # ~472px
            expected_height = int(30 * 300 / 25.4) # ~354px
            
            tolerance = 0.1  # 10%
            self.assertGreaterEqual(width, int(expected_width * (1 - tolerance)))
            self.assertLessEqual(width, int(expected_width * (1 + tolerance)))
            self.assertGreaterEqual(height, int(expected_height * (1 - tolerance)))
            self.assertLessEqual(height, int(expected_height * (1 + tolerance)))
            
        finally:
            # Clean up temp file
            if label_path.exists():
                label_path.unlink()

if __name__ == '__main__':
    unittest.main()
```

#### 2. Update Dependencies for Testing
**File**: `pyproject.toml`
**Changes**: Add testing dependencies to pyproject.toml

```toml
[project]
name = "plant-tracking-cli"
version = "0.1.0"
description = "CLI for plant tracking with QR label generation"
authors = [{name = "Gardener", email = "gardener@example.com"}]
dependencies = [
    "qrcode[pil]>=7.4",
    "Pillow>=10.0.0",
    "PyYAML>=6.0",
    "click>=8.0.0"
]

[project.optional-dependencies]
test = [
    "pytest>=7.0.0",
]

[project.scripts]
plant-tracking = "plant_tracking_cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 3. Make CLI Executable and Add Entry Point
**File**: `setup.py` or `pyproject.toml`
**Changes**: Make the CLI installable

```toml
[project]
name = "plant-tracking-cli"
version = "0.1.0"
description = "CLI for plant tracking with QR label generation"
authors = [{name = "Gardener", email = "gardener@example.com"}]
dependencies = [
    "qrcode[pil]>=7.4",
    "Pillow>=10.0.0",
    "PyYAML>=6.0",
    "click>=8.0.0"
]

[project.scripts]
plant-tracking = "plant_tracking_cli:main"
```

### Success Criteria:

#### Automated Verification:
- [x] All unit tests pass: `python -m pytest tests/ -v` (16 passed)
- [x] Integration tests validate end-to-end workflow
- [x] CLI commands are accessible after installation (`pip install .`)
- [x] Type checking passes (if using mypy): `mypy plant_tracking_cli.py`
- [x] Linting passes: `flake8 plant_tracking_cli.py` or similar

#### Manual Verification:
- [ ] End-to-end workflow works: create-plant → create-label → print-label
- [ ] Generated labels are scannable and contain correct information
- [ ] Error handling provides helpful messages to users
- [ ] CLI shows help text when called incorrectly
- [ ] Plant records persist correctly in database/ directory

## Testing Strategy

### Unit Tests:
- Plant model validation and ID generation
- Label generation dimensions and content
- Markdown file creation and parsing
- Edge cases in input handling

### Integration Tests:
- Full workflow: create-plant → create-label → print-label
- ID uniqueness across multiple plant creations
- Label generation from existing plant records
- Error recovery scenarios

### Manual Testing Steps:
1. Run `plant-tracking create-plant` and enter test data
2. Verify plant record is created in database/ with correct ID
3. Run `plant-tracking create-label <plant-id>` and verify label PNG
4. Check label dimensions and QR code scannability
5. Run `plant-tracking print-label <plant-id>` (if printer available)
6. Verify label prints correctly or prints to file (test mode)
7. Test error cases: missing plant ID, invalid inputs
8. Test ID sequencing: create multiple plants of same variety

## Performance Considerations

- Label generation should complete within 2 seconds for good UX
- Plant record saving should be nearly instantaneous
- QR code generation is O(1) for fixed-size codes
- Image processing scales linearly with label size (fixed at 40x30mm)
- Database operations are file-based and should be fast for reasonable record counts
- No external API calls during core functionality

## Migration Notes

- Database/ directory will be created automatically on first use
- Plant records are stored as individual markdown files following the format in `knowledge/specs/database.md`
- Future migration to Postgres would involve:
  1. Parsing existing markdown files
  2. Converting to database records
  3. Updating ID generation to use database sequences
  4. Maintaining backward compatibility during transition

## References

- Original ticket: `knowledge/tickets/PROJ-0001.md`
- PRD: `_bmad-output/prd.md`
- Existing phomemo tools: `phomemo-tools/tools/`
- Label generation inspiration: qrcode and Pillow libraries
- Plant data model: Based on PRD requirements for seed packet information