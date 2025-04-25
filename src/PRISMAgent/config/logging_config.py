"""
PRISMAgent.config.logging_config
----------------------------

Logging configuration for the PRISMAgent package.
"""

from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, field_validator

from . import env


class LogHandlerConfig(BaseModel):
    """Configuration for a log handler."""
    
    type: str = Field(..., description="Handler type: console, file, or external")
    level: str = Field(env.LOG_LEVEL, description="Minimum log level for this handler")
    format: str = Field("default", description="Log format string")
    
    # File handler specific fields
    filename: Optional[str] = Field(
        None, 
        description="Path to log file (for file handler)"
    )
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
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate handler type."""
        if v not in ("console", "file", "external"):
            raise ValueError(f"Invalid handler type: {v}")
        return v
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        # Strip any comments from the log level string
        clean_value = v.split('#')[0].strip().upper()
        
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if clean_value not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return clean_value


class LoggingConfig(BaseModel):
    """Configuration for the logging system."""
    
    level: str = Field(env.LOG_LEVEL, description="Global minimum log level")
    handlers: list[LogHandlerConfig] = []
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
    log_file_path: str = Field(
        env.get_env("LOG_PATH", "logs"),
        description="Default path for log files"
    )
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        # Strip any comments from the log level string
        clean_value = v.split('#')[0].strip().upper()
        
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if clean_value not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return clean_value
    
    def model_post_init(self, __context: Any) -> None:
        """Set up default handlers if none are provided."""
        # Ensure logs directory exists
        log_dir = Path(self.log_file_path)
        log_dir.mkdir(exist_ok=True, parents=True)
        
        if not self.handlers:
            # Default console handler
            console_handler = LogHandlerConfig(
                type="console",
                level=self.level,
                format=env.get_env("LOG_FORMAT", "default"),
                filename=None,
                max_bytes=None,
                backup_count=None,
                url=None,
                token=None
            )
            self.handlers.append(console_handler)
            
            # Always add a file handler to logs directory
            default_log_filename = f"{log_dir}/prism_agent.log"
            file_handler = LogHandlerConfig(
                type="file",
                level=self.level,
                format=env.get_env("LOG_FORMAT", "default"),
                filename=env.get_env("LOG_FILE", default_log_filename),
                max_bytes=env.get_env_int("LOG_ROTATE_MAX_BYTES", 10 * 1024 * 1024),
                backup_count=env.get_env_int("LOG_ROTATE_BACKUP_COUNT", 5),
                url=None,
                token=None
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
                    filename=None,
                    max_bytes=None,
                    backup_count=None
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
    return LoggingConfig(
        level=env.LOG_LEVEL,
        handlers=[],  # Will be populated by model_post_init
        capture_warnings=env.get_env_bool("LOG_CAPTURE_WARNINGS", True),
        propagate=env.get_env_bool("LOG_PROPAGATE", True),
        include_context=env.get_env_bool("LOG_INCLUDE_CONTEXT", True),
        log_file_path=env.get_env("LOG_PATH", "logs")
    )


# Export configuration
logging_config = get_logging_config()
