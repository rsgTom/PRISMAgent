"""
PRISMAgent.engine public re-exports.

This module re-exports the public interfaces from the engine submodules,
providing a clean and consistent API for users of the package.
"""

from PRISMAgent.engine.factory import agent_factory, spawn_agent
from PRISMAgent.engine.runner import runner_factory, run_agent
from PRISMAgent.engine.hooks import DynamicHandoffHook, hook_factory
from PRISMAgent.util import get_logger

# Get a logger for this module
logger = get_logger(__name__)

logger.debug("PRISMAgent.engine module initialized")

__all__ = [
    "agent_factory",
    "spawn_agent",
    "runner_factory",
    "run_agent",
    "DynamicHandoffHook",
    "hook_factory",
]