# src/PRISMAgent/engine/factory.py
from __future__ import annotations

"""
Factory helpers for creating OpenAI-Agents that comply with PRISMAgent rules:

* All agents are constructed through `agent_factory` (or its alias `spawn_agent`)
  ‣ never instantiate `agents.Agent` directly.
* Every new agent is automatically registered in the active registry so that
  runners, tracing, and memory back-ends can discover it.
"""

from typing import Callable, List, Optional

from agents import Agent  # OpenAI-Agents SDK
from PRISMAgent.storage import registry_factory
from PRISMAgent.tools import tool_factory
from PRISMAgent.util import get_logger, with_log_context
from PRISMAgent.util.exceptions import PRISMAgentError, AgentExistsError, ToolError

# Get a logger for this module
logger = get_logger(__name__)

__all__ = ["agent_factory", "spawn_agent"]


# --------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------- #
def _normalize_tools(tools: Optional[List[Callable]]) -> Optional[List[Callable]]:
    """Convert callables to SDK function-tools (idempotent)."""
    if not tools:
        return None

    try:
        normalized: List[Callable] = []
        for t in tools:
            # Already a tool? keep as-is.
            if getattr(t, "__agents_tool__", False):
                normalized.append(t)
            else:
                normalized.append(tool_factory(t))
        return normalized
    except ToolError as e:
        # Re-raise tool-specific errors
        raise
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Failed to normalize tools: {str(e)}"
        logger.error(error_msg, error=str(e), exc_info=True)
        raise PRISMAgentError(error_msg, details={"error": str(e)})


# --------------------------------------------------------------------- #
# Public factory
# --------------------------------------------------------------------- #
@with_log_context(component="agent_factory")
def agent_factory(
    name: str,
    *,
    instructions: str = "You are a helpful AI agent.",
    tools: Optional[List[Callable]] = None,
    handoffs: Optional[List[Agent]] = None,
) -> Agent:
    """Create **and register** an :class:`agents.Agent` instance.

    Args:
        name: Unique agent identifier.
        instructions: System prompt for the agent.
        tools: Optional list of callables or already-wrapped tools.
        handoffs: Agents this one may delegate tasks to.

    Returns:
        The live `Agent` object.
        
    Raises:
        AgentExistsError: If an agent with the given name already exists.
        ToolError: If there's an issue with tools.
        PRISMAgentError: For other unexpected errors.
    """
    logger.info(f"Creating agent: {name}", agent_name=name)
    
    registry = registry_factory()
    
    # Check if agent already exists
    if registry.exists_sync(name):
        error_msg = f"Agent already exists: {name}"
        logger.warning(error_msg, agent_name=name)
        raise AgentExistsError(name)
    
    try:
        # Normalize tools
        normalized_tools = _normalize_tools(tools)
        if normalized_tools:
            logger.debug(
                f"Agent {name} initialized with {len(normalized_tools)} tools", 
                agent_name=name, 
                tool_count=len(normalized_tools)
            )
        
        # Create the agent
        agent = Agent(
            name=name,
            instructions=instructions,
            tools=normalized_tools,
            handoffs=handoffs or [],
        )
        
        # Make the agent discoverable by runners / dashboards.
        registry.register_agent(agent)
        logger.info(f"Agent {name} registered successfully", agent_name=name)
        
        return agent
    except ToolError:
        # Re-raise tool errors (already logged by tool_factory)
        raise
    except PRISMAgentError:
        # Re-raise PRISMAgent errors 
        raise
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Failed to create agent {name}: {str(e)}"
        logger.error(error_msg, agent_name=name, error=str(e), exc_info=True)
        raise PRISMAgentError(error_msg, details={"agent_name": name, "error": str(e)})


def spawn_agent(**kwargs) -> Agent:  # pragma: no cover
    """Backward-compatibility alias for :func:`agent_factory`."""
    logger.debug("spawn_agent called (alias for agent_factory)")
    return agent_factory(**kwargs)
