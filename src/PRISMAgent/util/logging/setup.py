"""Logging setup for the PRISMAgent package."""

import logging
import logging.config
import os
import sys
from typing import Dict, List, Optional, Union, Any

from ...config.logging_config import LoggingConfig, LogHandlerConfig
from .handlers import create_handler_from_config, ContextFilter


def configure_logging(config: Optional[LoggingConfig] = None) -> None:
    """Configure the logging system based on the provided configuration.
    
    Args:
        config: The logging configuration to use
    """
    if config is None:
        from ...config.logging_config import get_logging_config
        config = get_logging_config()
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.level)
    
    # Remove all existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
    
    # Add handlers from config
    for handler_config in config.handlers:
        try:
            handler = create_handler_from_config(handler_config)
            root_logger.addHandler(handler)
        except Exception as e:
            print(f"Failed to create handler: {e}", file=sys.stderr)
    
    # Add a context filter if context is enabled
    if config.include_context:
        context_filter = ContextFilter()
        root_logger.addFilter(context_filter)
    
    # Configure warning capture if enabled
    if config.capture_warnings:
        logging.captureWarnings(True)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        A configured logger
    """
    return logging.getLogger(name)


def update_log_context(context: Dict[str, Any]) -> None:
    """Update the global logging context with new data.
    
    Args:
        context: New context data to add
    """
    root_logger = logging.getLogger()
    
    # Find the context filter
    for filter_obj in root_logger.filters:
        if isinstance(filter_obj, ContextFilter):
            filter_obj.update_context(context)
            return
    
    # If no filter found, add one
    context_filter = ContextFilter(context)
    root_logger.addFilter(context_filter)


def clear_log_context() -> None:
    """Clear all data in the global logging context."""
    root_logger = logging.getLogger()
    
    for filter_obj in root_logger.filters:
        if isinstance(filter_obj, ContextFilter):
            filter_obj.clear_context()
            return 