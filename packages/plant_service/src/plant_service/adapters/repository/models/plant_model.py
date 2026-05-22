"""SQLAlchemy ORM model for Plant entity"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .genus_model import Genus
    from .seed_packet_model import SeedPacket
    from plant_service.domain import Plant as PlantDomain


class Plant(Base, TimestampMixin):
    """SQLAlchemy Plant model matching existing schema"""

    __tablename__ = "plants"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    variety_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latin_name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    days_to_maturity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    germination_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    planting_depth: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    spacing: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sun_requirements: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    indoor_start_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    planting_date: Mapped[str] = mapped_column(String(10), nullable=False)

    seed_packet_id: Mapped[Optional[str]] = mapped_column(
        String(10), ForeignKey("seed_packets.id"), nullable=True
    )
    genus_id: Mapped[Optional[str]] = mapped_column(
        String(10), ForeignKey("genera.id"), nullable=True
    )

    seed_packet: Mapped[Optional["SeedPacket"]] = relationship(
        "SeedPacket", lazy="selectin", back_populates="plants"
    )
    genus: Mapped[Optional["Genus"]] = relationship(
        "Genus", lazy="selectin", back_populates="plants"
    )

    def to_domain(self) -> "PlantDomain":  # noqa: F821
        """Convert to domain model"""
        from plant_service.domain import Plant as PlantDomain

        return PlantDomain(
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
            planting_date=self.planting_date,
            seed_packet_id=self.seed_packet_id,
            genus_id=self.genus_id,
        )
