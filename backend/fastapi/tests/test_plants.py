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


def test_list_plants_returns_all(plants_client):
    """Test that list plants returns all plants."""
    response = plants_client.get("/api/plants/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["plants"]) == 2


def test_list_plants_alive_only(plants_client):
    """Test that alive_only filter works."""
    response = plants_client.get("/api/plants/?alive_only=true")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["plants"][0]["id"] == "TO-2026-001"
    assert data["plants"][0]["is_dead"] is False


def test_list_plants_dead_only(plants_client):
    """Test that dead_only filter works."""
    response = plants_client.get("/api/plants/?dead_only=true")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["plants"][0]["id"] == "PE-2026-001"
    assert data["plants"][0]["is_dead"] is True


def test_get_plant_returns_plant(plants_client):
    """Test that get plant returns correct data."""
    response = plants_client.get("/api/plants/PE-2026-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "PE-2026-001"
    assert data["variety_name"] == "Pepper"
    assert data["death_date"] == "2026-08-01"
    assert data["death_reason"] == "Disease"
    assert data["death_comment"] == "Fungal infection"
    assert data["is_dead"] is True


def test_get_plant_not_found(plants_client):
    """Test that get plant returns 404 for non-existent plant."""
    response = plants_client.get("/api/plants/NONEXISTENT")
    assert response.status_code == 404


def test_mark_plant_dead(plants_client):
    """Test that mark plant dead works."""
    response = plants_client.patch(
        "/api/plants/TO-2026-001/dead?death_date=2026-08-07&death_reason=Drought&death_comment=Too+hot"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "TO-2026-001"
    assert data["death_date"] == "2026-08-07"
    assert data["death_reason"] == "Drought"
    assert data["death_comment"] == "Too hot"
    assert data["is_dead"] is True


def test_mark_plant_other_with_comment(plants_client):
    """Test that 'Other' reason with valid comment succeeds."""
    response = plants_client.patch(
        "/api/plants/TO-2026-001/dead?death_date=2026-08-07&death_reason=Other&death_comment=Pest+infestation"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "TO-2026-001"
    assert data["death_reason"] == "Other"
    assert data["death_comment"] == "Pest infestation"
    assert data["is_dead"] is True


def test_mark_plant_already_dead(plants_client):
    """Test that marking already dead plant returns 400."""
    response = plants_client.patch(
        "/api/plants/PE-2026-001/dead?death_date=2026-08-07&death_reason=Disease"
    )
    assert response.status_code == 400


def test_mark_plant_invalid_reason(plants_client):
    """Test that invalid death reason returns 422."""
    response = plants_client.patch(
        "/api/plants/TO-2026-001/dead?death_date=2026-08-07&death_reason=InvalidReason"
    )
    assert response.status_code == 422


def test_mark_plant_other_requires_comment(plants_client):
    """Test that 'Other' reason requires comment."""
    response = plants_client.patch(
        "/api/plants/TO-2026-001/dead?death_date=2026-08-07&death_reason=Other&death_comment="
    )
    assert response.status_code == 422


def test_mark_plant_not_found(plants_client):
    """Test that marking non-existent plant returns 404."""
    response = plants_client.patch(
        "/api/plants/NONEXISTENT/dead?death_date=2026-08-07&death_reason=Disease"
    )
    assert response.status_code == 404
