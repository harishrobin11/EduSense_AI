"""Tests for health endpoint."""


def test_root_endpoint(client):
    """Test root GET endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_health_endpoint(client):
    """Test health GET endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert data["app_name"] == "EduSense AI"
    assert "database" in data
    assert data["database"]["connected"] is True
