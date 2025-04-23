"""
project_name.engine.hooks
-------------------------

Reusable `AgentHooks` implementations.
Keep each hook < 200 LOC; add new ones in separate files.
"""

from __future__ import annotations

from typing import List

from agents import Agent, AgentHooks, RunContextWrapper, Tool
from project_name.storage import registry_factory

# Singleton registry chosen via STORAGE_BACKEND env-var
_REGISTRY = registry_factory()


class DynamicHandoffHook(AgentHooks):
    """
    After an agent calls the `spawn_agent` tool, automatically attach the newly
    created agent to the caller’s `handoffs` list so the LLM can immediately
    invoke `transfer_to_<name>`. The spawned agent must already be registered.
    """

    async def on_tool_end(          # SDK-prescribed signature
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        if tool.name == "spawn_agent" and _REGISTRY.exists(result):
            agent.handoffs.append(_REGISTRY.get(result))


# ──────────────────────────────  OPTIONAL EXTRAS  ───────────────────────────── #
# Add other cross-cutting hooks here (tracing, redaction, cost-metering, …)
# Each should subclass `AgentHooks` and be <200 LOC.

__all__: List[str] = ["DynamicHandoffHook"]
