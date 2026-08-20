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


def test_head_requests_for_health_check(client):
    """Test HEAD HTTP requests on root and health endpoints for cloud health checks."""
    response_root = client.head("/")
    assert response_root.status_code == 200

    response_health = client.head("/health")
    assert response_health.status_code == 200

