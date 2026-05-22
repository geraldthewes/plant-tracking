"""SQLAlchemy implementation of Unit of Work"""
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from plant_service.service_layer.plant_service import PlantService
from plant_service.service_layer.genus_service import GenusService
from plant_service.service_layer.seed_packet_service import SeedPacketService
from plant_service.service_layer.log_service import LogService

from .plant_repository import PlantRepository
from .genus_repository import GenusRepository
from .seed_packet_repository import SeedPacketRepository
from .log_repository import LogRepository


class SqlAlchemyUnitOfWork(AbstractContextManager):
    """SQLAlchemy implementation of Unit of Work"""

    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory
        self.session: Optional[Session] = None
        self._plants: Optional[PlantService] = None
        self._genera: Optional[GenusService] = None
        self._seed_packets: Optional[SeedPacketService] = None
        self._logs: Optional[LogService] = None

    @property
    def plants(self) -> PlantService:
        if self._plants is None:
            raise RuntimeError("Accessing plants outside of transaction context")
        return self._plants

    @property
    def genera(self) -> GenusService:
        if self._genera is None:
            raise RuntimeError("Accessing genera outside of transaction context")
        return self._genera

    @property
    def seed_packets(self) -> SeedPacketService:
        if self._seed_packets is None:
            raise RuntimeError("Accessing seed_packets outside of transaction context")
        return self._seed_packets

    @property
    def logs(self) -> LogService:
        if self._logs is None:
            raise RuntimeError("Accessing logs outside of transaction context")
        return self._logs

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        """Enter transaction context"""
        self.session = self.session_factory()
        self._plants = PlantRepository(self.session)
        self._genera = GenusRepository(self.session)
        self._seed_packets = SeedPacketRepository(self.session)
        self._logs = LogRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction context"""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        if self.session:
            self.session.close()

    def commit(self) -> None:
        """Commit the current transaction"""
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction"""
        if self.session:
            self.session.rollback()
