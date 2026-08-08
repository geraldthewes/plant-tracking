"""
Plant domain model - pure Python with validation, no infrastructure imports
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar


@dataclass(frozen=False)
class Plant:
    """Plant entity matching existing Markdown-based Plant class"""

    REQUIRED_FIELDS: ClassVar[list[str]] = ["variety_name", "latin_name", "planting_date"]

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
    planting_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    seed_packet_id: str | None = None
    genus_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    death_date: str = ""
    death_reason: str = ""
    death_comment: str = ""

    DEATH_REASONS: ClassVar[list[str]] = [
        "Pest infestation",
        "Disease",
        "Overwatering",
        "Underwatering",
        "Frost/cold damage",
        "Heat stress",
        "Transplant shock",
        "Drought",
        "Unknown",
        "Other",
    ]

    def __post_init__(self) -> None:
        """Validate death fields on construction."""
        Plant.validate_death_fields(self.death_date, self.death_reason, self.death_comment)


    @property
    def is_dead(self) -> bool:
        """Return True if the plant has been marked as dead."""
        return bool(self.death_date)

    @staticmethod
    def make_abbrev(variety_name: str) -> str:
        """
        Extract abbreviation from variety name.
        First 2 letters of each word, max 4 chars total.
        """
        words = variety_name.upper().split()
        abbrev = "".join([word[:2] for word in words if word.isalpha()])[:4]
        if not abbrev:
            abbrev = variety_name[:4].upper()
        return abbrev

    def generate_id(self, variety_name: str, planting_date: str, seq: int = 1) -> str:
        """
        Generate plant ID in VARIETY-YYYY-SEQ format.
        Preserves exact logic from commands/models/plant.py:52-69

        Note: seq is passed in from the service layer which queries existing records.
        Default seq=1 is for standalone use (testing/domain layer only).
        """
        abbrev = self.make_abbrev(variety_name)

        if planting_date:
            year = datetime.strptime(planting_date, "%Y-%m-%d").year
        else:
            year = datetime.now().year

        return f"{abbrev}-{year}-{seq:03d}"

    @staticmethod
    def find_next_sequence(abbrev: str, year: int, existing_ids: list[str]) -> int:
        """
        Find next sequence number for given abbreviation and year.
        Takes existing IDs from the repository layer - no DB access here.
        """
        regex_pattern = re.compile(rf"^{re.escape(abbrev)}-{year}-(\d{{3}})$")
        max_seq = 0
        for plant_id in existing_ids:
            match = regex_pattern.match(plant_id)
            if match:
                seq = int(match.group(1))
                max_seq = max(max_seq, seq)
        return max_seq + 1

    @classmethod
    def create_from_dict(cls, data: dict) -> "Plant":
        """
        Create Plant instance from dictionary data.
        Preserves validation logic from commands/models/plant.py:97-124
        """
        # Validate required fields
        for fld in cls.REQUIRED_FIELDS:
            if fld not in data or not data[fld]:
                raise ValueError(f"Missing required field: {fld}")

        # Validate genus_id format if present
        if "genus_id" in data and data["genus_id"] not in (None, "unknown"):
            if not re.match(r"^GENUS-\d{3}$", data["genus_id"]):
                raise ValueError("genus_id must match GENUS-NNN format or be 'unknown'")

        # Validate seed_packet_id format if present
        if "seed_packet_id" in data and data["seed_packet_id"] not in (None, "unknown"):
            if not re.match(r"^SPKT-\d{3}$", data["seed_packet_id"]):
                raise ValueError("seed_packet_id must match SPKT-NNN format")

        # Validate date format
        if "planting_date" in data:
            try:
                datetime.strptime(data["planting_date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format")

        # Validate death_date format if present
        if "death_date" in data and data["death_date"]:
            try:
                datetime.strptime(data["death_date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("death_date must be in YYYY-MM-DD format")

        # Validate death_reason if present
        if "death_reason" in data and data["death_reason"]:
            if data["death_reason"] not in cls.DEATH_REASONS:
                raise ValueError(
                    f"death_reason must be one of: {', '.join(cls.DEATH_REASONS)}"
                )

        # "Other" reason requires a comment
        if (
            "death_reason" in data
            and data["death_reason"] == "Other"
            and not data.get("death_comment")
        ):
            raise ValueError(
                'death_comment is required when death_reason is "Other"'
            )

        # Ensure consistency: death_date requires a death_reason
        if (
            "death_date" in data
            and data["death_date"]
            and not data.get("death_reason")
        ):
            raise ValueError("death_reason is required when death_date is provided")

        return cls(**data)

    @staticmethod
    def validate_death_fields(
        death_date: str,
        death_reason: str,
        death_comment: str = "",
    ) -> None:
        """Validate death-related fields only."""
        if death_date:
            try:
                datetime.strptime(death_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("death_date must be in YYYY-MM-DD format")

        if death_reason:
            if death_reason not in Plant.DEATH_REASONS:
                raise ValueError(
                    f"death_reason must be one of: {', '.join(Plant.DEATH_REASONS)}"
                )

        if death_reason == "Other" and not death_comment:
            raise ValueError(
                'death_comment is required when death_reason is "Other"'
            )

        if death_date and not death_reason:
            raise ValueError("death_reason is required when death_date is provided")
