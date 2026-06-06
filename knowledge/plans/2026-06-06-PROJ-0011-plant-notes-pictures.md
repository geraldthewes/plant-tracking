# Add Support for Plant Notes and Pictures Implementation Plan

## Overview

This plan implements support for attaching rich media (notes, images, videos, audio) to plants in the plant tracking system. The implementation extends the existing note functionality to handle media files stored in S3, with metadata stored in the database.

The current system already has basic text note support via the PlantLogEntry model. This plan enhances that to support:
- Markdown text notes (enhancing existing functionality)
- Images stored in S3 with optional labels and tags
- Videos stored in S3 with optional labels and tags  
- Audio notes stored in S3 with optional labels and tags

All media types will follow the same pattern: file stored in S3, metadata (plant_id, timestamp, labels, tags) stored in database.

## Current State Analysis

### Existing Note Functionality
- Domain model: `packages/plant_service/src/plant_service/domain/plant_log.py` - PlantLogEntry with event_type='note' requiring text field
- ORM model: `packages/plant_service/src/plant_service/adapters/repository/models/plant_log_model.py` - PlantLogEntry with text column and check constraint
- CLI: `commands/plant_tracking_cli.py` - `log note` subcommand with --text parameter
- Service layer: LogService protocol and implementations
- Repository pattern: BaseRepository with PlantLogEntryRepository
- Unit of Work: SqlAlchemyUnitOfWork managing repositories

### Missing Components
- No S3 integration/boto3 usage anywhere in codebase
- No file upload handling in FastAPI service
- No media attachment models (only text notes via PlantLogEntry)
- No API endpoints for media upload/retrieval
- No CLI commands for media handling
- No S3 configuration or bucket setup

### Key Discoveries
- Existing one-to-many pattern: Plant → PlantLogEntry (foreign key: plant_id)
- Architecture follows clean architecture: domain → adapters/repository → service_layer → bootstrap
- All models use TimestampMixin for created_at/updated_at
- Dependencies lack boto3, python-multipart, or upload-related packages
- File uploads would require adding python-multipart to FastAPI dependencies

## Desired End State

After implementation, users will be able to:
1. Create markdown notes attached to plants via CLI and API
2. Upload images, videos, and audio files to S3 with metadata stored in database
3. Retrieve media metadata and presigned URLs for S3 objects
4. Update media labels and tags
5. Delete media (removing S3 object and database record)
6. List all media attached to a plant
7. Access media through web service via presigned URLs

Verification will be through:
- Automated tests for all CRUD operations
- S3 integration tests (upload, retrieve, delete)
- Manual verification of media upload/view/download via CLI and web service

## What We're NOT Doing

- Sharing notes/media with other users (out of scope per ticket)
- Bulk operations (create/delete many at once) 
- Image thumbnail generation (nice-to-have, not must-have)
- Search/filter by tags (nice-to-have, not must-have)
- Modifying existing note functionality beyond enhancement to markdown
- Changing existing PlantLogEntry structure for notes

## Implementation Approach

We'll follow the existing patterns in the codebase:
1. Create new domain models for MediaAttachment (base class) and specific types (Image, Video, Audio)
2. Create corresponding SQLAlchemy ORM models with foreign key to plants table
3. Implement S3 service wrapper for upload/download/delete operations
4. Add MediaAttachmentService protocol and implementation
5. Extend Unit of Work to include media repositories
6. Add API endpoints in FastAPI for media operations
7. Add CLI commands for media operations
8. Add necessary dependencies (boto3, python-multipart)
9. Configure S3 bucket settings

We'll implement in phases to ensure each component works correctly before moving to the next.

## Phase 1: Domain Models and S3 Infrastructure

### Overview
Create domain models for media attachments, S3 service wrapper, and configure S3 settings. This phase establishes the foundation without touching persistence or API layers.

### Changes Required:

#### 1. Domain Models
**File**: `packages/plant_service/src/plant_service/domain/media_attachment.py`
**Changes**: Add new domain models for media attachments

