"""Media attachment service protocol defining the use-case contract"""
from __future__ import annotations

from typing import List, Optional, Protocol, runtime_checkable

from plant_service.domain import MediaAttachment


@runtime_checkable
class MediaAttachmentService(Protocol):
    """Service protocol for media attachment operations."""

    def create_media_attachment(self, media_data: dict) -> MediaAttachment:
        """Create a new media attachment."""
        ...

    def get_media_attachment(self, media_id: int) -> Optional[MediaAttachment]:
        """Get media attachment by ID."""
        ...

    def get_media_attachments_by_plant(self, plant_id: str) -> List[MediaAttachment]:
        """Get all media attachments for a plant."""
        ...

    def update_media_attachment(
        self, media_id: int, media_data: dict
    ) -> Optional[MediaAttachment]:
        """Update media attachment metadata."""
        ...

    def delete_media_attachment(self, media_id: int) -> bool:
        """Delete media attachment and associated S3 object."""
        ...
