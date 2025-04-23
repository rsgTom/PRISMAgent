"""
PRISMAgent.engine.runner
------------------------

Thin wrapper around the Agents-SDK `Runner`.
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from local_agents import Agent, Runner, StreamEvent
from PRISMAgent.config.model import MODEL_SETTINGS
from PRISMAgent.engine.hooks import DynamicHandoffHook

# --------------------------------------------------------------------------- #
# Runner factory                                                              #
# --------------------------------------------------------------------------- #
def runner_factory(
    *,
    stream: bool = False,
    extra_hooks: Iterable[Any] | None = None,
    max_tools_per_run: int | None = None,
) -> Runner:
    return Runner(
        default_model=MODEL_SETTINGS.default_model,
        stream=stream,
        extra_agent_hooks=list(extra_hooks or []) + [DynamicHandoffHook()],
        max_tools_per_run=max_tools_per_run,
    )

# --------------------------------------------------------------------------- #
# Convenience helper                                                          #
# --------------------------------------------------------------------------- #
def run_agent(
    agent: Agent,
    user_input: str,
    *,
    stream: bool = False,
    **runner_kwargs: Any,
) -> str | Iterator[StreamEvent]:
    runner = runner_factory(stream=stream, **runner_kwargs)
    return (
        runner.run_streamed(agent, user_input)
        if stream
        else runner.run(agent, user_input)
    )

__all__ = ["runner_factory", "run_agent"]
