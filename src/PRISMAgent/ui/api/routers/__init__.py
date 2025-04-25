"""
PRISMAgent API Routers
---------------------

Package containing FastAPI routers for different API endpoints.
"""

from . import agents, chat, tools
from PRISMAgent.util import get_logger

# Get a logger for this module
logger = get_logger(__name__)

logger.debug("PRISMAgent.ui.api.routers module initialized")

__all__ = ["agents", "chat", "tools"]