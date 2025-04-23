"""
PRISMAgent.engine.factory
-------------------------

Central factory for creating or retrieving agents.

Key additions
-------------
* Dynamic model selection via MODEL_SETTINGS.get_model_for_task()
* Optional `task` and `complexity` kwargs so callers (or the LLM) can
  influence the tier without hard-coding a model name.
"""

from __future__ import annotations

from typing import Iterable, List, Literal, Sequence

from agents import Agent, AgentHooks, Tool, function_tool
from PRISMAgent.storage import registry_factory
from PRISMAgent.config.model import MODEL_SETTINGS

# ──────────────────────────────────────────────────────────────────────────────
# Registry singleton (backend chosen via STORAGE_BACKEND env-var)
# ──────────────────────────────────────────────────────────────────────────────
_REGISTRY = registry_factory()       # InMemoryRegistry, RedisRegistry, …

# ──────────────────────────────────────────────────────────────────────────────
# Public factory
# ──────────────────────────────────────────────────────────────────────────────
def agent_factory(
    name: str,
    instructions: str,
    *,
    tools: Iterable[Tool] | None = None,
    hooks: Sequence[AgentHooks] | None = None,
    task: str = "chat",
    complexity: Literal["auto", "basic", "advanced"] = "auto",
    model: str | None = None,
) -> Agent:
    """
    Create **or** fetch an `Agent` and store it in the global registry.

    Parameters
    ----------
    name : unique agent handle
    instructions : system prompt
    tools : iterable of `Tool`
    hooks : iterable of `AgentHooks`
    task : logical task category ("chat", "code", "math", "vision", …)
    complexity : force tier ("basic"/"advanced") or "auto"
    model : explicit model override; if None we auto-select

    Returns
    -------
    Agent
    """
    if _REGISTRY.exists(name):
        return _REGISTRY.get(name)

    chosen_model = (
        model
        if model
        else MODEL_SETTINGS.get_model_for_task(task, complexity=complexity)
    )

    agent = Agent(
        name=name,
        instructions=instructions,
        model=chosen_model,
        tools=list(tools or []),
        hooks=list(hooks or []),
    )
    _REGISTRY.register(agent)
    return agent


# ──────────────────────────────────────────────────────────────────────────────
# LLM-callable spawn tool
# ──────────────────────────────────────────────────────────────────────────────
@function_tool
def spawn_agent(
    name: str,
    instructions: str,
    task: str = "chat",
    complexity: Literal["auto", "basic", "advanced"] = "auto",
    model: str | None = None,
) -> str:
    """
    Tool that lets an agent create a new sub-agent on the fly.

    The LLM can specify either `model` directly *or* a logical `task`
    category (plus optional `complexity` tier) and let the factory choose.
    """
    new_agent = agent_factory(
        name=name,
        instructions=instructions,
        task=task,
        complexity=complexity,
        model=model,
    )
    return new_agent.name


__all__: List[str] = ["agent_factory", "spawn_agent"]
