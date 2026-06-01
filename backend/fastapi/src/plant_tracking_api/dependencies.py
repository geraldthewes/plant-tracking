from typing import Generator

from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork
from plant_service.bootstrap import create_unit_of_work


def get_uow() -> Generator[SqlAlchemyUnitOfWork, None, None]:
    """Dependency that provides a UnitOfWork instance per request."""
    uow = create_unit_of_work()
    yield uow
