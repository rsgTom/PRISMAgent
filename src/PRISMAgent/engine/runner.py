"""
PRISMAgent.engine.runner
-----------------------

Thin wrapper around the Agents-SDK `Runner`.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, Optional, Type

from agents import Agent, Runner, StreamEvent
from PRISMAgent.config.model import MODEL_SETTINGS
from PRISMAgent.engine.hooks import DynamicHandoffHook
from PRISMAgent.util import get_logger, with_log_context
from PRISMAgent.util.exceptions import (
    RunnerError, 
    RunnerConfigurationError, 
    ExecutionError,
    ModelAPIError,
    ToolExecutionError
)

# Get a logger for this module
logger = get_logger(__name__)

# ----------------------------------------------------------------------- #
# Runner factory                                                          #
# ----------------------------------------------------------------------- #
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
        
    Raises:
        RunnerConfigurationError: If there's an issue with the runner configuration
        RunnerError: If there's a general issue creating the runner
    """
    try:
        default_model = MODEL_SETTINGS.default_model
        
        logger.debug(
            f"Creating runner with stream={stream}", 
            stream=stream, 
            model=default_model
        )
        
        # Validate model settings
        if not default_model:
            raise RunnerConfigurationError(
                "No default model specified in MODEL_SETTINGS",
                details={"check": "MODEL_SETTINGS.default_model"}
            )
        
        # Apply hooks
        hooks = list(extra_hooks or []) + [DynamicHandoffHook()]
        logger.debug(
            f"Applied {len(hooks)} hooks to runner", 
            hook_count=len(hooks),
            hook_types=[hook.__class__.__name__ for hook in hooks]
        )
        
        # Create runner
        runner = Runner(
            default_model=default_model,
            stream=stream,
            extra_agent_hooks=hooks,
            max_tools_per_run=max_tools_per_run,
        )
        
        logger.info(
            "Runner created successfully", 
            model=default_model,
            stream=stream,
            max_tools=max_tools_per_run
        )
        return runner
    
    except RunnerConfigurationError:
        # Re-raise configuration errors directly
        raise
    
    except Exception as e:
        error_msg = f"Failed to create runner: {str(e)}"
        error_type = type(e).__name__
        
        logger.error(
            error_msg, 
            error=str(e), 
            error_type=error_type,
            exc_info=True
        )
        
        # Provide specific suggestions based on exception type
        suggestions = [
            "Check MODEL_SETTINGS.default_model is properly configured",
            "Verify that extra hooks are compatible with the runner",
            "Ensure max_tools_per_run is a positive integer or None"
        ]
        
        raise RunnerError(error_msg, 
                         details={"original_error": str(e), "error_type": error_type},
                         suggestions=suggestions)

# ----------------------------------------------------------------------- #
# Convenience helper                                                      #
# ----------------------------------------------------------------------- #
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
        
    Raises:
        ExecutionError: If there's an issue during agent execution
        ModelAPIError: If there's an error communicating with the model API
        ToolExecutionError: If a tool execution fails
        RunnerError: If there's an issue creating the runner
    """
    logger.info(
        f"Running agent: {agent.name}", 
        agent_name=agent.name, 
        input_length=len(user_input), 
        stream=stream,
        tools_available=len(agent.tools) if hasattr(agent, 'tools') else 0
    )
    
    runner = None
    try:
        # Create runner
        runner = runner_factory(stream=stream, **runner_kwargs)
        
        # Run agent
        if stream:
            logger.debug("Using streaming mode")
            return runner.run_streamed(agent, user_input)
        else:
            logger.debug("Using non-streaming mode")
            result = runner.run(agent, user_input)
            logger.debug(
                f"Agent run completed", 
                result_length=len(result),
                agent_name=agent.name
            )
            return result
    
    except RunnerError:
        # Re-raise runner errors
        raise
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Log detailed error information
        logger.error(
            f"Error executing agent: {error_msg}", 
            agent_name=agent.name, 
            error=error_msg,
            error_type=error_type,
            runner_exists=runner is not None,
            exc_info=True
        )
        
        # Classify the error for more specific handling
        if "api" in error_type.lower() or "openai" in error_type.lower():
            # Handle API errors
            status_code = getattr(e, "status_code", None)
            model_name = getattr(agent, "model", MODEL_SETTINGS.default_model)
            
            raise ModelAPIError(
                api_error=error_msg,
                model_name=model_name,
                status_code=status_code,
                agent_name=agent.name,
                details={"error_type": error_type}
            )
            
        elif "tool" in error_type.lower():
            # Handle tool execution errors
            tool_name = getattr(e, "tool_name", "unknown")
            
            raise ToolExecutionError(
                tool_name=tool_name,
                error_message=error_msg,
                details={
                    "agent_name": agent.name,
                    "error_type": error_type
                }
            )
            
        else:
            # General execution error
            raise ExecutionError(
                message=f"Error executing agent: {error_msg}",
                agent_name=agent.name,
                details={
                    "error_type": error_type,
                    "user_input_length": len(user_input),
                    "stream_mode": stream
                }
            )

__all__ = ["runner_factory", "run_agent"]
