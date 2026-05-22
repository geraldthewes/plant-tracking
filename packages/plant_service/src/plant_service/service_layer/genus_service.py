"""Genus service interface (port) defining genus-related use cases"""
from __future__ import annotations

from typing import Iterator, Protocol, runtime_checkable

from plant_service.domain import Genus


@runtime_checkable
class GenusService(Protocol):
    """Interface for genus-related use cases"""

    def create_genus(self, genus_data: dict) -> Genus:
        """Create a new genus record"""
        ...

    def get_genus(self, genus_id: str) -> Genus | None:
        """Retrieve a genus by ID"""
        ...

    def list_genera(self) -> Iterator[Genus]:
        """List all genera (returns iterator for streaming)"""
        ...

    def find_matching(
        self, variety_name: str, latin_name: str
    ) -> Genus | None:
        """Find existing genus by variety_name and latin_name"""
        ...

    def find_by_variety_name(self, variety_name: str) -> Genus | None:
        """Find genus by variety name (case-insensitive)"""
        ...
