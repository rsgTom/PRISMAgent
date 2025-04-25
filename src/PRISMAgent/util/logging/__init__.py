"""
PRISMAgent logging system.

This module provides a flexible logging system with support for adding context to logs,
formatting logs as JSON, and configuring multiple log handlers.

Example usage:
-------------
from PRISMAgent.util.logging import get_logger

logger = get_logger(__name__)
logger.info("This is an info message")
logger.error("This is an error message", user_id="12345", action="login")
"""

import logging
import sys

from .constants import LogLevel
from .context import log_context, with_log_context, init_request_context, clear_request_context
from .formatters import ContextFilter, JsonFormatter
from .formatting import get_formatter
from .handlers import create_handler_from_config, ContextFilter as HandlerContextFilter
from .logger import Logger, get_logger, configure_root_logger
from .models import LogHandlerConfig, LoggingConfig
from .setup import (
    configure_logging,
    update_log_context,
    clear_log_context,
)

# Configure the root logger
configure_root_logger()

# Export public API
__all__ = [
    "Logger",
    "get_logger",
    "configure_root_logger",
    "LogLevel",
    "log_context",
    "with_log_context",
    "init_request_context",
    "clear_request_context",
    "ContextFilter",
    "JsonFormatter",
    "get_formatter",
    "LogHandlerConfig",
    "LoggingConfig",
    "create_handler_from_config",
    "HandlerContextFilter",
    "configure_logging",
    "update_log_context",
    "clear_log_context",
] 