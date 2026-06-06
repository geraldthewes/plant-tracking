"""
PlantLogEntry domain model - pure Python with validation, no infrastructure imports
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar


@dataclass(frozen=False)
class PlantLogEntry:
    """PlantLogEntry entity matching existing SQLAlchemy model.

    Note: For event_type='note', the text field supports markdown formatting.
    """

    VALID_EVENT_TYPES: ClassVar[set[str]] = {"humidity", "water", "fertilizer", "note"}

    id: int | None = None
    plant_id: str = ""
    event_type: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    level: int | None = None
    amount_ml: int | None = None
    fertilizer_type: str | None = None
    fertilizer_strength: str | None = None
    text: str | None = None

    @classmethod
    def create_from_dict(cls, data: dict) -> "PlantLogEntry":
        """
        Create PlantLogEntry instance from dictionary data.
        Preserves validation logic from commands/models/plant_log.py:57-113
        """
        for fld in ("plant_id", "event_type"):
            if fld not in data:
                raise ValueError(f"Missing required field: {fld}")

        if data["event_type"] not in cls.VALID_EVENT_TYPES:
            raise ValueError(
                f"Invalid event_type: {data['event_type']}. "
                f"Must be one of {cls.VALID_EVENT_TYPES}"
            )

        if not isinstance(data["plant_id"], str) or not data["plant_id"]:
            raise ValueError("plant_id must be a non-empty string")

        if "timestamp" in data and data["timestamp"]:
            try:
                datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise ValueError("timestamp must be in YYYY-MM-DDTHH:MM:SSZ format")

        event_type = data["event_type"]

        if event_type == "humidity":
            if "level" not in data:
                raise ValueError("Missing required field: level for humidity event")
            level = data["level"]
            if not isinstance(level, int):
                raise ValueError("Humidity level must be an integer between 1 and 10")
            if level < 1 or level > 10:
                raise ValueError("Humidity level must be between 1 and 10")

        elif event_type == "water":
            if "amount_ml" not in data:
                raise ValueError("Missing required field: amount_ml for water event")

        elif event_type == "fertilizer":
            if "fertilizer_type" not in data:
                raise ValueError("Missing required field: fertilizer_type for fertilizer event")
            if "fertilizer_strength" not in data:
                raise ValueError(
                    "Missing required field: fertilizer_strength for fertilizer event"
                )

        elif event_type == "note":
            if "text" not in data:
                raise ValueError("Missing required field: text for note event")

        if "timestamp" not in data or not data["timestamp"]:
            data["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return cls(**data)
