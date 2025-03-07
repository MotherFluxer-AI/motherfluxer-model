from pydantic_settings import BaseSettings  # Changed from pydantic import BaseSettings due to Pydantic v2 changes

class Settings(BaseSettings):
    # Model configuration
    model_name: str = "microsoft/Phi-3.5-mini-instruct"
    model_revision: str = "main"
    model_version: str = "1.0.0"  # Added for health check endpoint
    rebuild_model: bool = False  # Renamed from model_rebuild to avoid conflicts with Pydantic protected namespace
    
    # Model parameters
    max_sequence_length: int = 2048
    default_temperature: float = 0.7
    
    # Authentication and routing
    instance_id: str = ""
    auth_token: str = ""
    central_router_url: str = "wss://router.motherfluxer.ai"
    huggingface_token: str = ""  # Token should be set in .env file, not in code

    class Config:
        env_file = ".env"