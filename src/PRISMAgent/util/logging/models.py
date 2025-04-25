"""Pydantic models for logging configuration."""

from typing import List, Optional

from pydantic import BaseModel, Field

from .constants import DEFAULT_FORMAT, LogLevel


class LogHandlerConfig(BaseModel):
    """Configuration for a log handler."""
    
    type: str = Field(..., description="Handler type: console, file, or external")
    level: str = Field(LogLevel.INFO, description="Minimum log level for this handler")
    format: str = Field(DEFAULT_FORMAT, description="Log format string")
    
    # File handler specific fields
    filename: Optional[str] = Field(None, description="Path to log file (for file handler)")
    max_bytes: Optional[int] = Field(
        10 * 1024 * 1024, 
        description="Maximum size for log file before rotation"
    )
    backup_count: Optional[int] = Field(
        5, 
        description="Number of backup files to keep"
    )
    
    # External handler specific fields
    url: Optional[str] = Field(None, description="URL for external log service")
    token: Optional[str] = Field(None, description="Auth token for external log service")


class LoggingConfig(BaseModel):
    """Configuration for the logging system."""
    
    level: str = Field(LogLevel.INFO, description="Global minimum log level")
    handlers: List[LogHandlerConfig] = Field(
        default_factory=lambda: [
            LogHandlerConfig(
                type="console",
                level=LogLevel.INFO,
                format=DEFAULT_FORMAT,
                filename=None,
                max_bytes=None,
                backup_count=None,
                url=None,
                token=None
            )
        ]
    )
    capture_warnings: bool = Field(True, description="Capture Python warnings in logs")
    propagate: bool = Field(True, description="Propagate logs to parent loggers")
    include_context: bool = Field(True, description="Include context data in logs")
    log_file_path: Optional[str] = Field(None, description="Default path for log files") 