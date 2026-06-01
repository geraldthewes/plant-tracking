import pytest

from plant_tracking_api.dependencies import get_uow
from plant_tracking_api.main import app


def test_get_uow_mock():
    """Mock UoW dependency for tests."""
    return None


app.dependency_overrides[get_uow] = test_get_uow_mock


@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)
