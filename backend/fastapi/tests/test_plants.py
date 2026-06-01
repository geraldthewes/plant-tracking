


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
