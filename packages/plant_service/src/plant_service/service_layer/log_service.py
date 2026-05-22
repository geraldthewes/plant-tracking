"""Log service interface (port) defining log-related use cases"""
from __future__ import annotations

from typing import Iterator, Protocol, runtime_checkable

from plant_service.domain import PlantLogEntry


@runtime_checkable
class LogService(Protocol):
    """Interface for log-related use cases"""

    def create_log_entry(self, log_data: dict) -> PlantLogEntry:
        """Create a new log entry"""
        ...

    def get_log_entry(self, entry_id: int) -> PlantLogEntry | None:
        """Retrieve a log entry by ID"""
        ...

    def list_entries(
        self,
        plant_id: str | None = None,
        event_type: str | None = None,
    ) -> Iterator[PlantLogEntry]:
        """List log entries (returns iterator for streaming)"""
        ...