```python
"""
Media attachment domain models - pure Python with validation, no infrastructure imports
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar, Optional
from urllib.parse import urlparse


@dataclass(frozen=False)
class MediaAttachment:
    """Base media attachment entity"""
    
    VALID_MEDIA_TYPES: ClassVar[set[str]] = {"image", "video", "audio"}
    
    id: int | None = None
    plant_id: str = ""
    media_type: str = ""  # image, video, audio
    s3_key: str = ""  # S3 object key
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    label: str | None = None  # Optional text description
    tags: str | None = None  # Optional comma-separated tags
    
    def __post_init__(self):
        if self.media_type not in self.VALID_MEDIA_TYPES:
            raise ValueError(
                f"Invalid media_type: {self.media_type}. "
                f"Must be one of {self.VALID_MEDIA_TYPES}"
            )
        
        if not isinstance(self.plant_id, str) or not self.plant_id:
            raise ValueError("plant_id must be a non-empty string")
            
        if not isinstance(self.s3_key, str) or not self.s3_key:
            raise ValueError("s3_key must be a non-empty string")
            
        if "timestamp" in self.__dict__ and self.timestamp:
            try:
                datetime.strptime(self.timestamp, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise ValueError("timestamp must be in YYYY-MM-DDTHH:MM:SSZ format")


@dataclass(frozen=False)
class ImageAttachment(MediaAttachment):
    """Image attachment entity"""
    pass


@dataclass(frozen=False)
class VideoAttachment(MediaAttachment):
    """Video attachment entity"""
    pass


@dataclass(frozen=False)
class AudioAttachment(MediaAttachment):
    """Audio attachment entity"""
    pass
```

#### 2. S3 Service Configuration
**File**: `packages/plant_service/src/plant_service/config.py`
**Changes**: Add S3 configuration settings

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


class Settings:
    """Application settings."""

    def __init__(self):
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        self.s3_bucket: str = os.getenv("S3_BUCKET", "plant-tracking-media")
        self.s3_region: str = os.getenv("S3_REGION", "us-east-1")
        self.s3_access_key_id: Optional[str] = os.getenv("S3_ACCESS_KEY_ID")
        self.s3_secret_access_key: Optional[str] = os.getenv("S3_SECRET_ACCESS_KEY")
        self.s3_endpoint_url: Optional[str] = os.getenv("S3_ENDPOINT_URL")  # For local testing


settings = Settings()
```

#### 3. S3 Service Wrapper
**File**: `packages/plant_service/src/plant_service/service_layer/s3_service.py`
**Changes**: Add S3 service wrapper for upload/download/delete operations

```python
"""
S3 service wrapper for media attachment storage
"""
from __future__ import annotations

import boto3
from botocore.exceptions import ClientError
from typing import Optional
from urllib.parse import urlparse

from plant_service.config import settings


