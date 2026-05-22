"""Composition root - wires everything together"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import get_database_url
from .adapters.repository.uow import SqlAlchemyUnitOfWork
from .service_layer.export_service import ExportService


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
