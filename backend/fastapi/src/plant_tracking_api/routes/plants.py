from fastapi import APIRouter, Depends

from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork
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
