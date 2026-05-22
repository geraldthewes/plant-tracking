"""SQLAlchemy ORM model for SeedPacket entity"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .plant_model import Plant
    from plant_service.domain import SeedPacket as SeedPacketDomain


class SeedPacket(Base, TimestampMixin):
    """SQLAlchemy SeedPacket model matching existing schema"""

    __tablename__ = "seed_packets"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    variety_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latin_name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    days_to_maturity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    germination_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    planting_depth: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    spacing: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sun_requirements: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    indoor_start_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    plants: Mapped[List["Plant"]] = relationship(
        "Plant", lazy="selectin", back_populates="seed_packet"
    )

    def to_domain(self) -> "SeedPacketDomain":  # noqa: F821
        """Convert to domain model"""
        from plant_service.domain import SeedPacket as SeedPacketDomain

        return SeedPacketDomain(
            id=self.id,
            variety_name=self.variety_name,
            latin_name=self.latin_name,
            brand=self.brand,
            days_to_maturity=self.days_to_maturity,
            germination_time=self.germination_time,
            planting_depth=self.planting_depth,
            spacing=self.spacing,
            sun_requirements=self.sun_requirements,
            indoor_start_time=self.indoor_start_time,
        )
