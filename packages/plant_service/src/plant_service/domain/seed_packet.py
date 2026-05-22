"""
SeedPacket domain model - pure Python with validation, no infrastructure imports
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar


@dataclass(frozen=False)
class SeedPacket:
    """SeedPacket entity matching existing SQLAlchemy model"""

    REQUIRED_FIELDS: ClassVar[list[str]] = ["variety_name", "latin_name"]

    id: str = ""
    variety_name: str = ""
    latin_name: str = ""
    brand: str | None = None
    days_to_maturity: str | None = None
    germination_time: str | None = None
    planting_depth: str | None = None
    spacing: str | None = None
    sun_requirements: str | None = None
    indoor_start_time: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def generate_id(self, seq: int = 1) -> str:
        """
        Generate seed packet ID in SPKT-NNN format.
        Note: seq is passed in from the service layer which queries existing records.
        """
        return f"SPKT-{seq:03d}"

    @staticmethod
    def find_next_sequence(existing_ids: list[str]) -> int:
        """
        Find next sequence number for seed packet ID.
        Takes existing IDs from the repository layer - no DB access here.
        """
        regex_pattern = re.compile(r"^SPKT-(\d{3})$")
        max_seq = 0
        for packet_id in existing_ids:
            match = regex_pattern.match(packet_id)
            if match:
                seq = int(match.group(1))
                max_seq = max(max_seq, seq)
        return max_seq + 1

    @classmethod
    def create_from_dict(cls, data: dict) -> "SeedPacket":
        """
        Create SeedPacket instance from dictionary data.
        Preserves validation logic from commands/models/seed_packet.py:71-84
        """
        for fld in cls.REQUIRED_FIELDS:
            if fld not in data or not data[fld]:
                raise ValueError(f"Missing required field: {fld}")

        return cls(**data)
