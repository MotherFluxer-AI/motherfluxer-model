from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class ModelConfig(BaseSettings):
    """Model-specific configuration"""
    name: str = Field(
        default="microsoft/phi-2",
        description="Name of the model to use",
        alias="model_name"
    )
    revision: str = Field(
        default="main",
        description="Model revision to use",
        alias="model_revision"
    )
    version: str = Field(
        default="1.0.0",
        description="Model version",
        alias="model_version"
    )
    rebuild: bool = Field(
        default=False,
        description="Whether to rebuild the model",
        alias="rebuild_model"
    )
    
    model_config = ConfigDict(extra='allow')

class ModelParams(BaseSettings):
    """Model generation parameters"""
    max_sequence_length: int = Field(
        default=2048,
        description="Maximum sequence length for generation",
        alias="max_sequence_length"
    )
    default_temperature: float = Field(
        default=0.7,
        description="Default temperature for generation",
        alias="default_temperature"
    )
    
    model_config = ConfigDict(extra='allow')

class ServerConfig(BaseSettings):
    """Server configuration"""
    port: int = Field(
        default=8000,
        description="Port to run the server on",
        alias="port"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host to run the server on",
        alias="host"
    )
    
    model_config = ConfigDict(extra='allow')

class AuthConfig(BaseSettings):
    """Authentication configuration"""
    huggingface_token: str = Field(
        default="",
        description="Hugging Face API token (should be set in .env file)",
        alias="huggingface_token"
    )
    
    model_config = ConfigDict(extra='allow')

class Settings(BaseSettings):
    """Main settings class that combines all configuration"""
    model: ModelConfig = ModelConfig()
    params: ModelParams = ModelParams()
    server: ServerConfig = ServerConfig()
    auth: AuthConfig = AuthConfig()
    
    model_config = ConfigDict(
        env_file=".env",
        protected_namespaces=('settings_',),
        env_nested_delimiter="__",
        extra='allow'
    )