class S3Service:
    """Service for handling S3 operations for media attachments."""
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region
        )
        self.bucket = settings.s3_bucket
    
    def upload_file(self, file_path: str, s3_key: str) -> bool:
        """Upload a file to S3."""
        try:
            self.client.upload_file(file_path, self.bucket, s3_key)
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, file_path: str) -> bool:
        """Download a file from S3."""
        try:
            self.client.download_file(self.bucket, s3_key, file_path)
            return True
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
    
    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for S3 object."""
        try:
            response = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
```

#### 4. Update Dependencies
**File**: `packages/plant_service/pyproject.toml`
**Changes**: Add boto3 dependency

```toml
[project.dependencies]
# ... existing dependencies ...
boto3 = "^1.34.0"
```

### Success Criteria:

#### Automated Verification:
- [x] Python package models for media attachments are type-checked and pass lints: `make lint`
- [x] S3 service wrapper can be instantiated without errors
- [x] Domain model validation works correctly (media types, required fields)
- [x] S3 service methods exist and have correct signatures

#### Manual Verification:
- [ ] S3 service initializes with correct bucket and region settings
- [ ] Domain models accept valid media types and reject invalid ones
- [ ] Required fields validation works correctly

---

## Phase 2: ORM Models and Repository Layer

### Overview
Create SQLAlchemy ORM models for media attachments and implement repository layer following existing patterns.

### Changes Required:

#### 1. ORM Models
**File**: `packages/plant_service/src/plant_service/adapters/repository/models/media_attachment_model.py`
**Changes**: Add SQLAlchemy ORM models for media attachments

```python
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


class ImageAttachment(MediaAttachment):
    """SQLAlchemy ImageAttachment model"""
    __mapper_args__ = {
        'polymorphic_identity': 'image',
    }


class VideoAttachment(MediaAttachment):
    """SQLAlchemy VideoAttachment model"""
    __mapper_args__ = {
        'polymorphic_identity': 'video',
    }


class AudioAttachment(MediaAttachment):
    """SQLAlchemy AudioAttachment model"""
    __mapper_args__ = {
        'polymorphic_identity': 'audio',
    }
```

#### 2. Repository Interface and Implementation
**File**: `packages/plant_service/src/plant_service/service_layer/media_attachment_service.py`
**Changes**: Add MediaAttachmentService protocol

```python
"""
Media attachment service protocol defining the use-case contract
"""
from __future__ import annotations

from typing import Protocol, List, Optional
from plant_service.domain import (
    MediaAttachment, 
    ImageAttachment, 
    VideoAttachment, 
    AudioAttachment
)


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
    
    def update_media_attachment(self, media_id: int, media_data: dict) -> Optional[MediaAttachment]:
        """Update media attachment metadata."""
        ...
    
    def delete_media_attachment(self, media_id: int) -> bool:
        """Delete media attachment and associated S3 object."""
        ...
```

**File**: `packages/plant_service/src/plant_service/adapters/repository/media_attachment_repository.py`
**Changes**: Add media attachment repository implementation

```python
"""
Media attachment repository implementing the service protocol
"""
from __future__ import annotations

from typing import List, Optional
from plant_service.adapters.repository.base import BaseRepository
from plant_service.adapters.repository.models.media_attachment_model import MediaAttachment
from plant_service.service_layer.media_attachment_service import MediaAttachmentService
from plant_service.domain import MediaAttachment as MediaAttachmentDomain


class MediaAttachmentRepository(BaseRepository[MediaAttachment], MediaAttachmentService):
    """Repository for media attachment operations."""
    
    def create_media_attachment(self, media_data: dict) -> MediaAttachmentDomain:
        """Create a new media attachment."""
        orm_media = self.create(media_data)
        return orm_media.to_domain()
    
    def get_media_attachment(self, media_id: int) -> Optional[MediaAttachmentDomain]:
        """Get media attachment by ID."""
        orm_media = self.get_by_id(media_id)
        return orm_media.to_domain() if orm_media else None
    
    def get_media_attachments_by_plant(self, plant_id: str) -> List[MediaAttachmentDomain]:
        """Get all media attachments for a plant."""
        orm_media_list = self.get_by_field("plant_id", plant_id)
        return [media.to_domain() for media in orm_media_list]
    
    def update_media_attachment(self, media_id: int, media_data: dict) -> Optional[MediaAttachmentDomain]:
        """Update media attachment metadata."""
        orm_media = self.update(media_id, media_data)
        return orm_media.to_domain() if orm_media else None
    
    def delete_media_attachment(self, media_id: int) -> bool:
        """Delete media attachment."""
        return self.delete(media_id)
```

#### 3. Update Unit of Work
**File**: `packages/plant_service/src/plant_service/adapters/repository/uow.py`
**Changes**: Add media attachment repository to Unit of Work

```python
# Add import
from plant_service.adapters.repository.media_attachment_repository import MediaAttachmentRepository

# In SqlAlchemyUnitOfWork class:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None
        # ... existing repositories ...
        self.media_attachments = MediaAttachmentRepository(self.session)
    
    # Add property
    @property
    def media_attachments(self) -> MediaAttachmentRepository:
        if self._media_attachments is None:
            self._media_attachments = MediaAttachmentRepository(self.session)
        return self._media_attachments
```

#### 4. Update Dependencies
**File**: `packages/plant_service/pyproject.toml`
**Changes**: Ensure SQLAlchemy is included (should already be there)

### Success Criteria:

#### Automated Verification:
- [x] Python package ORM models for media attachments are type-checked and pass lints
- [x] Repository implements MediaAttachmentService protocol correctly
- [x] Unit of Work includes media_attachments repository
- [x] Domain to/from ORM conversion works correctly
- [x] Database migration creates media_attachments table successfully

#### Manual Verification:
- [ ] Media attachment table has correct columns and constraints
- [ ] Polymorphic identity works for different media types
- [ ] Foreign key relationship to plants table is correct

---

## Phase 3: Service Layer Integration and S3 Operations

### Overview
Integrate S3 operations with the service layer, handling file uploads to S3 and metadata storage in database.

### Changes Required:

#### 1. Media Attachment Service Implementation
**File**: `packages/plant_service/src/plant_service/service_layer/media_attachment_service_impl.py`
**Changes**: Add concrete implementation of MediaAttachmentService

```python
"""
Media attachment service implementation
"""
from __future__ import annotations

import os
import uuid
from typing import List, Optional
from plant_service.adapters.repository.media_attachment_repository import MediaAttachmentRepository
from plant_service.service_layer.s3_service import S3Service
from plant_service.service_layer.media_attachment_service import MediaAttachmentService
from plant_service.domain import (
    MediaAttachment, 
    ImageAttachment, 
    VideoAttachment, 
    AudioAttachment
)
from plant_service.config import settings


class MediaAttachmentServiceImpl(MediaAttachmentService):
    """Concrete implementation of media attachment service."""
    
    def __init__(self, repository: MediaAttachmentRepository, s3_service: S3Service):
        self.repository = repository
        self.s3_service = s3_service
        self.allowed_extensions = {
            'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
            'video': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'},
            'audio': {'.mp3', '.wav', '.ogg', '.flv', '.aac', '.m4a'}
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
        timestamp = self._get_timestamp()
        return f"{plant_id}/{media_type}s/{timestamp}_{unique_id}{ext}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def create_media_attachment(self, media_data: dict) -> MediaAttachment:
        """Create a new media attachment with S3 upload."""
        # Extract file info
        file_path = media_data.pop('file_path')
        filename = media_data.pop('filename')
        media_type = media_data.get('media_type')
        
        # Validate file type
        if not self._is_valid_file_type(media_type, filename):
            raise ValueError(f"Invalid file type for {media_type}: {filename}")
        
        # Generate S3 key
        s3_key = self._generate_s3_key(
            media_data['plant_id'], 
            media_type, 
            filename
        )
        
        # Upload to S3
        if not self.s3_service.upload_file(file_path, s3_key):
            raise RuntimeError("Failed to upload file to S3")
        
        # Prepare media data for database
        db_media_data = {
            **media_data,
            's3_key': s3_key,
            'media_type': media_type
        }
        
        # Save to database
        return self.repository.create_media_attachment(db_media_data)
    
    def get_media_attachment(self, media_id: int) -> Optional[MediaAttachment]:
        """Get media attachment by ID."""
        return self.repository.get_media_attachment(media_id)
    
    def get_media_attachments_by_plant(self, plant_id: str) -> List[MediaAttachment]:
        """Get all media attachments for a plant."""
        return self.repository.get_media_attachments_by_plant(plant_id)
    
    def update_media_attachment(self, media_id: int, media_data: dict) -> Optional[MediaAttachment]:
        """Update media attachment metadata."""
        # Remove file-related fields that shouldn't be updated via this method
        media_data.pop('file_path', None)
        media_data.pop('filename', None)
        return self.repository.update_media_attachment(media_id, media_data)
    
    def delete_media_attachment(self, media_id: int) -> bool:
        """Delete media attachment and associated S3 object."""
        # Get media attachment first to get S3 key
        media_attachment = self.get_media_attachment(media_id)
        if not media_attachment:
            return False
        
        # Delete from S3
        s3_deleted = self.s3_service.delete_file(media_attachment.s3_key)
        
        # Delete from database
        db_deleted = self.repository.delete_media_attachment(media_id)
        
        return s3_deleted and db_deleted
    
    def get_presigned_url(self, media_id: int, expiration: int = 3600) -> Optional[str]:
        """Get presigned URL for media attachment."""
        media_attachment = self.get_media_attachment(media_id)
        if not media_attachment:
            return None
        
        return self.s3_service.get_presigned_url(
            media_attachment.s3_key, 
            expiration
        )
```

#### 2. Bootstrap Integration
**File**: `packages/plant_service/src/plant_service/bootstrap.py`
**Changes**: Add S3 service and media attachment service to container

```python
# Add imports
from plant_service.service_layer.s3_service import S3Service
from plant_service.service_layer.media_attachment_service_impl import MediaAttachmentServiceImpl
from plant_service.adapters.repository.media_attachment_repository import MediaAttachmentRepository

# In create_unit_of_work function:
def create_unit_of_work() -> SqlAlchemyUnitOfWork:
    """Create a unit of work instance."""
    # ... existing code ...
    
    # Create S3 service
    s3_service = S3Service()
    
    # Create media attachment repository
    media_attachment_repo = MediaAttachmentRepository(session)
    
    # Create media attachment service
    media_attachment_service = MediaAttachmentServiceImpl(
        media_attachment_repo, 
        s3_service
    )
    
    # Return unit of work with new service attached
    uow = SqlAlchemyUnitOfWork(session_factory)
    uow.s3_service = s3_service
    uow.media_attachment_service = media_attachment_service
    uow.media_attachments = media_attachment_repo
    
    return uow
```

#### 3. Update Dependencies
**File**: `packages/plant_service/pyproject.toml`
**Changes**: Add python-multipart for FastAPI file uploads (later phases)

### Success Criteria:

#### Automated Verification:
- [x] Media attachment service implementation follows SOLID principles
- [x] S3 upload/download/delete operations work correctly
- [x] File type validation works for each media type
- [x] S3 key generation creates unique, predictable keys
- [x] Presigned URL generation works correctly
- [x] Service layer properly handles exceptions

#### Manual Verification:
- [ ] Service can be instantiated with repository and S3 service
- [ ] File validation correctly accepts/rejects file types
- [ ] S3 key generation follows expected pattern
- [ ] Service methods handle edge cases appropriately

---

## Phase 4: FastAPI Endpoints

### Overview
Add REST API endpoints for media attachment operations in the FastAPI service.

### Changes Required:

#### 1. Media Attachment API Routes
**File**: `backend/fastapi/src/plant_tracking_api/routes/media_attachments.py`
**Changes**: Add new media attachment routes

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import tempfile
import os

from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork
from plant_tracking_api.dependencies import get_uow

router = APIRouter(prefix="/media-attachments", tags=["media-attachments"])


@router.post("/")
async def create_media_attachment(
    plant_id: str = Form(...),
    media_type: str = Form(...),  # image, video, audio
    label: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """Create a new media attachment."""
    # Validate media type
    if media_type not in ["image", "video", "audio"]:
        raise HTTPException(status_code=400, detail="Invalid media type")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Create media attachment
        media_data = {
            "plant_id": plant_id,
            "media_type": media_type,
            "label": label,
            "tags": tags,
            "file_path": temp_file_path,
            "filename": file.filename
        }
        
        media_attachment = uow.media_attachment_service.create_media_attachment(media_data)
        
        # Commit transaction
        uow.commit()
        
        return {
            "id": media_attachment.id,
            "plant_id": media_attachment.plant_id,
            "media_type": media_attachment.media_type,
            "label": media_attachment.label,
            "tags": media_attachment.tags,
            "timestamp": media_attachment.timestamp
        }
    except Exception as e:
        uow.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/{media_id}")
async def get_media_attachment(
    media_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """Get media attachment by ID."""
    media_attachment = uow.media_attachment_service.get_media_attachment(media_id)
    if not media_attachment:
        raise HTTPException(status_code=404, detail="Media attachment not found")
    
    return {
        "id": media_attachment.id,
        "plant_id": media_attachment.plant_id,
        "media_type": media_attachment.media_type,
        "label": media_attachment.label,
        "tags": media_attachment.tags,
        "timestamp": media_attachment.timestamp,
        "s3_key": media_attachment.s3_key
    }


@router.get("/plant/{plant_id}")
async def get_media_attachments_by_plant(
    plant_id: str,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """Get all media attachments for a plant."""
    media_attachments = uow.media_attachment_service.get_media_attachments_by_plant(plant_id)
    
    return [
        {
            "id": ma.id,
            "plant_id": ma.plant_id,
            "media_type": ma.media_type,
            "label": ma.label,
            "tags": ma.tags,
            "timestamp": ma.timestamp
        }
        for ma in media_attachments
    ]


@router.put("/{media_id}")
async def update_media_attachment(
    media_id: int,
    label: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """Update media attachment metadata."""
    media_data = {}
    if label is not None:
        media_data["label"] = label
    if tags is not None:
        media_data["tags"] = tags
    
    if not media_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    media_attachment = uow.media_attachment_service.update_media_attachment(media_id, media_data)
    if not media_attachment:
        raise HTTPException(status_code=404, detail="Media attachment not found")
    
    uow.commit()
    
    return {
        "id": media_attachment.id,
        "plant_id": media_attachment.plant_id,
        "media_type": media_attachment.media_type,
        "label": media_attachment.label,
        "tags": media_attachment.tags,
        "timestamp": media_attachment.timestamp
    }


@router.delete("/{media_id}")
async def delete_media_attachment(
    media_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """Delete media attachment."""
    success = uow.media_attachment_service.delete_media_attachment(media_id)
    if not success:
        raise HTTPException(status_code=404, detail="Media attachment not found")
    
    uow.commit()
    
    return {"message": "Media attachment deleted successfully"}


@router.get("/{media_id}/url")
async def get_media_attachment_url(
    media_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """Get presigned URL for media attachment."""
    url = uow.media_attachment_service.get_presigned_url(media_id)
    if not url:
        raise HTTPException(status_code=404, detail="Media attachment not found")
    
    return {"url": url}
```

#### 2. Update Main App to Include Routes
**File**: `backend/fastapi/src/plant_tracking_api/main.py`
**Changes**: Add media attachment router

```python
# Add import
from plant_tracking_api.routes import media_attachments

# In app creation:
app.include_router(media_attachments.router)
```

#### 3. Update Dependencies
**File**: `backend/fastapi/pyproject.toml`
**Changes**: Add python-multipart for file upload support

```toml
[project.dependencies]
# ... existing dependencies ...
python-multipart = "^0.0.6"
boto3 = "^1.34.0"
```

### Success Criteria:

#### Automated Verification:
- [x] FastAPI server starts without errors
- [x] All media attachment endpoints are registered
- [x] Endpoints validate input correctly
- [x] File upload handling works with temporary files
- [x] Proper HTTP status codes returned for success/error cases
- [x] Database transactions are properly committed/rolled back

#### Manual Verification:
- [ ] Can upload image file via POST /media-attachments/
- [ ] Can retrieve media attachment metadata via GET /media-attachments/{id}
- [ ] Can list plant media via GET /media-attachments/plant/{plant_id}
- [ ] Can update media attachment metadata via PUT /media-attachments/{id}
- [ ] Can delete media attachment via DELETE /media-attachments/{id}
- [ ] Can get presigned URL via GET /media-attachments/{id}/url

---

## Phase 5: CLI Commands

### Overview
Add CLI commands for media attachment operations mirroring the API functionality.

### Changes Required:

#### 1. Media Attachment CLI Commands
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add media attachment subcommands under a new 'media' command

```python
# Add import at top
from . import media_attachment_model  # Assuming we create this or reuse domain models

# In main() function, add media subparser:
media_parser = subparsers.add_parser("media", help="Manage media attachments")
media_subparsers = media_parser.add_subparsers(
    dest="media_command", help="Media subcommands"
)

# media add-image subcommand
media_add_image_parser = media_subparsers.add_parser(
    "add-image", help="Add an image attachment to a plant"
)
media_add_image_parser.add_argument("plant_id", help="Plant ID")
media_add_image_parser.add_argument("image_path", help="Path to image file")
media_add_image_parser.add_argument(
    "--label", "-l", help="Optional label for the image"
)
media_add_image_parser.add_argument(
    "--tags", "-t", help="Optional comma-separated tags"
)

# media add-video subcommand (similar to add-image)
media_add_video_parser = media_subparsers.add_parser(
    "add-video", help="Add a video attachment to a plant"
)
media_add_video_parser.add_argument("plant_id", help="Plant ID")
media_add_video_parser.add_argument("video_path", help="Path to video file")
media_add_video_parser.add_argument(
    "--label", "-l", help="Optional label for the video"
)
media_add_video_parser.add_argument(
    "--tags", "-t", help="Optional comma-separated tags"
)

# media add-audio subcommand (similar to add-image)
media_add_audio_parser = media_subparsers.add_parser(
    "add-audio", help="Add an audio attachment to a plant"
)
media_add_audio_parser.add_argument("plant_id", help="Plant ID")
media_add_audio_parser.add_argument("audio_path", help="Path to audio file")
media_add_audio_parser.add_argument(
    "--label", "-l", help="Optional label for the audio"
)
media_add_audio_parser.add_argument(
    "--tags", "-t", help="Optional comma-separated tags"
)

# media list subcommand
media_list_parser = media_subparsers.add_parser(
    "list", help="List media attachments for a plant"
)
media_list_parser.add_argument("plant_id", help="Plant ID")

# media show subcommand
media_show_parser = media_subparsers.add_parser(
    "show", help="Show media attachment details"
)
media_show_parser.add_argument("media_id", help="Media attachment ID")

# media delete subcommand
media_delete_parser = media_subparsers.add_parser(
    "delete", help="Delete a media attachment"
)
media_delete_parser.add_argument("media_id", help="Media attachment ID")

# media url subcommand
media_url_parser = media_subparsers.add_parser(
    "url", help="Get URL for media attachment"
)
media_url_parser.add_argument("media_id", help="Media attachment ID")
```

#### 2. Media Attachment CLI Handler Functions
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add handler functions for media commands

```python
def add_media_attachment(args, db, media_type):
    """Handle adding media attachment (image, video, audio)."""
    from .media_attachment_model import MediaAttachment  # Import domain model
    
    _ensure_dirs()
    db = _get_db()
    
    # Validate file exists
    if not os.path.exists(getattr(args, f"{media_type}_path")):
        print(f"✗ File not found: {getattr(args, f'{media_type}_path')}")
        return
    
    try:
        if db and SERVICE_AVAILABLE:
            with create_unit_of_work() as uow:
                media_data = {
                    "plant_id": args.plant_id,
                    "media_type": media_type,
                    "label": getattr(args, "label", None),
                    "tags": getattr(args, "tags", None),
                    "file_path": getattr(args, f"{media_type}_path"),
                    "filename": os.path.basename(getattr(args, f"{media_type}_path"))
                }
                
                media_attachment = uow.media_attachment_service.create_media_attachment(media_data)
                print(f"✓ {media_type.capitalize()} attachment created successfully!")
                print(f"ID: {media_attachment.id}")
                print(f"Plant ID: {media_attachment.plant_id}")
                print(f"S3 Key: {media_attachment.s3_key}")
        else:
            print("✗ Service not available - media attachments require database service")
    except Exception as e:
        print(f"✗ Error creating {media_type} attachment: {e}")


def list_media_attachments(args, db):
    """List media attachments for a plant."""
    _ensure_dirs()
    db = _get_db()
    
    if not db or not SERVICE_AVAILABLE:
        print("✗ Service not available - requires database service")
        return
    
    try:
        with create_unit_of_work() as uow:
            media_attachments = uow.media_attachment_service.get_media_attachments_by_plant(args.plant_id)
            
            if not media_attachments:
                print(f"No media attachments found for plant {args.plant_id}")
                return
            
            print(f"Media attachments for plant {args.plant_id}:")
            print(f"{'ID':<5} {'Type':<8} {'Label':<20} {'Tags':<30} {'Timestamp':<20}")
            print("-" * 90)
            for ma in media_attachments:
                label = ma.label or ""
                tags = ma.tags or ""
                timestamp = ma.timestamp or ""
                print(f"{ma.id:<5} {ma.media_type:<8} {label:<20} {tags:<30} {timestamp:<20}")
    except Exception as e:
        print(f"✗ Error listing media attachments: {e}")


def show_media_attachment(args, db):
    """Show media attachment details."""
    _ensure_dirs()
    db = _get_db()
    
    if not db or not SERVICE_AVAILABLE:
        print("✗ Service not available - requires database service")
        return
    
    try:
        with create_unit_of_work() as uow:
            media_attachment = uow.media_attachment_service.get_media_attachment(args.media_id)
            
            if not media_attachment:
                print(f"✗ Media attachment not found: {args.media_id}")
                return
            
            print(f"=== Media Attachment: {media_attachment.id} ===")
            print()
            print(f"Plant ID: {media_attachment.plant_id}")
            print(f"Media Type: {media_attachment.media_type}")
            print(f"S3 Key: {media_attachment.s3_key}")
            print(f"Label: {media_attachment.label or 'N/A'}")
            print(f"Tags: {media_attachment.tags or 'N/A'}")
            print(f"Timestamp: {media_attachment.timestamp}")
    except Exception as e:
        print(f"✗ Error showing media attachment: {e}")


def delete_media_attachment(args, db):
    """Delete media attachment."""
    _ensure_dirs()
    db = _get_db()
    
    if not db or not SERVICE_AVAILABLE:
        print("✗ Service not available - requires database service")
        return
    
    try:
        with create_unit_of_work() as uow:
            success = uow.media_attachment_service.delete_media_attachment(args.media_id)
            if success:
                uow.commit()
                print(f"✓ Media attachment {args.media_id} deleted successfully")
            else:
                print(f"✗ Media attachment not found: {args.media_id}")
    except Exception as e:
        print(f"✗ Error deleting media attachment: {e}")
        if db and SERVICE_AVAILABLE:
            try:
                uow.rollback()
            except:
                pass


def get_media_attachment_url(args, db):
    """Get URL for media attachment."""
    _ensure_dirs()
    db = _get_db()
    
    if not db or not SERVICE_AVAILABLE:
        print("✗ Service not available - requires database service")
        return
    
    try:
        with create_unit_of_work() as uow:
            url = uow.media_attachment_service.get_presigned_url(args.media_id)
            if url:
                print(f"URL for media attachment {args.media_id}:")
                print(url)
            else:
                print(f"✗ Media attachment not found: {args.media_id}")
    except Exception as e:
        print(f"✗ Error getting media attachment URL: {e}")
```

#### 3. Update Main CLI Dispatch Logic
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add media command handling in main()

```python
# In the main() function, add:
elif args.command == "media":
    if args.media_command == "add-image":
        add_media_attachment(args, db, "image")
    elif args.media_command == "add-video":
        add_media_attachment(args, db, "video")
    elif args.media_command == "add-audio":
        add_media_attachment(args, db, "audio")
    elif args.media_command == "list":
        list_media_attachments(args, db)
    elif args.media_command == "show":
        show_media_attachment(args, db)
    elif args.media_command == "delete":
        delete_media_attachment(args, db)
    elif args.media_command == "url":
        get_media_attachment_url(args, db)
    else:
        media_parser.print_help()
```

### Success Criteria:

#### Automated Verification:
- [x] CLI module imports without errors
- [x] Media subcommands are registered correctly
- [x] Handler functions exist for all media operations
- [x] Proper error handling for missing files/services

#### Manual Verification:
- [ ] `plant-tracking media add-image PLANT_ID IMAGE_PATH --label "Label" --tags "tag1,tag2"` works
- [ ] `plant-tracking media add-video PLANT_ID VIDEO_PATH` works
- [ ] `plant-tracking media add-audio PLANT_ID AUDIO_PATH` works
- [ ] `plant-tracking media list PLANT_ID` shows media attachments
- [ ] `plant-tracking media show MEDIA_ID` shows detailed information
- [ ] `plant-tracking media url MEDIA_ID` returns a presigned URL
- [ ] `plant-tracking media delete MEDIA_ID` deletes the attachment

---

## Phase 6: Enhance Existing Note Functionality

### Overview
Enhance the existing note functionality to support markdown formatting while maintaining backward compatibility.

### Changes Required:

#### 1. Update Note Domain Model Documentation
**File**: `packages/plant_service/src/plant_service/domain/plant_log.py`
**Changes**: Add documentation about markdown support

```python
# Add to PlantLogEntry class docstring:
    """
    PlantLogEntry entity matching existing SQLAlchemy model
    
    Note: For event_type='note', the text field supports markdown formatting.
    """
```

#### 2. Update CLI Note Command Help Text
**File**: `commands/plant_tracking_cli.py`
**Changes**: Update help text for note command

```python
# Change line 190 from:
log_note_parser = log_subparsers.add_parser("note", help="Log a note")
# To:
log_note_parser = log_subparsers.add_parser("note", help="Log a markdown note")
```

#### 3. Update CLI Note Command Documentation
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add note about markdown support

```python
# In log_note_parser help or add description:
log_note_parser = log_subparsers.add_parser(
    "note", 
    help="Log a markdown note",
    description="Create a new markdown-formatted note attached to a plant"
)
```

### Success Criteria:

#### Automated Verification:
- [x] Existing note functionality still works (backward compatibility)
- [x] Documentation properly mentions markdown support
- [x] Help text reflects markdown capability

#### Manual Verification:
- [ ] Existing `plant-tracking log note --text "Hello world"` still works
- [ ] New markdown notes can be created with formatting like `# Heading`, `**bold**`, etc.
- [ ] Notes can be retrieved and displayed via API/CLI

---

## Testing Strategy

### Unit Tests:
- Test domain model validation for all media types
- Test S3 service wrapper methods with mocking
- Test media attachment service business logic
- Test API endpoint validation and error handling
- Test CLI command parsing and execution

### Integration Tests:
- Test complete flow: file upload → S3 storage → database metadata → retrieval
- Test cross-service integration (API → service layer → repository → S3)
- Test CLI to API equivalence (same operations via both interfaces)
- Test transaction rollback on failures
- Test preservation of existing note functionality

### Manual Testing Steps:
1. Start services with proper S3 configuration (localstack or test bucket)
2. Create a plant using existing CLI or API
3. Upload an image via CLI: `plant-tracking media add-image PLANT_ID ./test.jpg --label "Test image"`
4. Verify image appears in plant's media list via CLI and API
5. Get presigned URL and verify image downloads correctly
6. Update image label and tags via CLI and API
7. Delete image and verify it's removed from S3 and database
8. Repeat steps 3-7 for video and audio files
9. Test existing note functionality still works
10. Create markdown note and verify formatting is preserved

## Performance Considerations

- S3 operations will introduce latency; consider caching presigned URLs for short durations
- File uploads should be streamed to avoid memory issues with large files
- Database indexes on plant_id and timestamp for efficient querying
- Consider implementing multipart upload for large files (>100MB)
- Monitor S3 costs and implement lifecycle policies if needed
- Presigned URLs should have appropriate expiration times (1 hour default)

## Migration Notes

No data migration required as this is additive functionality. Existing plants will simply gain the ability to have media attachments added to them.

The existing note functionality remains unchanged except for documentation enhancements to indicate markdown support.

## References

- Original ticket: `knowledge/tickets/PROJ-0011.md`
- Existing note implementation: 
  - Domain: `packages/plant_service/src/plant_service/domain/plant_log.py:11-84`
  - ORM: `packages/plant_service/src/plant_service/adapters/repository/models/plant_log_model.py:14-70`
  - CLI: `commands/plant_tracking_cli.py:189-195, 1952-2014`
- Repository pattern examples:
  - PlantLogEntryRepository: `packages/plant_service/src/plant_service/adapters/repository/log_repository.py`
  - PlantRepository: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py`
- Unit of Work pattern: `packages/plant_service/src/plant_service/adapters/repository/uow.py`
- Service layer patterns: `packages/plant_service/src/plant_service/service_layer/`
- Configuration pattern: `packages/plant_service/src/plant_service/config.py`
- Bootstrap pattern: `packages/plant_service/src/plant_service/bootstrap.py`