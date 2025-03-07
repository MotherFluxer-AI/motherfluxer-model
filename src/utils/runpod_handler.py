import runpod
import logging
from ..model.model_manager import ModelManager
from .config import Settings

logger = logging.getLogger(__name__)

def init_model():
    """Initialize the model on RunPod startup"""
    model_manager = ModelManager()
    return model_manager

def inference_handler(event):
    """Handle inference requests from RunPod"""
    try:
        model_manager = init_model()
        
        # Extract input from the event
        input_data = event["input"]
        message = input_data["message"]
        parameters = input_data.get("parameters", {})
        
        # Generate response
        response = model_manager.generate(message, **parameters)
        
        return {
            "status": "success",
            "output": response
        }
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# Initialize RunPod
runpod.serverless(inference_handler) 