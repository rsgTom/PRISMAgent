"""Base configuration settings for PRISMAgent."""

from typing import Optional
from pydantic import BaseModel, Field


class BaseSettings(BaseModel):
    """Base settings for the PRISMAgent framework.
    
    This class defines common settings used throughout the application.
    Environment variables take precedence over values defined here.
    """
    
    api_key: str = Field(
        ..., 
        description="OpenAI API key", 
        env="OPENAI_API_KEY"
    )
    model_name: str = Field(
        "gpt-4", 
        description="Default model name", 
        env="DEFAULT_MODEL_NAME"
    )
    max_tokens: int = Field(
        1000, 
        description="Default max tokens", 
        env="DEFAULT_MAX_TOKENS"
    )
    temperature: float = Field(
        0.7, 
        description="Default temperature", 
        env="DEFAULT_TEMPERATURE"
    )
    log_level: str = Field(
        "INFO", 
        description="Logging level", 
        env="LOG_LEVEL"
    )
    debug: bool = Field(
        False, 
        description="Debug mode", 
        env="DEBUG_MODE"
    )
    storage_type: str = Field(
        "file", 
        description="Storage backend type (file, redis, supabase, vector)", 
        env="STORAGE_TYPE"
    )
    storage_path: Optional[str] = Field(
        None, 
        description="Path for file storage", 
        env="STORAGE_PATH"
    )
    
    class Config:
        """Configuration for the BaseSettings model."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        allow_mutation = True 