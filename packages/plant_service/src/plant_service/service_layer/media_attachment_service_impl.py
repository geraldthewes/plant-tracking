"""Media attachment service implementation"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from plant_service.adapters.repository.media_attachment_repository import (
    MediaAttachmentRepository,
)
from plant_service.domain import MediaAttachment
from plant_service.service_layer.media_attachment_service import MediaAttachmentService
from plant_service.service_layer.s3_service import S3Service


class MediaAttachmentServiceImpl(MediaAttachmentService):
    """Concrete implementation of media attachment service."""

    def __init__(
        self, repository: MediaAttachmentRepository, s3_service: S3Service
    ):
        self.repository = repository
        self.s3_service = s3_service
        self.allowed_extensions: dict[str, set[str]] = {
            "image": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
            "video": {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"},
            "audio": {".mp3", ".wav", ".ogg", ".flv", ".aac", ".m4a"},
        }

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase."""
        return os.path.splitext(filename)[1].lower()

    def _is_valid_file_type(self, media_type: str, filename: str) -> bool:
        """Check if file extension matches media type."""
        ext = self._get_file_extension(filename)
        return ext in self.allowed_extensions.get(media_type, set())

    def _generate_s3_key(self, plant_id: str, media_type: str, filename: str) -> str:
        """Generate unique S3 key for media file."""
        ext = self._get_file_extension(filename)
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"{plant_id}/{media_type}s/{timestamp}_{unique_id}{ext}"

    def create_media_attachment(self, media_data: dict) -> MediaAttachment:
        """Create a new media attachment with S3 upload."""
        file_path = media_data.pop("file_path")
        filename = media_data.pop("filename")
        media_type = media_data.get("media_type")

        if not self._is_valid_file_type(media_type, filename):
            raise ValueError(f"Invalid file type for {media_type}: {filename}")

        s3_key = self._generate_s3_key(media_data["plant_id"], media_type, filename)

        if not self.s3_service.upload_file(file_path, s3_key):
            raise RuntimeError("Failed to upload file to S3")

        db_media_data = {
            **media_data,
            "s3_key": s3_key,
            "media_type": media_type,
        }

        return self.repository.create_media_attachment(db_media_data)

    def get_media_attachment(self, media_id: int) -> Optional[MediaAttachment]:
        """Get media attachment by ID."""
        return self.repository.get_media_attachment(media_id)

    def get_media_attachments_by_plant(
        self, plant_id: str
    ) -> List[MediaAttachment]:
        """Get all media attachments for a plant."""
        return self.repository.get_media_attachments_by_plant(plant_id)

    def update_media_attachment(
        self, media_id: int, media_data: dict
    ) -> Optional[MediaAttachment]:
        """Update media attachment metadata."""
        media_data.pop("file_path", None)
        media_data.pop("filename", None)
        return self.repository.update_media_attachment(media_id, media_data)

    def delete_media_attachment(self, media_id: int) -> bool:
        """Delete media attachment and associated S3 object."""
        media_attachment = self.get_media_attachment(media_id)
        if not media_attachment:
            return False

        self.s3_service.delete_file(media_attachment.s3_key)
        return self.repository.delete_media_attachment(media_id)

    def get_presigned_url(self, media_id: int, expiration: int = 3600) -> str | None:
        """Get presigned URL for media attachment."""
        media_attachment = self.get_media_attachment(media_id)
        if not media_attachment:
            return None

        return self.s3_service.get_presigned_url(media_attachment.s3_key, expiration)
