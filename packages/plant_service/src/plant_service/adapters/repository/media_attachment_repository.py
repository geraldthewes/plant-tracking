"""Media attachment repository implementing the service protocol"""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from plant_service.adapters.repository.base import BaseRepository
from plant_service.adapters.repository.models.media_attachment_model import (
    MediaAttachment as MediaAttachmentORM,
)
from plant_service.domain import MediaAttachment as MediaAttachmentDomain
from plant_service.service_layer.media_attachment_service import MediaAttachmentService


class MediaAttachmentRepository(
    BaseRepository[MediaAttachmentORM], MediaAttachmentService
):
    """Repository for media attachment operations."""

    def __init__(self, session: Session):
        super().__init__(session, MediaAttachmentORM)

    def create_media_attachment(self, media_data: dict) -> MediaAttachmentDomain:
        """Create a new media attachment."""
        orm_media = MediaAttachmentORM(
            plant_id=media_data["plant_id"],
            media_type=media_data["media_type"],
            s3_key=media_data["s3_key"],
            timestamp=media_data.get(
                "timestamp",
                MediaAttachmentDomain().timestamp,
            ),
            label=media_data.get("label"),
            tags=media_data.get("tags"),
        )
        self.add(orm_media)
        return orm_media.to_domain()

    def get_media_attachment(self, media_id: int) -> Optional[MediaAttachmentDomain]:
        """Get media attachment by ID."""
        result = self.get(media_id)
        if result:
            return result.to_domain()
        return None

    def get_media_attachments_by_plant(
        self, plant_id: str
    ) -> List[MediaAttachmentDomain]:
        """Get all media attachments for a plant."""
        stmt = (
            select(MediaAttachmentORM)
            .where(MediaAttachmentORM.plant_id == plant_id)
            .order_by(MediaAttachmentORM.timestamp)
        )
        results = self.session.execute(stmt).scalars().all()
        return [media.to_domain() for media in results]

    def update_media_attachment(
        self, media_id: int, media_data: dict
    ) -> Optional[MediaAttachmentDomain]:
        """Update media attachment metadata."""
        orm_media = self.get(media_id)
        if not orm_media:
            return None

        for key, value in media_data.items():
            if hasattr(orm_media, key):
                setattr(orm_media, key, value)

        self.update(orm_media)
        return orm_media.to_domain()

    def delete_media_attachment(self, media_id: int) -> bool:
        """Delete media attachment."""
        return self.delete(media_id)
