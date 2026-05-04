"""
Genus data model and validation
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


# All available fields
GENUS_FIELDS = ["variety_name", "latin_name"]

# Required fields
REQUIRED_FIELDS = ["variety_name", "latin_name"]


def get_genera_dir() -> Path:
    """Get the genera directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database")) / "genera"


class Genus:
    """Represents a genus record"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
        # Generate ID if not present
        if "id" not in self.data:
            self.data["id"] = self.generate_id()

    def validate(self):
        """Validate genus data"""
        for field in REQUIRED_FIELDS:
            if field not in self.data or not self.data[field]:
                raise ValueError(f"Missing required field: {field}")

    def to_markdown(self) -> str:
        """Convert genus data to markdown with YAML frontmatter"""
        now = datetime.now(timezone.utc)

        # Set timestamps in ISO 8601 format
        if "created_at" not in self.data:
            self.data["created_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data["updated_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        frontmatter = yaml.dump(self.data, default_flow_style=False, sort_keys=False)
        body = (
            f"# Genus Record for {self.data['variety_name']}\n\n"
            f"*ID: {self.data['id']}*\n\n"
            f"*Created: {now.strftime('%Y-%m-%d')}*"
        )
        return f"---\n{frontmatter}---\n\n{body}"

    def generate_id(self) -> str:
        """Generate genus ID in GENUS-NNN format"""
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
                    with open(file, "r") as f:
                        content = f.read()
                        # Extract YAML frontmatter
                        if content.startswith("---"):
                            parts = content.split("---", 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1]
                                data = yaml.safe_load(frontmatter)
                                if "id" in data:
                                    match = pattern.match(data["id"])
                                    if match:
                                        seq = int(match.group(1))
                                        max_seq = max(max_seq, seq)
                except Exception:
                    continue  # Skip unreadable files

        return max_seq + 1


def find_matching(variety_name: str, latin_name: str) -> Optional["Genus"]:
    """Find existing genus by variety_name and latin_name"""
    genera_dir = get_genera_dir()
    if not genera_dir.exists():
        return None

    for file in genera_dir.glob("*.md"):
        try:
            genus = load_from_file(file)
            if (
                genus.data.get("variety_name") == variety_name
                and genus.data.get("latin_name") == latin_name
            ):
                return genus
        except Exception:
            continue  # Skip unreadable files
    return None


def find_by_variety_name(variety_name: str) -> Optional["Genus"]:
    """Find existing genus by variety_name only (case-insensitive)"""
    genera_dir = get_genera_dir()
    if not genera_dir.exists():
        return None

    for file in genera_dir.glob("*.md"):
        try:
            genus = load_from_file(file)
            if genus.data.get("variety_name", "").lower() == variety_name.lower():
                return genus
        except Exception:
            continue  # Skip unreadable files
    return None


def list_all() -> List["Genus"]:
    """Load all genus records"""
    genera = []
    genera_dir = get_genera_dir()
    if not genera_dir.exists():
        return genera

    for file in sorted(genera_dir.glob("*.md")):
        try:
            genus = load_from_file(file)
            genera.append(genus)
        except Exception:
            continue  # Skip unreadable files
    return genera


def load_from_file(file_path: Path) -> "Genus":
    """Load a genus record from a markdown file"""
    with open(file_path, "r") as f:
        content = f.read()

    if not content.startswith("---"):
        raise ValueError("Invalid genus file format: missing YAML frontmatter")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid genus file format: malformed frontmatter")

    frontmatter = parts[1]
    data = yaml.safe_load(frontmatter)
    return Genus(data)
