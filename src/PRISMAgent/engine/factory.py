"""
PRISMAgent.engine.factory
===========================

🍋  Core agent-creation utilities that *must* be used by every part of the
code-base (tools, plug-ins, tasks) instead of calling `Agent(...)` directly.
Keeps one authoritative place for:

• Model defaults
• Hook wiring (handoff, tracing, redaction, …)
• Registry persistence (in-memory ⬌ Redis ⬌ Supabase)

→  File size <200 LOC by contract.  Add new helpers in a separate module.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence

from agents import Agent, AgentHooks, RunContextWrapper, Tool, function_tool
from project_name.config.model import MODEL_SETTINGS  # ↩︎ centralised model config
from project_name.storage import registry_factory

# --------------------------------------------------------------------------- #
# 0.  Registry singleton (back-end decided by STORAGE_BACKEND env var)        #
# --------------------------------------------------------------------------- #

_REGISTRY = registry_factory()  # e.g. InMemoryRegistry, RedisRegistry, …

# --------------------------------------------------------------------------- #
# 1.  Public factory                                                         #
# --------------------------------------------------------------------------- #


def agent_factory(
    name: str,
    instructions: str,
    *,
    tools: Iterable[Tool] | None = None,
    hooks: Sequence[AgentHooks] | None = None,
) -> Agent:
    """
    Create **or** fetch an `Agent`.

    Parameters
    ----------
    name : str
        Unique handle (also used to generate transfer tool names).
    instructions : str
        System prompt for the agent.
    tools : Iterable[Tool] | None
        Collection of OpenAI Function Tools (`@function_tool`) to attach.
    hooks : Sequence[AgentHooks] | None
        Extra lifecycle hooks (tracing, redaction, …).

    Returns
    -------
    Agent
        Fully-configured agent, persisted in the global registry.
    """
    if _REGISTRY.exists(name):  # idempotent
        return _REGISTRY.get(name)

    agent = Agent(
        name=name,
        instructions=instructions,
        model=MODEL_SETTINGS.default_model,
        tools=list(tools or []),
        hooks=list(hooks or []),
    )
    _REGISTRY.register(agent)
    return agent


# --------------------------------------------------------------------------- #
# 2.  Runtime-spawn tool (LLM callable)                                       #
# --------------------------------------------------------------------------- #


@function_tool
def spawn_agent(
    name: str,
    instructions: str,
    model: str | None = None,
) -> str:
    """
    OpenAI function-tool that allows an agent to create another agent on the fly.

    Returns the `name` so the LLM can pass it as the result in the tool call.
    """
    agent = agent_factory(
        name=name,
        instructions=instructions,
        tools=[],
        hooks=[],
    )
    if model and model != agent.model:
        agent.model = model  # simple override; advanced tuning lives in config
    return agent.name


# --------------------------------------------------------------------------- #
# 3.  Auto-handoff hook                                                      #
# --------------------------------------------------------------------------- #


class DynamicHandoffHook(AgentHooks):
    """
    When an agent calls `spawn_agent`, automatically append the new agent
    to the caller's `handoffs` list so the LLM can `transfer_to_<name>`
    in the very next turn.
    """

    async def on_tool_end(  # noqa: D401 (SDK signature)
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        if tool.name == "spawn_agent" and _REGISTRY.exists(result):
            agent.handoffs.append(_REGISTRY.get(result))


__all__: List[str] = [
    "agent_factory",
    "spawn_agent",
    "DynamicHandoffHook",
]
