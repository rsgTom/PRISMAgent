"""Custom logging handlers for the PRISMAgent package."""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ...config.logging_config import LogHandlerConfig as ConfigLogHandlerConfig
from ..logging.models import LogHandlerConfig as ModelsLogHandlerConfig


class ContextFilter(logging.Filter):
    """Filter for adding context data to log records."""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """Initialize the context filter.
        
        Args:
            context: Optional initial context data
        """
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context data to the record and return True to allow the record.
        
        Args:
            record: The log record
            
        Returns:
            Always True, as this filter doesn't actually filter anything
        """
        # Add context attribute if it doesn't exist
        if not hasattr(record, "context"):
            setattr(record, "context", {})
            
        # Update with the current context
        getattr(record, "context").update(self.context)
        return True
    
    def update_context(self, new_context: Dict[str, Any]) -> None:
        """Update the context with new data.
        
        Args:
            new_context: New context data to add
        """
        self.context.update(new_context)
    
    def clear_context(self) -> None:
        """Clear all context data."""
        self.context = {}


def create_handler_from_config(
    config: Union[ConfigLogHandlerConfig, ModelsLogHandlerConfig]
) -> logging.Handler:
    """Create a logging handler from a configuration object.
    
    Args:
        config: The handler configuration from either the config or models module
        
    Returns:
        A configured logging handler
        
    Raises:
        ValueError: If an unsupported handler type is specified
    """
    handler_type = config.type.lower()
    handler: logging.Handler
    
    if handler_type == "console":
        handler = logging.StreamHandler(sys.stdout)
    elif handler_type == "file":
        if not config.filename:
            raise ValueError("File path must be specified for file handler")
        
        # Ensure the directory exists
        path = Path(config.filename)
        os.makedirs(path.parent, exist_ok=True)
        
        # Create a rotating file handler if max_bytes is specified
        if config.max_bytes and config.max_bytes > 0:
            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(
                config.filename,
                maxBytes=config.max_bytes,
                backupCount=config.backup_count or 5,
                encoding="utf-8"
            )
        else:
            handler = logging.FileHandler(config.filename, encoding="utf-8")
    elif handler_type == "null":
        handler = logging.NullHandler()
    else:
        raise ValueError(f"Unsupported handler type: {handler_type}")
    
    # Set the log level
    try:
        level = getattr(logging, config.level.strip().upper())
    except (AttributeError, TypeError):
        # Fallback to INFO level if the level is invalid
        level = logging.INFO
    handler.setLevel(level)
    
    # Set up the formatter based on the format string
    if config.format:
        from .formatting import get_formatter
        include_ctx = True  # Default value
        # LogHandlerConfig doesn't have include_context, so we'll use True as default
        handler.setFormatter(get_formatter(
            config.format, 
            include_context=include_ctx
        ))
    
    return handler 