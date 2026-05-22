"""SeedPacket repository adapter implementing seed packet service port"""
from __future__ import annotations

from typing import Iterator
from sqlalchemy.orm import Session
from sqlalchemy import select

from plant_service.domain import SeedPacket as SeedPacketDomain
from plant_service.service_layer.seed_packet_service import SeedPacketService
from .base import BaseRepository
from .models.seed_packet_model import SeedPacket


class SeedPacketRepository(BaseRepository[SeedPacket], SeedPacketService):
    """SQLAlchemy implementation of seed packet repository"""

    def __init__(self, session: Session):
        super().__init__(session, SeedPacket)

    def create_seed_packet(self, packet_data: dict) -> SeedPacketDomain:
        """Create a new seed packet record"""
        # Generate ID with sequence
        existing_ids = self.get_all_ids()
        seq = SeedPacketDomain.find_next_sequence(existing_ids)
        packet_data["id"] = SeedPacketDomain().generate_id(seq)

        domain_obj = SeedPacketDomain.create_from_dict(packet_data)
        orm_obj = SeedPacket(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
            brand=domain_obj.brand,
            days_to_maturity=domain_obj.days_to_maturity,
            germination_time=domain_obj.germination_time,
            planting_depth=domain_obj.planting_depth,
            spacing=domain_obj.spacing,
            sun_requirements=domain_obj.sun_requirements,
            indoor_start_time=domain_obj.indoor_start_time,
        )
        self.add(orm_obj)
        return domain_obj

    def get_seed_packet(self, packet_id: str) -> SeedPacketDomain | None:
        """Retrieve a seed packet by ID"""
        result = self.get(packet_id)
        if result:
            return result.to_domain()
        return None

    def list_seed_packets(self) -> Iterator[SeedPacketDomain]:
        """List all seed packets (returns iterator for streaming)"""
        for orm_sp in self.list_all():
            yield orm_sp.to_domain()

    def find_matching(
        self, variety_name: str, latin_name: str
    ) -> SeedPacketDomain | None:
        """Find existing seed packet by variety_name and latin_name"""
        stmt = select(SeedPacket).where(
            SeedPacket.variety_name == variety_name,
            SeedPacket.latin_name == latin_name,
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        if result:
            return result.to_domain()
        return None
