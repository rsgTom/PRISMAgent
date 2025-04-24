# src/PRISMAgent/engine/factory.py
from __future__ import annotations

"""
Factory helpers for creating OpenAI-Agents that comply with PRISMAgent rules:

* All agents are constructed through `agent_factory` (or its alias `spawn_agent`)
  – never instantiate `agents.Agent` directly.
* Every new agent is automatically registered in the active registry so that
  runners, tracing, and memory back-ends can discover it.
"""

from typing import Callable, List, Optional

from agents import Agent  # OpenAI-Agents SDK
from PRISMAgent.storage import registry_factory
from PRISMAgent.tools import tool_factory

__all__ = ["agent_factory", "spawn_agent"]


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _normalize_tools(tools: Optional[List[Callable]]) -> Optional[List[Callable]]:
    """Convert callables to SDK function-tools (idempotent)."""
    if not tools:
        return None

    normalized: List[Callable] = []
    for t in tools:
        # Already a tool? keep as-is.
        if getattr(t, "__agents_tool__", False):
            normalized.append(t)
        else:
            normalized.append(tool_factory(t))
    return normalized


# --------------------------------------------------------------------------- #
# Public factory
# --------------------------------------------------------------------------- #
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
    """
    registry = registry_factory()
    agent = Agent(
        name=name,
        instructions=instructions,
        tools=_normalize_tools(tools),
        handoffs=handoffs or [],
    )
    # Make the agent discoverable by runners / dashboards.
    registry.register_agent(agent)
    return agent


def spawn_agent(**kwargs) -> Agent:  # pragma: no cover
    """Backward-compatibility alias for :func:`agent_factory`."""
    return agent_factory(**kwargs)
