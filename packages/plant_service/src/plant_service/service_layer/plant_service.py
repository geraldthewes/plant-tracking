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

    def list_plants(self, alive_only: bool = False, dead_only: bool = False) -> Iterator[Plant]:
        """List plants with optional alive/dead filtering (returns iterator for streaming).

        Args:
            alive_only: If True, only return plants that are still alive (no death_date).
            dead_only: If True, only return plants that are dead (have death_date set).

        Note:
            If both are False, all plants are returned. Implementations should raise
            ValueError if both alive_only and dead_only are True.

        Returns:
            An iterator yielding Plant objects matching the filter criteria.
        """
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
