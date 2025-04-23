"""
prismagent.engine.runner
--------------------------

Tiny wrapper around the Agents-SDK `Runner` that selects sync vs. streamed
execution and injects default observability settings.  (< 200 LOC)
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from agents import Agent, Runner, StreamEvent
from prismagent.config.model import MODEL_SETTINGS
from prismagent.engine.hooks import DynamicHandoffHook


def runner_factory(
    *,
    stream: bool = False,
    extra_hooks: Iterable[Any] | None = None,
    max_tools_per_run: int | None = None,
) -> Runner:
    """
    Return a configured `Runner` instance.

    Parameters
    ----------
    stream : bool
        If True, prepare for `run_streamed`; else for `run`.
    extra_hooks : Iterable[Any] | None
        Additional `AgentHooks` instances applied to the root agent at runtime.
    max_tools_per_run : int | None
        Optional guard-rail to cap tool invocations in a single run.

    Notes
    -----
    The caller still decides *when* to invoke `.run()` or `.run_streamed()`.
    """
    return Runner(
        default_model=MODEL_SETTINGS.default_model,
        stream=stream,
        extra_agent_hooks=list(extra_hooks or []) + [DynamicHandoffHook()],
        max_tools_per_run=max_tools_per_run,
    )


# ------------------------------- Convenience API ----------------------------- #


def run_agent(
    agent: Agent,
    user_input: str,
    *,
    stream: bool = False,
    **runner_kwargs: Any,
) -> str | Iterator[StreamEvent]:
    """
    Fire-and-forget helper so callers don’t need to touch `Runner` directly.

    Examples
    --------
    >>> result = run_agent(my_agent, "Summarise this article:")
    >>> for event in run_agent(my_agent, "Generate code:", stream=True):
    ...     print(event.content, end="")
    """
    runner = runner_factory(stream=stream, **runner_kwargs)
    if stream:
        return runner.run_streamed(agent, user_input)
    return runner.run(agent, user_input)


__all__ = ["runner_factory", "run_agent"]
