"""
PRISMAgent
---------

A modular, multi-agent framework with plug-and-play storage, tools, and UIs.

This package provides a lightweight framework for building and running
AI agents with configurable storage backends, function tools, and interfaces.
"""

# Initialize the logging system first to ensure it's available throughout the app
from PRISMAgent.config import logging_config
from PRISMAgent.util.logging import configure_root_logger

# Initialize the root logger with our configuration
configure_root_logger(logging_config)

# Now import other modules
from PRISMAgent.util import get_logger

# Get a logger for this module
logger = get_logger(__name__)

# Log package initialization
logger.info("PRISMAgent initialized", version="0.1.0")

__version__ = "0.1.0"
