"""Plant repository adapter implementing plant service port"""
from __future__ import annotations

from typing import Iterator
from sqlalchemy.orm import Session
from sqlalchemy import select

from plant_service.domain import Plant as PlantDomain
from plant_service.service_layer.plant_service import PlantService
from .base import BaseRepository
from .models.plant_model import Plant


class PlantRepository(BaseRepository[Plant], PlantService):
    """SQLAlchemy implementation of plant repository"""

    def __init__(self, session: Session):
        super().__init__(session, Plant)

    def create_plant(self, plant_data: dict) -> PlantDomain:
        """Create a new plant record"""
        # Generate ID with sequence from existing records
        abbrev = PlantDomain.make_abbrev(plant_data["variety_name"])
        from datetime import datetime

        planting_date = plant_data.get("planting_date", datetime.now().strftime("%Y-%m-%d"))
        year = datetime.strptime(planting_date, "%Y-%m-%d").year

        existing_ids = self.get_all_ids()
        seq = PlantDomain.find_next_sequence(abbrev, year, existing_ids)

        plant_data["id"] = PlantDomain().generate_id(
            plant_data["variety_name"], planting_date, seq
        )

        domain_obj = PlantDomain.create_from_dict(plant_data)
        orm_obj = Plant(
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
            planting_date=domain_obj.planting_date,
            seed_packet_id=domain_obj.seed_packet_id,
            genus_id=domain_obj.genus_id,
        )
        self.add(orm_obj)
        return domain_obj

    def get_plant(self, plant_id: str) -> PlantDomain | None:
        """Retrieve a plant by ID"""
        result = self.get(plant_id)
        if result:
            return result.to_domain()
        return None

    def list_plants(self) -> Iterator[PlantDomain]:
        """List all plants (returns iterator for streaming)"""
        for orm_plant in self.list_all():
            yield orm_plant.to_domain()

    def update_plant(self, plant_id: str, plant_data: dict) -> PlantDomain | None:
        """Update an existing plant"""
        orm_obj = self.get(plant_id)
        if not orm_obj:
            return None

        for key, value in plant_data.items():
            if hasattr(orm_obj, key) and key not in ("id",):
                setattr(orm_obj, key, value)

        self.update(orm_obj)
        return orm_obj.to_domain()

    def delete_plant(self, plant_id: str) -> bool:
        """Delete a plant by ID"""
        return self.delete(plant_id)

    def find_plant_by_variety_name(self, variety_name: str) -> PlantDomain | None:
        """Find plant by variety name"""
        stmt = select(Plant).where(Plant.variety_name == variety_name)
        result = self.session.execute(stmt).scalar_one_or_none()
        if result:
            return result.to_domain()
        return None
