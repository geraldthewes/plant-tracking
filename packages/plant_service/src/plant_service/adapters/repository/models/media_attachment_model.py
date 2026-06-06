"""SQLAlchemy ORM models for MediaAttachment entities"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .plant_model import Plant
    from plant_service.domain import MediaAttachment as MediaAttachmentDomain


class MediaAttachment(Base, TimestampMixin):
    """SQLAlchemy MediaAttachment model"""

    __tablename__ = "media_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("plants.id"), nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    plant: Mapped["Plant"] = relationship("Plant")

    __table_args__ = (
        CheckConstraint(
            "media_type IN ('image', 'video', 'audio')",
            name="check_media_type",
        ),
    )

    def to_domain(self) -> "MediaAttachmentDomain":
        """Convert to domain model"""
        from plant_service.domain import MediaAttachment as MediaAttachmentDomain

        return MediaAttachmentDomain(
            id=self.id,
            plant_id=self.plant_id,
            media_type=self.media_type,
            s3_key=self.s3_key,
            timestamp=self.timestamp,
            label=self.label,
            tags=self.tags,
        )
