"""Genus repository adapter implementing genus service port"""
from __future__ import annotations

from typing import Iterator
from sqlalchemy.orm import Session
from sqlalchemy import select

from plant_service.domain import Genus as GenusDomain
from plant_service.service_layer.genus_service import GenusService
from .base import BaseRepository
from .models.genus_model import Genus


class GenusRepository(BaseRepository[Genus], GenusService):
    """SQLAlchemy implementation of genus repository"""

    def __init__(self, session: Session):
        super().__init__(session, Genus)

    def create_genus(self, genus_data: dict) -> GenusDomain:
        """Create a new genus record"""
        # Generate ID with sequence
        existing_ids = self.get_all_ids()
        seq = GenusDomain.find_next_sequence(existing_ids)
        genus_data["id"] = GenusDomain().generate_id(seq)

        domain_obj = GenusDomain.create_from_dict(genus_data)
        orm_obj = Genus(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
        )
        self.add(orm_obj)
        return domain_obj

    def get_genus(self, genus_id: str) -> GenusDomain | None:
        """Retrieve a genus by ID"""
        result = self.get(genus_id)
        if result:
            return result.to_domain()
        return None

    def list_genera(self) -> Iterator[GenusDomain]:
        """List all genera (returns iterator for streaming)"""
        for orm_genus in self.list_all():
            yield orm_genus.to_domain()

    def find_matching(
        self, variety_name: str, latin_name: str
    ) -> GenusDomain | None:
        """Find existing genus by variety_name and latin_name"""
        stmt = select(Genus).where(
            Genus.variety_name == variety_name,
            Genus.latin_name == latin_name,
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        if result:
            return result.to_domain()
        return None

    def find_by_variety_name(self, variety_name: str) -> GenusDomain | None:
        """Find genus by variety name (case-insensitive)"""
        stmt = select(Genus).where(Genus.variety_name.ilike(variety_name))
        result = self.session.execute(stmt).scalar_one_or_none()
        if result:
            return result.to_domain()
        return None
