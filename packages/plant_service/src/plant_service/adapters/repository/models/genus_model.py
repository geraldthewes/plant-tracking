"""SQLAlchemy ORM model for Genus entity"""
from __future__ import annotations

from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .plant_model import Plant
    from plant_service.domain import Genus as GenusDomain


class Genus(Base, TimestampMixin):
    """SQLAlchemy Genus model matching existing schema"""

    __tablename__ = "genera"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    variety_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latin_name: Mapped[str] = mapped_column(String(100), nullable=False)

    plants: Mapped[List["Plant"]] = relationship(
        "Plant", lazy="selectin", back_populates="genus"
    )

    def to_domain(self) -> "GenusDomain":  # noqa: F821
        """Convert to domain model"""
        from plant_service.domain import Genus as GenusDomain

        return GenusDomain(
            id=self.id,
            variety_name=self.variety_name,
            latin_name=self.latin_name,
        )
