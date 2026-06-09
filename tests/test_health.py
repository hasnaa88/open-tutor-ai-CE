# tests/test_health.py
"""Tests for health check endpoint."""


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_check_post(client):
    """Test POST health check endpoint."""
    response = client.post("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
