"""
Plant data model and validation
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# Fields needed for label generation (all required)
LABEL_FIELDS = ['variety_name', 'latin_name', 'planting_date']

# All available fields (record-keeping)
ALL_FIELDS = [
    'variety_name', 'latin_name', 'brand', 'days_to_maturity',
    'germination_time', 'planting_depth', 'spacing', 'sun_requirements',
    'indoor_start_time', 'planting_date', 'seed_packet_id'
]

# All label fields are required
REQUIRED_FIELDS = ['variety_name', 'latin_name', 'planting_date']

# Fields for record-keeping only (not used in labels)
RECORD_ONLY = [
    'brand', 'days_to_maturity', 'germination_time',
    'planting_depth', 'spacing', 'sun_requirements',
    'indoor_start_time'
]

# Configurable database directory (overridden for testing via PLANT_DATABASE_DIR env var)


def get_database_dir() -> Path:
    """Get the database directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database"))


class Plant:
    """Represents a plant record"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
        # Generate ID if not present
        if 'id' not in self.data:
            self.data['id'] = self.generate_id()

    def validate(self):
        """Validate plant data"""
        for field in REQUIRED_FIELDS:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")

        # Validate date format
        if 'planting_date' in self.data:
            try:
                datetime.strptime(self.data['planting_date'], '%Y-%m-%d')
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format")

    def to_markdown(self) -> str:
        """Convert plant data to markdown with YAML frontmatter"""
        now = datetime.now(timezone.utc)

        # Set timestamps in ISO 8601 format
        if 'created_at' not in self.data:
            self.data['created_at'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.data['updated_at'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')

        frontmatter = yaml.dump(self.data, default_flow_style=False, sort_keys=False)
        body = (
            f"# Plant Record for {self.data['variety_name']}\n\n"
            f"*ID: {self.data['id']}*\n\n"
            f"*Created: {now.strftime('%Y-%m-%d')}*"
        )
        return f"---\n{frontmatter}---\n\n{body}"

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

    def find_next_sequence(self, abbrev: str, year: int) -> int:
        """Find next sequence number for given abbreviation and year"""
        pattern = re.compile(rf"{abbrev}-{year}-(\d{{3}})")
        max_seq = 0

        # Check existing markdown files in database
        database_dir = get_database_dir()
        if database_dir.exists():
            for file in database_dir.glob("*.md"):
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

    def get_seed_packet(self) -> Optional['SeedPacket']:
        """Load and return the referenced SeedPacket, or None."""
        spkt_id = self.data.get('seed_packet_id')
        if not spkt_id or spkt_id == 'unknown':
            return None
        return load_seed_packet(spkt_id)


def load_seed_packet(packet_id: str):
    """Load a seed packet by ID. Returns None if not found."""
    from commands.seed_packet_model import load_from_file, get_seed_packets_dir

    packets_dir = get_seed_packets_dir()
    if not packets_dir.exists():
        return None

    filepath = packets_dir / f"{packet_id}.md"
    if filepath.exists():
        return load_from_file(filepath)
    return None


def load_plant_from_file(file_path: Path) -> Plant:
    """Load a plant record from a markdown file"""
    with open(file_path, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        raise ValueError("Invalid plant file format: missing YAML frontmatter")

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError("Invalid plant file format: malformed frontmatter")

    frontmatter = parts[1]
    data = yaml.safe_load(frontmatter)
    return Plant(data)
