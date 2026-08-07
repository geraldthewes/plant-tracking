from unittest.mock import MagicMock

from plant_tracking_api.main import app


def _mock_uow_with_plants():
    """Create a mock UoW with test plants for API tests."""
    from plant_service.domain import Plant as PlantDomain

    mock_uow = MagicMock()

    alive_plant = PlantDomain(
        id="TO-2026-001",
        variety_name="Tomato",
        latin_name="Solanum lycopersicum",
        planting_date="2026-01-01",
    )

    dead_plant = PlantDomain(
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


def _get_mock_uow_factory(mock_uow):
    """Create a generator that yields the mock UoW."""
    def mock_uow_gen():
        yield mock_uow
    return mock_uow_gen


def test_get_plants_needing_care_returns_empty(client):
    """Test that care-needed endpoint returns empty response."""
    response = client.get("/api/plants/care-needed")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["plants"] == []


def test_health_check_endpoint(client):
    """Test that health check endpoint works."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_plants_returns_all():
    """Test that list plants returns all plants."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.get("/api/plants/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["plants"]) == 2
    finally:
        app.dependency_overrides.clear()


def test_list_plants_alive_only():
    """Test that alive_only filter works."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.get("/api/plants/?alive_only=true")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["plants"][0]["id"] == "TO-2026-001"
        assert data["plants"][0]["is_dead"] is False
    finally:
        app.dependency_overrides.clear()


def test_list_plants_dead_only():
    """Test that dead_only filter works."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.get("/api/plants/?dead_only=true")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["plants"][0]["id"] == "PE-2026-001"
        assert data["plants"][0]["is_dead"] is True
    finally:
        app.dependency_overrides.clear()


def test_get_plant_returns_plant():
    """Test that get plant returns correct data."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.get("/api/plants/PE-2026-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PE-2026-001"
        assert data["variety_name"] == "Pepper"
        assert data["death_date"] == "2026-08-01"
        assert data["death_reason"] == "Disease"
        assert data["death_comment"] == "Fungal infection"
        assert data["is_dead"] is True
    finally:
        app.dependency_overrides.clear()


def test_get_plant_not_found():
    """Test that get plant returns 404 for non-existent plant."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.get("/api/plants/NONEXISTENT")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_mark_plant_dead():
    """Test that mark plant dead works."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.patch(
            "/api/plants/TO-2026-001/dead?death_date=2026-08-07&death_reason=Drought&death_comment=Too+hot"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "TO-2026-001"
        assert data["death_date"] == "2026-08-07"
        assert data["death_reason"] == "Drought"
        assert data["is_dead"] is True
    finally:
        app.dependency_overrides.clear()


def test_mark_plant_already_dead():
    """Test that marking already dead plant returns 400."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.patch(
            "/api/plants/PE-2026-001/dead?death_date=2026-08-07&death_reason=Disease"
        )
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_mark_plant_invalid_reason():
    """Test that invalid death reason returns 422."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.patch(
            "/api/plants/TO-2026-001/dead?death_date=2026-08-07&death_reason=InvalidReason"
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_mark_plant_other_requires_comment():
    """Test that 'Other' reason requires comment."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.patch(
            "/api/plants/TO-2026-001/dead?death_date=2026-08-07&death_reason=Other&death_comment="
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_mark_plant_not_found():
    """Test that marking non-existent plant returns 404."""
    from plant_tracking_api.dependencies import get_uow
    from fastapi.testclient import TestClient

    mock_uow = _mock_uow_with_plants()
    app.dependency_overrides[get_uow] = _get_mock_uow_factory(mock_uow)

    try:
        client = TestClient(app)
        response = client.patch(
            "/api/plants/NONEXISTENT/dead?death_date=2026-08-07&death_reason=Disease"
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
