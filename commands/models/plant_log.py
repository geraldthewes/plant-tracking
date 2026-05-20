"""
SQLAlchemy model for PlantLogEntry entity
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .plant import Plant


class PlantLogEntry(Base, TimestampMixin):
    """PlantLogEntry model matching existing Markdown-based PlantLogEntry class"""

    __tablename__ = "plant_log_entries"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core fields
    plant_id: Mapped[str] = mapped_column(String(20), ForeignKey("plants.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(20), nullable=False)

    # Event-specific fields (sparse columns pattern)
    level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    amount_ml: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fertilizer_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fertilizer_strength: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationship
    plant: Mapped["Plant"] = relationship("Plant")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "(event_type = 'humidity' AND level IS NOT NULL) OR "
            "(event_type = 'water' AND amount_ml IS NOT NULL) OR "
            "(event_type = 'fertilizer' AND fertilizer_type IS NOT NULL AND fertilizer_strength IS NOT NULL) OR "
            "(event_type = 'note' AND text IS NOT NULL)",
            name="check_event_type_fields",
        ),
        CheckConstraint(
            "event_type IN ('humidity', 'water', 'fertilizer', 'note')",
            name="check_event_type",
        ),
        CheckConstraint(
            "(event_type != 'humidity') OR (level >= 1 AND level <= 10)",
            name="check_humidity_level",
        ),
    )

    @classmethod
    def create_from_dict(cls, data: dict) -> "PlantLogEntry":
        """
        Create PlantLogEntry instance from dictionary data
        """
        required_fields = ["plant_id", "event_type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        valid_event_types = {"humidity", "water", "fertilizer", "note"}
        if data["event_type"] not in valid_event_types:
            raise ValueError(
                f"Invalid event_type: {data['event_type']}. "
                f"Must be one of {valid_event_types}"
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
                raise ValueError("Missing required field: amount for water event")

        elif event_type == "fertilizer":
            if "fertilizer_type" not in data:
                raise ValueError("Missing required field: type for fertilizer event")
            if "fertilizer_strength" not in data:
                raise ValueError(
                    "Missing required field: strength for fertilizer event"
                )

        elif event_type == "note":
            if "text" not in data:
                raise ValueError("Missing required field: text for note event")

        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

        return cls(**data)

    @classmethod
    def load_entries(
        cls, plant_id: Optional[str] = None, event_type: Optional[str] = None
    ) -> List["PlantLogEntry"]:
        """
        Load log entries from database
        """
        from sqlalchemy import select

        from commands.database import get_db

        with get_db() as session:
            stmt = select(PlantLogEntry)

            if plant_id:
                stmt = stmt.where(PlantLogEntry.plant_id == plant_id)
            if event_type:
                stmt = stmt.where(PlantLogEntry.event_type == event_type)

            stmt = stmt.order_by(PlantLogEntry.timestamp)
            results = session.execute(stmt).scalars().all()
            return list(results)
