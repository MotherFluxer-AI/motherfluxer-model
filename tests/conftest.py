import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.model.model_manager import ModelManager
from src.utils.config import Settings
from pydantic_settings import BaseSettings

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_settings():
    """Provide test settings"""
    return Settings(
        model_name="microsoft/Phi-3.5-mini-instruct",
        model_revision="main",
        rebuild_model=False,
        instance_id="test-instance",
        auth_token="test-token",
        max_sequence_length=2048,
        default_temperature=0.7
    )

@pytest.fixture
def mock_model_manager(mocker):
    """Create a mocked model manager"""
    manager = ModelManager()
    mocker.patch.object(manager, '_is_ready', return_value=True)
    mocker.patch.object(manager, 'generate', return_value="Test response")
    return manager 