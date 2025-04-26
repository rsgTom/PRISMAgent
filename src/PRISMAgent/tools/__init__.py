"""Tools module for PRISMAgent.

This module provides OpenAI function tools that can be used by agents.
"""

from .spawn import spawn_agent
from .factory import tool_factory, list_available_tools
from .code_interpreter import code_interpreter, install_package
from .web_search import web_search, fetch_url
from PRISMAgent.util import get_logger

# Get a logger for this module
logger = get_logger(__name__)

logger.debug("PRISMAgent.tools module initialized")

__all__ = [
    "spawn_agent", 
    "tool_factory", 
    "list_available_tools",
    "code_interpreter",
    "install_package",
    "web_search",
    "fetch_url"
]
