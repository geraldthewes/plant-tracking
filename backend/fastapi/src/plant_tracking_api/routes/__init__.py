"""API routes package."""

from .health import router as health_router
from .plants import router as plants_router
from .media_attachments import router as media_attachments_router

__all__ = ["health_router", "plants_router", "media_attachments_router"]
