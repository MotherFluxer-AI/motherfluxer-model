from fastapi.testclient import TestClient
import pytest

def test_health_check(test_client: TestClient):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "model_loaded" in data
    assert "version" in data 