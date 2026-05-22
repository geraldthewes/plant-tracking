"""Log repository adapter implementing log service port"""
from __future__ import annotations

from typing import Iterator
from sqlalchemy.orm import Session
from sqlalchemy import select

from plant_service.domain import PlantLogEntry as PlantLogEntryDomain
from plant_service.service_layer.log_service import LogService
from .base import BaseRepository
from .models.plant_log_model import PlantLogEntry


class LogRepository(BaseRepository[PlantLogEntry], LogService):
    """SQLAlchemy implementation of log repository"""

    def __init__(self, session: Session):
        super().__init__(session, PlantLogEntry)

    def create_log_entry(self, log_data: dict) -> PlantLogEntryDomain:
        """Create a new log entry"""
        domain_obj = PlantLogEntryDomain.create_from_dict(log_data)
        orm_obj = PlantLogEntry(
            plant_id=domain_obj.plant_id,
            event_type=domain_obj.event_type,
            timestamp=domain_obj.timestamp,
            level=domain_obj.level,
            amount_ml=domain_obj.amount_ml,
            fertilizer_type=domain_obj.fertilizer_type,
            fertilizer_strength=domain_obj.fertilizer_strength,
            text=domain_obj.text,
        )
        self.add(orm_obj)
        return domain_obj

    def get_log_entry(self, entry_id: int) -> PlantLogEntryDomain | None:
        """Retrieve a log entry by ID"""
        result = self.get(entry_id)
        if result:
            return result.to_domain()
        return None

    def list_entries(
        self,
        plant_id: str | None = None,
        event_type: str | None = None,
    ) -> Iterator[PlantLogEntryDomain]:
        """List log entries (returns iterator for streaming)"""
        stmt = select(PlantLogEntry)
        if plant_id:
            stmt = stmt.where(PlantLogEntry.plant_id == plant_id)
        if event_type:
            stmt = stmt.where(PlantLogEntry.event_type == event_type)
        stmt = stmt.order_by(PlantLogEntry.timestamp)

        for orm_entry in self.session.execute(stmt).scalars().yield_per(100):
            yield orm_entry.to_domain()
