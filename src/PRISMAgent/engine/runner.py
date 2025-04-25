"""
PRISMAgent.engine.runner
------------------------

Thin wrapper around the Agents-SDK `Runner`.
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from agents import Agent, Runner, StreamEvent
from PRISMAgent.config.model import MODEL_SETTINGS
from PRISMAgent.engine.hooks import DynamicHandoffHook
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)

# ---------------------------------------------------------------------- #
# Runner factory                                                         #
# ---------------------------------------------------------------------- #
@with_log_context(component="runner_factory")
def runner_factory(
    *,
    stream: bool = False,
    extra_hooks: Iterable[Any] | None = None,
    max_tools_per_run: int | None = None,
) -> Runner:
    """
    Create a Runner instance with the specified configuration.
    
    Args:
        stream: Whether to enable streaming output
        extra_hooks: Additional agent hooks to apply
        max_tools_per_run: Maximum number of tool calls per agent run
        
    Returns:
        Configured Runner instance
    """
    logger.debug(f"Creating runner with stream={stream}", 
                stream=stream, 
                model=MODEL_SETTINGS.default_model)
    
    hooks = list(extra_hooks or []) + [DynamicHandoffHook()]
    logger.debug(f"Applied {len(hooks)} hooks to runner", hook_count=len(hooks))
    
    runner = Runner(
        default_model=MODEL_SETTINGS.default_model,
        stream=stream,
        extra_agent_hooks=hooks,
        max_tools_per_run=max_tools_per_run,
    )
    
    logger.info("Runner created successfully")
    return runner

# ---------------------------------------------------------------------- #
# Convenience helper                                                     #
# ---------------------------------------------------------------------- #
@with_log_context(component="run_agent")
def run_agent(
    agent: Agent,
    user_input: str,
    *,
    stream: bool = False,
    **runner_kwargs: Any,
) -> str | Iterator[StreamEvent]:
    """
    Run an agent with the given input.
    
    Args:
        agent: The agent to run
        user_input: The user's input to process
        stream: Whether to enable streaming output
        **runner_kwargs: Additional keyword arguments for runner_factory
        
    Returns:
        String output (non-streaming) or iterator of StreamEvents (streaming)
    """
    logger.info(f"Running agent: {agent.name}", 
               agent_name=agent.name, 
               input_length=len(user_input), 
               stream=stream)
    
    runner = runner_factory(stream=stream, **runner_kwargs)
    
    if stream:
        logger.debug("Using streaming mode")
        return runner.run_streamed(agent, user_input)
    else:
        logger.debug("Using non-streaming mode")
        result = runner.run(agent, user_input)
        logger.debug(f"Agent run completed", result_length=len(result))
        return result

__all__ = ["runner_factory", "run_agent"]