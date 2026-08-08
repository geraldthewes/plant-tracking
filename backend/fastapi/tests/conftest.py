import pytest
import unittest.mock

import plant_service.domain
from plant_tracking_api.dependencies import get_uow
from plant_tracking_api.main import app


def _mock_uow_with_plants():
    """Create a mock UoW with test plants for API tests."""
    mock_uow = unittest.mock.MagicMock()

    alive_plant = plant_service.domain.Plant(
        id="TO-2026-001",
        variety_name="Tomato",
        latin_name="Solanum lycopersicum",
        planting_date="2026-01-01",
    )

    dead_plant = plant_service.domain.Plant(
        id="PE-2026-001",
        variety_name="Pepper",
        latin_name="Capsicum annuum",
        planting_date="2026-02-01",
        death_date="2026-08-01",
        death_reason="Disease",
        death_comment="Fungal infection",
    )

    mock_uow.plants.list_plants.return_value = iter([alive_plant, dead_plant])

    def get_plant(plant_id):
        if plant_id == "TO-2026-001":
            return alive_plant
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


def test_get_uow_mock():
    """Mock UoW dependency for tests."""
    return None


app.dependency_overrides[get_uow] = test_get_uow_mock


@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def plants_client():
    """Create a test client with mock UoW seeded with plant data."""
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()

    def mock_uow_gen():
        yield mock_uow

    app.dependency_overrides[get_uow] = mock_uow_gen

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
