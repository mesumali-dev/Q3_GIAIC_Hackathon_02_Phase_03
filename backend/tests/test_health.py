"""
Health endpoint tests for the backend API.

Verifies that the health check endpoint returns the expected response.
"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    """Test that health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_healthy_status():
    """Test that health endpoint returns healthy status."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "healthy"


def test_health_endpoint_returns_timestamp():
    """Test that health endpoint includes a timestamp."""
    response = client.get("/health")
    data = response.json()
    assert "timestamp" in data
    assert data["timestamp"] is not None


def test_health_endpoint_returns_service_info():
    """Test that health endpoint includes service information."""
    response = client.get("/health")
    data = response.json()
    assert data["service"] == "todo-backend"
    assert "version" in data


def test_root_endpoint_returns_200():
    """Test that root endpoint returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200


def test_root_endpoint_returns_api_info():
    """Test that root endpoint returns API information."""
    response = client.get("/")
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
