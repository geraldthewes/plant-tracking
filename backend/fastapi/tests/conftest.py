import unittest.mock
from datetime import date

import pytest

import plant_service.domain
from plant_tracking_api.dependencies import get_uow
from plant_tracking_api.main import app


def _mock_uow_with_plants() -> unittest.mock.MagicMock:
    """Create a mock UoW with test plants for API tests."""
    mock_uow = unittest.mock.MagicMock()

    alive_plant = plant_service.domain.Plant(
        id="TO-2026-001",
        variety_name="Tomato",
        latin_name="Solanum lycopersicum",
        planting_date=date(2026, 1, 1),
    )

    alive_plant_2 = plant_service.domain.Plant(
        id="PE-2026-002",
        variety_name="Pepper",
        latin_name="Capsicum annuum",
        planting_date=date(2026, 3, 1),
    )

    dead_plant = plant_service.domain.Plant(
        id="PE-2026-001",
        variety_name="Pepper",
        latin_name="Capsicum annuum",
        planting_date=date(2026, 2, 1),
        death_date=date(2026, 8, 1),
        death_reason="Disease",
        death_comment="Fungal infection",
    )

    mock_uow.plants.list_plants.side_effect = lambda alive_only=False, dead_only=False: iter(
        [p for p in [alive_plant, alive_plant_2, dead_plant]
         if (alive_only and not p.is_dead) or
             (dead_only and p.is_dead) or
             (not alive_only and not dead_only)]
    )

    def get_plant(plant_id):
        if plant_id == "TO-2026-001":
            return alive_plant
        if plant_id == "PE-2026-002":
            return alive_plant_2
        if plant_id == "PE-2026-001":
            return dead_plant
        return None

    def update_plant(plant_id, data):
        plant = get_plant(plant_id)
        if plant:
            for k, v in data.items():
                setattr(plant, k, v)
            return plant
        return None

    mock_uow.plants.get_plant.side_effect = get_plant
    mock_uow.plants.update_plant.side_effect = update_plant
    return mock_uow


@pytest.fixture
def client():
    """Create test client with mocked UoW."""
    from fastapi.testclient import TestClient

    original_overrides = app.dependency_overrides.copy()
    mock_uow = unittest.mock.MagicMock()
    # Configure the mock uow.plants methods to return sensible defaults
    mock_uow.plants.list_plants.side_effect = lambda **kwargs: iter([])
    mock_uow.plants.get_plant.return_value = None
    mock_uow.plants.update_plant.return_value = None

    def mock_get_uow():
        return mock_uow

    app.dependency_overrides[get_uow] = mock_get_uow
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture
def plants_client():
    """Create a test client with mock UoW seeded with plant data."""
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()

    def mock_uow_gen():
        yield mock_uow

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_uow] = mock_uow_gen
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
