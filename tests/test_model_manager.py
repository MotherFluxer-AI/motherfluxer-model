import pytest
from src.model.model_manager import ModelManager

@pytest.mark.asyncio
async def test_model_initialization(mock_model_manager):
    """Test model initialization"""
    assert mock_model_manager.is_ready()

@pytest.mark.asyncio
async def test_model_generation(mock_model_manager):
    """Test text generation"""
    prompt = "Hello, how are you?"
    response = await mock_model_manager.generate(prompt)
    assert isinstance(response, str)
    assert len(response) > 0 