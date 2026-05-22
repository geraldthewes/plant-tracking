"""Plant service interface (port) defining plant-related use cases"""
from __future__ import annotations

from typing import Iterator, Protocol, runtime_checkable

from plant_service.domain import Plant


@runtime_checkable
class PlantService(Protocol):
    """Interface for plant-related use cases"""

    def create_plant(self, plant_data: dict) -> Plant:
        """Create a new plant record"""
        ...

    def get_plant(self, plant_id: str) -> Plant | None:
        """Retrieve a plant by ID"""
        ...

    def list_plants(self) -> Iterator[Plant]:
        """List all plants (returns iterator for streaming)"""
        ...

    def update_plant(self, plant_id: str, plant_data: dict) -> Plant | None:
        """Update an existing plant"""
        ...

    def delete_plant(self, plant_id: str) -> bool:
        """Delete a plant by ID"""
        ...

    def find_plant_by_variety_name(self, variety_name: str) -> Plant | None:
        """Find plant by variety name"""
        ...
