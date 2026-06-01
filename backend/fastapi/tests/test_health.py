from fastapi.testclient import TestClient
from plant_tracking_api.main import app


def test_health_check():
    """Test that health check endpoint works."""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root():
    """Test that root endpoint works."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Plant Tracking API"}
