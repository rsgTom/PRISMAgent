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

# -------------------------------------------------------------------- #
# Runner factory                                                      #
# -------------------------------------------------------------------- #
@with_log_context(component="runner_factory")
def runner_factory(
    *,
    stream: bool = False,
    extra_hooks: Iterable[Any] | None = None,
    max_tools_per_run: int | None = None,
) -> Runner:
    logger.debug("Creating runner instance", 
                stream=stream, 
                max_tools_per_run=max_tools_per_run)
    
    hooks = list(extra_hooks or []) + [DynamicHandoffHook()]
    
    return Runner(
        default_model=MODEL_SETTINGS.default_model,
        stream=stream,
        extra_agent_hooks=hooks,
        max_tools_per_run=max_tools_per_run,
    )

# -------------------------------------------------------------------- #
# Convenience helper                                                  #
# -------------------------------------------------------------------- #
@with_log_context(component="run_agent")
def run_agent(
    agent: Agent,
    user_input: str,
    *,
    stream: bool = False,
    **runner_kwargs: Any,
) -> str | Iterator[StreamEvent]:
    logger.info(f"Running agent {agent.name}", 
                agent_name=agent.name, 
                input_length=len(user_input), 
                stream=stream)
    
    runner = runner_factory(stream=stream, **runner_kwargs)
    
    try:
        result = (
            runner.run_streamed(agent, user_input)
            if stream
            else runner.run(agent, user_input)
        )
        
        if not stream:
            logger.debug(f"Agent {agent.name} response length: {len(result)}", 
                        agent_name=agent.name, 
                        response_length=len(result))
        
        return result
    except Exception as e:
        logger.error(f"Error running agent {agent.name}: {str(e)}", 
                    agent_name=agent.name, 
                    error=str(e), 
                    exc_info=True)
        raise

__all__ = ["runner_factory", "run_agent"]
