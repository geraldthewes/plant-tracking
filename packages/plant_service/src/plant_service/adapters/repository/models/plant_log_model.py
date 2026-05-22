"""SQLAlchemy ORM model for PlantLogEntry entity"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .plant_model import Plant
    from plant_service.domain import PlantLogEntry as PlantLogEntryDomain


class PlantLogEntry(Base, TimestampMixin):
    """SQLAlchemy PlantLogEntry model matching existing schema"""

    __tablename__ = "plant_log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("plants.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(20), nullable=False)

    level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    amount_ml: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fertilizer_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fertilizer_strength: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    plant: Mapped["Plant"] = relationship("Plant")  # noqa: F821

    __table_args__ = (
        CheckConstraint(
            "(event_type = 'humidity' AND level IS NOT NULL) OR "
            "(event_type = 'water' AND amount_ml IS NOT NULL) OR "
            "(event_type = 'fertilizer' AND "
            "fertilizer_type IS NOT NULL AND "
            "fertilizer_strength IS NOT NULL) OR "
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

    def to_domain(self) -> "PlantLogEntryDomain":  # noqa: F821
        """Convert to domain model"""
        from plant_service.domain import PlantLogEntry as PlantLogEntryDomain

        return PlantLogEntryDomain(
            id=self.id,
            plant_id=self.plant_id,
            event_type=self.event_type,
            timestamp=self.timestamp,
            level=self.level,
            amount_ml=self.amount_ml,
            fertilizer_type=self.fertilizer_type,
            fertilizer_strength=self.fertilizer_strength,
            text=self.text,
        )
