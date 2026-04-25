"""
Seed packet data model and validation
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


SEED_PACKET_FIELDS = [
    'variety_name', 'latin_name', 'brand', 'days_to_maturity',
    'germination_time', 'planting_depth', 'spacing', 'sun_requirements',
    'indoor_start_time'
]

REQUIRED_FIELDS = ['variety_name', 'latin_name']


def get_seed_packets_dir() -> Path:
    """Get the seed packets directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database")) / "seed_packets"


class SeedPacket:
    """Represents a seed packet record"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
        if 'id' not in self.data:
            self.data['id'] = self.generate_id()

    def validate(self):
        """Validate seed packet data"""
        for field in REQUIRED_FIELDS:
            if field not in self.data or not self.data[field]:
                raise ValueError(f"Missing required field: {field}")

    def to_markdown(self) -> str:
        """Convert seed packet data to markdown with YAML frontmatter"""
        now = datetime.now(timezone.utc)

        if 'created_at' not in self.data:
            self.data['created_at'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.data['updated_at'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')

        frontmatter = yaml.dump(self.data, default_flow_style=False, sort_keys=False)
        body = (
            f"# Seed Packet: {self.data['variety_name']}\n\n"
            f"*ID: {self.data['id']}*\n\n"
            f"*Created: {now.strftime('%Y-%m-%d')}*"
        )
        return f"---\n{frontmatter}---\n\n{body}"

    def generate_id(self) -> str:
        """Generate seed packet ID in SPKT-NNN format"""
        seq = self.find_next_sequence()
        return f"SPKT-{seq:03d}"

    def find_next_sequence(self) -> int:
        """Find next sequence number by checking existing seed packet records"""
        pattern = re.compile(r"SPKT-(\d{3})")
        max_seq = 0

        packets_dir = get_seed_packets_dir()
        if packets_dir.exists():
            for file in packets_dir.glob("*.md"):
                try:
                    with open(file, 'r') as f:
                        content = f.read()
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
                    continue

        return max_seq + 1


def find_matching(variety_name: str, latin_name: str) -> Optional[SeedPacket]:
    """Find an existing seed packet matching variety_name and latin_name.
    
    Returns the matching SeedPacket or None if no match exists.
    """
    packets_dir = get_seed_packets_dir()
    if not packets_dir.exists():
        return None

    for file in packets_dir.glob("*.md"):
        try:
            packet = load_from_file(file)
            if (packet.data.get('variety_name') == variety_name and
                    packet.data.get('latin_name') == latin_name):
                return packet
        except Exception:
            continue

    return None


def list_all() -> List[SeedPacket]:
    """Return all seed packets."""
    packets = []
    packets_dir = get_seed_packets_dir()
    if not packets_dir.exists():
        return packets

    for file in sorted(packets_dir.glob("*.md")):
        try:
            packets.append(load_from_file(file))
        except Exception:
            continue

    return packets


def load_from_file(file_path: Path) -> SeedPacket:
    """Load a seed packet record from a markdown file"""
    with open(file_path, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        raise ValueError("Invalid seed packet file format: missing YAML frontmatter")

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError("Invalid seed packet file format: malformed frontmatter")

    frontmatter = parts[1]
    data = yaml.safe_load(frontmatter)
    return SeedPacket(data)
