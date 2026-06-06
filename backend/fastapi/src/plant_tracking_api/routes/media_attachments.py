"""Media attachment API routes"""
import os
import tempfile
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork
from plant_service.service_layer.s3_service import S3Service
from plant_service.service_layer.media_attachment_service_impl import (
    MediaAttachmentServiceImpl,
)
from plant_tracking_api.dependencies import get_uow

router = APIRouter(prefix="/media-attachments", tags=["media-attachments"])


def get_media_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> MediaAttachmentServiceImpl:
    """Create media attachment service for the request."""
    s3_service = S3Service()
    return MediaAttachmentServiceImpl(uow.media_attachments, s3_service)


@router.post("/")
async def create_media_attachment(
    plant_id: str = Form(...),
    media_type: str = Form(...),
    label: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """Create a new media attachment."""
    if media_type not in ("image", "video", "audio"):
        raise HTTPException(status_code=400, detail="Invalid media type")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        s3_service = S3Service()
        media_service = MediaAttachmentServiceImpl(
            uow.media_attachments, s3_service
        )

        media_data = {
            "plant_id": plant_id,
            "media_type": media_type,
            "label": label,
            "tags": tags,
            "file_path": temp_file_path,
            "filename": file.filename or "unknown",
        }

        media_attachment = media_service.create_media_attachment(media_data)
        uow.commit()

        return {
            "id": media_attachment.id,
            "plant_id": media_attachment.plant_id,
            "media_type": media_attachment.media_type,
            "label": media_attachment.label,
            "tags": media_attachment.tags,
            "timestamp": media_attachment.timestamp,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        uow.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/{media_id}")
async def get_media_attachment(
    media_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """Get media attachment by ID."""
    media_attachment = uow.media_attachments.get_media_attachment(media_id)
    if not media_attachment:
        raise HTTPException(status_code=404, detail="Media attachment not found")

    return {
        "id": media_attachment.id,
        "plant_id": media_attachment.plant_id,
        "media_type": media_attachment.media_type,
        "label": media_attachment.label,
        "tags": media_attachment.tags,
        "timestamp": media_attachment.timestamp,
        "s3_key": media_attachment.s3_key,
    }


@router.get("/plant/{plant_id}")
async def get_media_attachments_by_plant(
    plant_id: str,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """Get all media attachments for a plant."""
    media_attachments = uow.media_attachments.get_media_attachments_by_plant(plant_id)

    return [
        {
            "id": ma.id,
            "plant_id": ma.plant_id,
            "media_type": ma.media_type,
            "label": ma.label,
            "tags": ma.tags,
            "timestamp": ma.timestamp,
        }
        for ma in media_attachments
    ]


@router.put("/{media_id}")
async def update_media_attachment(
    media_id: int,
    label: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """Update media attachment metadata."""
    media_data = {}
    if label is not None:
        media_data["label"] = label
    if tags is not None:
        media_data["tags"] = tags

    if not media_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    media_attachment = uow.media_attachments.update_media_attachment(
        media_id, media_data
    )
    if not media_attachment:
        raise HTTPException(status_code=404, detail="Media attachment not found")

    uow.commit()

    return {
        "id": media_attachment.id,
        "plant_id": media_attachment.plant_id,
        "media_type": media_attachment.media_type,
        "label": media_attachment.label,
        "tags": media_attachment.tags,
        "timestamp": media_attachment.timestamp,
    }


@router.delete("/{media_id}")
async def delete_media_attachment(
    media_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """Delete media attachment."""
    media_attachment = uow.media_attachments.get_media_attachment(media_id)
    if not media_attachment:
        raise HTTPException(status_code=404, detail="Media attachment not found")

    s3_service = S3Service()
    s3_service.delete_file(media_attachment.s3_key)

    success = uow.media_attachments.delete_media_attachment(media_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete media attachment")

    uow.commit()

    return {"message": "Media attachment deleted successfully"}


@router.get("/{media_id}/url")
async def get_media_attachment_url(
    media_id: int,
    expiration: int = Form(3600),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """Get presigned URL for media attachment."""
    media_attachment = uow.media_attachments.get_media_attachment(media_id)
    if not media_attachment:
        raise HTTPException(status_code=404, detail="Media attachment not found")

    s3_service = S3Service()
    url = s3_service.get_presigned_url(media_attachment.s3_key, expiration)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate URL")

    return {"url": url}
