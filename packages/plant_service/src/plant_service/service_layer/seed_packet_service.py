"""SeedPacket service interface (port) defining seed packet use cases"""
from __future__ import annotations

from typing import Iterator, Protocol, runtime_checkable

from plant_service.domain import SeedPacket


@runtime_checkable
class SeedPacketService(Protocol):
    """Interface for seed packet-related use cases"""

    def create_seed_packet(self, packet_data: dict) -> SeedPacket:
        """Create a new seed packet record"""
        ...

    def get_seed_packet(self, packet_id: str) -> SeedPacket | None:
        """Retrieve a seed packet by ID"""
        ...

    def list_seed_packets(self) -> Iterator[SeedPacket]:
        """List all seed packets (returns iterator for streaming)"""
        ...

    def find_matching(
        self, variety_name: str, latin_name: str
    ) -> SeedPacket | None:
        """Find existing seed packet by variety_name and latin_name"""
        ...
