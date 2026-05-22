"""Unit of Work interface and SQLAlchemy implementation"""
from __future__ import annotations

from typing import Protocol

from .plant_service import PlantService
from .genus_service import GenusService
from .seed_packet_service import SeedPacketService
from .log_service import LogService


class UnitOfWork(Protocol):
    """Interface defining transaction boundaries"""

    plants: PlantService
    genera: GenusService
    seed_packets: SeedPacketService
    logs: LogService

    def __enter__(self) -> UnitOfWork:
        """Enter transaction context"""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction context - commit if no exception, rollback otherwise"""
        ...

    def commit(self) -> None:
        """Commit the current transaction"""
        ...

    def rollback(self) -> None:
        """Rollback the current transaction"""
        ...
