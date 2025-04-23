"""
PRISMAgent.engine.hooks
-----------------------

Reusable `AgentHooks` implementations (each <200 LOC).
"""

from __future__ import annotations

from typing import List

from local_agents import Agent, AgentHooks, RunContextWrapper, Tool
from PRISMAgent.storage import registry_factory

_REGISTRY = registry_factory()  # singleton

# --------------------------------------------------------------------------- #
# Dynamic hand-off after spawn                                                #
# --------------------------------------------------------------------------- #
class DynamicHandoffHook(AgentHooks):
    async def on_tool_end(        # SDK-prescribed signature
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        if tool.name == "spawn_agent" and _REGISTRY.exists(result):
            agent.handoffs.append(_REGISTRY.get(result))

# --------------------------------------------------------------------------- #
# Simple factory so __init__.py export still works                            #
# --------------------------------------------------------------------------- #
def hook_factory(hook_cls: type[AgentHooks], **kwargs) -> AgentHooks:
    """Return a new hook instance—kept only for backward compatibility."""
    return hook_cls(**kwargs)

__all__: List[str] = ["DynamicHandoffHook", "hook_factory"]
