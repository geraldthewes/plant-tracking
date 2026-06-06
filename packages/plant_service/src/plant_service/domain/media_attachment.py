"""
Media attachment domain models - pure Python with validation, no infrastructure imports
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar


@dataclass(frozen=False)
class MediaAttachment:
    """Base media attachment entity"""

    VALID_MEDIA_TYPES: ClassVar[set[str]] = {"image", "video", "audio"}

    id: int | None = None
    plant_id: str = ""
    media_type: str = ""
    s3_key: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    label: str | None = None
    tags: str | None = None

    def __post_init__(self):
        if self.media_type and self.media_type not in self.VALID_MEDIA_TYPES:
            raise ValueError(
                f"Invalid media_type: {self.media_type}. "
                f"Must be one of {self.VALID_MEDIA_TYPES}"
            )

        if self.plant_id and not isinstance(self.plant_id, str):
            raise ValueError("plant_id must be a non-empty string")

        if self.s3_key and not isinstance(self.s3_key, str):
            raise ValueError("s3_key must be a non-empty string")

        if self.timestamp:
            try:
                datetime.strptime(self.timestamp, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise ValueError("timestamp must be in YYYY-MM-DDTHH:MM:SSZ format")


@dataclass(frozen=False)
class ImageAttachment(MediaAttachment):
    """Image attachment entity"""

    def __post_init__(self):
        self.media_type = "image"
        super().__post_init__()


@dataclass(frozen=False)
class VideoAttachment(MediaAttachment):
    """Video attachment entity"""

    def __post_init__(self):
        self.media_type = "video"
        super().__post_init__()


@dataclass(frozen=False)
class AudioAttachment(MediaAttachment):
    """Audio attachment entity"""

    def __post_init__(self):
        self.media_type = "audio"
        super().__post_init__()
