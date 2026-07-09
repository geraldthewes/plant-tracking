"""Composition root - wires everything together"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import get_database_url
from .adapters.repository.uow import SqlAlchemyUnitOfWork
from .service_layer.export_service import ExportService
from .service_layer.s3_service import S3Service
from .service_layer.media_attachment_service_impl import MediaAttachmentServiceImpl


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Create session factory configured with database URL"""
    url = database_url or get_database_url()
    engine = create_engine(
        url,
        pool_pre_ping=True,
        echo=False,
    )
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )


def create_unit_of_work(database_url: str | None = None) -> SqlAlchemyUnitOfWork:
    """Create a Unit of Work instance"""
    session_factory = get_session_factory(database_url)
    return SqlAlchemyUnitOfWork(session_factory)


def create_export_service(database_url: str | None = None) -> ExportService:
    """Create an export service instance"""
    uow = create_unit_of_work(database_url)
    return ExportService(uow)


def create_s3_service() -> S3Service:
    """Create an S3 service instance"""
    return S3Service.from_config()


def create_media_attachment_service(
    database_url: str | None = None,
) -> MediaAttachmentServiceImpl:
    """Create a media attachment service instance (S3 + DB)."""
    s3_service = S3Service.from_config()

    def _factory() -> MediaAttachmentServiceImpl:
        uow = create_unit_of_work(database_url)
        uow.__enter__()
        repo = uow.media_attachments
        return MediaAttachmentServiceImpl(repo, s3_service)

    return _factory()

