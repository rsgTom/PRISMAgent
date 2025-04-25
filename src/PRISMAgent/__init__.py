"""
PRISMAgent
---------

A modular, multi-agent framework with plug-and-play storage, tools, and UIs.

This package provides a lightweight framework for building and running
AI agents with configurable storage backends, function tools, and interfaces.
"""

# Import all dependencies at the top
from pathlib import Path
from typing import Any, List

from PRISMAgent.config import logging_config
from PRISMAgent.util.logging import LogHandlerConfig as UtilLogHandlerConfig
from PRISMAgent.util.logging import LoggingConfig as UtilLoggingConfig
from PRISMAgent.util.logging import configure_root_logger, get_logger

# Ensure the logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True, parents=True)


# Convert config type to be compatible with util.logging
def convert_config(config: Any) -> UtilLoggingConfig:
    """Convert config.logging_config.LoggingConfig to util.logging.LoggingConfig."""
    # Convert each handler config
    converted_handlers: List[UtilLogHandlerConfig] = []
    for handler in config.handlers:
        converted_handler = UtilLogHandlerConfig(
            type=handler.type,
            level=handler.level,
            format=handler.format,
            filename=handler.filename,
            max_bytes=handler.max_bytes,
            backup_count=handler.backup_count,
            url=handler.url,
            token=handler.token
        )
        converted_handlers.append(converted_handler)
    
    # Create a new LoggingConfig for the util module
    return UtilLoggingConfig(
        level=config.level,
        handlers=converted_handlers,
        capture_warnings=config.capture_warnings,
        propagate=config.propagate,
        include_context=config.include_context,
        log_file_path=config.log_file_path
    )


# Initialize the root logger with our configuration
configure_root_logger(convert_config(logging_config))

# Get a logger for this module
logger = get_logger(__name__)

# Log package initialization
logger.info("PRISMAgent initialized", version="0.1.0")

__version__ = "0.1.0"
