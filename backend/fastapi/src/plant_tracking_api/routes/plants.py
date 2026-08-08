from fastapi import APIRouter, Depends, HTTPException

from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork
from plant_service.domain import Plant as PlantDomain
from plant_tracking_api.dependencies import get_uow

router = APIRouter()


@router.get("/care-needed")
async def get_plants_needing_care(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """
    Get plants needing care attention today.

    Returns mock data or empty response until care threshold logic is defined.
    """
    # TODO: Implement actual care logic once thresholds are defined
    # For now, return empty response as specified

    return {"count": 0, "plants": []}


@router.get("/")
async def list_plants(
    alive_only: bool = False,
    dead_only: bool = False,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """
    List all plants with optional alive/dead filtering.
    """
    plants = list(uow.plants.list_plants(alive_only=alive_only, dead_only=dead_only))

    return {
        "plants": [
            {
                "id": p.id,
                "variety_name": p.variety_name,
                "latin_name": p.latin_name,
                "planting_date": p.planting_date,
                "death_date": p.death_date or None,
                "death_reason": p.death_reason or None,
                "is_dead": p.is_dead,
            }
            for p in plants
        ],
        "count": len(plants),
    }


@router.get("/{plant_id}")
async def get_plant(
    plant_id: str,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """
    Get a specific plant by ID.
    """
    plant = uow.plants.get_plant(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant not found: {plant_id}")

    return {
        "id": plant.id,
        "variety_name": plant.variety_name,
        "latin_name": plant.latin_name,
        "brand": plant.brand,
        "days_to_maturity": plant.days_to_maturity,
        "germination_time": plant.germination_time,
        "planting_depth": plant.planting_depth,
        "spacing": plant.spacing,
        "sun_requirements": plant.sun_requirements,
        "indoor_start_time": plant.indoor_start_time,
        "planting_date": plant.planting_date,
        "seed_packet_id": plant.seed_packet_id,
        "genus_id": plant.genus_id,
        "death_date": plant.death_date or None,
        "death_reason": plant.death_reason or None,
        "death_comment": plant.death_comment or None,
        "is_dead": plant.is_dead,
    }


@router.patch("/{plant_id}/dead")
async def mark_plant_dead(
    plant_id: str,
    death_date: str,
    death_reason: str,
    death_comment: str = "",
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """
    Mark a plant as dead.
    """
    plant = uow.plants.get_plant(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant not found: {plant_id}")

    if plant.is_dead:
        raise HTTPException(
            status_code=400,
            detail=f"Plant {plant_id} is already marked as dead on {plant.death_date}",
        )

    # Validate using domain model
    try:
        PlantDomain.create_from_dict({
            "variety_name": plant.variety_name,
            "latin_name": plant.latin_name,
            "planting_date": plant.planting_date,
            "death_date": death_date,
            "death_reason": death_reason,
            "death_comment": death_comment,
        })
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    updated = uow.plants.update_plant(plant_id, {
        "death_date": death_date,
        "death_reason": death_reason,
        "death_comment": death_comment,
    })

    return {
        "id": updated.id,
        "variety_name": updated.variety_name,
        "death_date": updated.death_date,
        "death_reason": updated.death_reason,
        "death_comment": updated.death_comment,
        "is_dead": updated.is_dead,
    }
