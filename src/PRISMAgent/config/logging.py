"""
PRISMAgent.config.logging
------------------------

Logging configuration for the PRISMAgent package.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator

from . import env


class LogHandlerConfig(BaseModel):
    """Configuration for a log handler."""
    
    type: str = Field(..., description="Handler type: console, file, or external")
    level: str = Field(env.LOG_LEVEL, description="Minimum log level for this handler")
    format: str = Field("default", description="Log format string")
    
    # File handler specific fields
    filename: Optional[str] = Field(None, description="Path to log file (for file handler)")
    max_bytes: Optional[int] = Field(
        env.get_env_int("LOG_ROTATE_MAX_BYTES", 10 * 1024 * 1024),
        description="Maximum size for log file before rotation"
    )
    backup_count: Optional[int] = Field(
        env.get_env_int("LOG_ROTATE_BACKUP_COUNT", 5),
        description="Number of backup files to keep"
    )
    
    # External handler specific fields
    url: Optional[str] = Field(
        env.get_env("LOG_EXTERNAL_URL"),
        description="URL for external log service"
    )
    token: Optional[str] = Field(
        env.get_env("LOG_EXTERNAL_TOKEN"),
        description="Auth token for external log service"
    )
    
    @validator('type')
    def validate_type(cls, v: str) -> str:
        """Validate handler type."""
        if v not in ("console", "file", "external"):
            raise ValueError(f"Invalid handler type: {v}")
        return v
    
    @validator('level')
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()


class LoggingConfig(BaseModel):
    """Configuration for the logging system."""
    
    level: str = Field(env.LOG_LEVEL, description="Global minimum log level")
    handlers: List[LogHandlerConfig] = []
    capture_warnings: bool = Field(
        env.get_env_bool("LOG_CAPTURE_WARNINGS", True),
        description="Capture Python warnings in logs"
    )
    propagate: bool = Field(
        env.get_env_bool("LOG_PROPAGATE", True),
        description="Propagate logs to parent loggers"
    )
    include_context: bool = Field(
        env.get_env_bool("LOG_INCLUDE_CONTEXT", True),
        description="Include context data in logs"
    )
    log_file_path: Optional[str] = Field(
        env.get_env("LOG_PATH", "./logs"),
        description="Default path for log files"
    )
    
    @validator('level')
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()
    
    def model_post_init(self, __context: Any) -> None:
        """Set up default handlers if none are provided."""
        if not self.handlers:
            # Default console handler
            console_handler = LogHandlerConfig(
                type="console",
                level=self.level,
                format=env.get_env("LOG_FORMAT", "default"),
            )
            self.handlers.append(console_handler)
            
            # Add file handler if LOG_FILE is set
            log_file = env.get_env("LOG_FILE")
            if log_file:
                file_handler = LogHandlerConfig(
                    type="file",
                    level=self.level,
                    format=env.get_env("LOG_FORMAT", "default"),
                    filename=log_file,
                )
                self.handlers.append(file_handler)
            
            # Add external handler if LOG_EXTERNAL_URL is set
            log_external_url = env.get_env("LOG_EXTERNAL_URL")
            if log_external_url:
                external_handler = LogHandlerConfig(
                    type="external",
                    level=self.level,
                    format="json",  # Always use JSON for external logging
                    url=log_external_url,
                    token=env.get_env("LOG_EXTERNAL_TOKEN"),
                )
                self.handlers.append(external_handler)


def get_logging_config() -> LoggingConfig:
    """
    Get logging configuration from environment variables.
    
    Returns
    -------
    LoggingConfig
        Logging configuration
    """
    return LoggingConfig()


# Export configuration
logging_config = get_logging_config()
