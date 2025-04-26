"""
PRISMAgent.util.error_handling
----------------------------

Utility functions for consistent error handling across the PRISMAgent codebase.

This module provides decorators and helper functions to standardize error
handling patterns throughout the application.
"""

import functools
import inspect
import sys
import traceback
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

from PRISMAgent.util import get_logger
from PRISMAgent.util.exceptions import (
    PRISMAgentError, 
    ExecutionError,
    ValidationError,
    ConfigurationError,
    StorageError,
    ToolError,
)

# Get a logger for this module
logger = get_logger(__name__)

# Type variables for function signatures
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')

def handle_exceptions(
    error_map: Dict[Type[Exception], Type[PRISMAgentError]] = None,
    default_error_class: Type[PRISMAgentError] = PRISMAgentError,
    log_level: str = "error",
    include_traceback: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to standardize exception handling across the codebase.
    
    This decorator catches exceptions specified in error_map and converts them
    to the corresponding PRISMAgentError subclass. Any other exceptions are 
    converted to the default_error_class.
    
    Args:
        error_map: Mapping from exception types to PRISMAgentError subclasses
        default_error_class: PRISMAgentError subclass to use for unspecified exceptions
        log_level: Level to use for logging the error
        include_traceback: Whether to include traceback in the log
        
    Returns:
        Decorated function that handles exceptions according to the specified rules
        
    Example:
        @handle_exceptions(
            error_map={
                ValueError: ValidationError,
                IOError: StorageError
            },
            default_error_class=ExecutionError
        )
        def my_function():
            ...
    """
    if error_map is None:
        error_map = {}
        
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
                
            except PRISMAgentError:
                # Re-raise PRISMAgentError exceptions directly
                raise
                
            except Exception as e:
                # Get calling context info
                frame = inspect.currentframe()
                if frame:
                    frame = frame.f_back
                module_name = frame.f_globals['__name__'] if frame else "unknown"
                
                # Convert exception according to error_map
                error_type = type(e)
                error_class = error_map.get(error_type, default_error_class)
                
                # Extract error details
                error_msg = str(e)
                error_details = {
                    "original_error": error_msg,
                    "error_type": error_type.__name__,
                    "function": func.__name__,
                    "module": module_name
                }
                
                # Get appropriate logger
                func_logger = logger
                if hasattr(func, "__self__") and hasattr(func.__self__, "logger"):
                    func_logger = func.__self__.logger
                
                # Log the error
                log_method = getattr(func_logger, log_level)
                log_method(
                    f"Error in {func.__name__}: {error_msg}",
                    exc_info=include_traceback,
                    **error_details
                )
                
                # Create and raise appropriate exception
                if error_class == ValidationError:
                    field_name = getattr(e, "field", "input")
                    raise ValidationError(field_name, error_msg, error_details)
                    
                elif error_class == ConfigurationError:
                    config_key = getattr(e, "config_key", "configuration")
                    raise ConfigurationError(f"Invalid {config_key}: {error_msg}", error_details)
                    
                elif error_class == StorageError:
                    operation = getattr(e, "operation", "operation")
                    raise StorageError(f"Storage {operation} failed: {error_msg}", error_details)
                    
                elif error_class == ToolError:
                    tool_name = getattr(e, "tool_name", "unknown")
                    raise ToolError(f"Tool '{tool_name}' error: {error_msg}", error_details)
                    
                elif error_class == ExecutionError:
                    agent_name = getattr(e, "agent_name", None)
                    raise ExecutionError(error_msg, agent_name, error_details)
                
                else:
                    # Generic PRISMAgentError
                    raise error_class(f"Error in {func.__name__}: {error_msg}", error_details)
                
        return cast(F, wrapper)
    
    return decorator


@contextmanager
def error_context(
    context_message: str,
    error_map: Dict[Type[Exception], Type[PRISMAgentError]] = None,
    default_error_class: Type[PRISMAgentError] = PRISMAgentError,
    context_details: Dict[str, Any] = None,
) -> None:
    """
    Context manager for handling exceptions with additional context.
    
    Args:
        context_message: Message to prepend to the error message
        error_map: Mapping from exception types to PRISMAgentError subclasses
        default_error_class: PRISMAgentError subclass to use for unspecified exceptions
        context_details: Additional details to include in the error
        
    Example:
        with error_context(
            "Failed to load configuration",
            error_map={FileNotFoundError: ConfigurationError},
            context_details={"config_path": config_path}
        ):
            load_config(config_path)
    """
    if error_map is None:
        error_map = {}
        
    if context_details is None:
        context_details = {}
        
    try:
        yield
        
    except PRISMAgentError as e:
        # Add context to PRISMAgentError
        e.message = f"{context_message}: {e.message}"
        e.details.update(context_details)
        raise
        
    except Exception as e:
        # Convert other exceptions according to error_map
        error_type = type(e)
        error_class = error_map.get(error_type, default_error_class)
        
        error_msg = f"{context_message}: {str(e)}"
        error_details = {
            "original_error": str(e),
            "error_type": error_type.__name__,
        }
        error_details.update(context_details)
        
        # Log the error
        logger.error(error_msg, exc_info=True, **error_details)
        
        # Raise appropriate exception
        if error_class == ValidationError:
            field_name = getattr(e, "field", "input")
            raise ValidationError(field_name, error_msg, error_details)
            
        elif error_class == ConfigurationError:
            config_key = getattr(e, "config_key", "configuration")
            raise ConfigurationError(f"Invalid {config_key}: {error_msg}", error_details)
            
        elif error_class == StorageError:
            operation = getattr(e, "operation", "operation")
            raise StorageError(f"Storage {operation} failed: {error_msg}", error_details)
            
        elif error_class == ToolError:
            tool_name = getattr(e, "tool_name", "unknown")
            raise ToolError(f"Tool '{tool_name}' error: {error_msg}", error_details)
            
        elif error_class == ExecutionError:
            agent_name = getattr(e, "agent_name", None)
            raise ExecutionError(error_msg, agent_name, error_details)
        
        else:
            # Generic PRISMAgentError
            raise error_class(error_msg, error_details)


def format_exception_with_context(
    exc_info=None, 
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format an exception with additional context for better error messages.
    
    Args:
        exc_info: Exception info as returned by sys.exc_info()
        context: Additional context to include in the error message
        
    Returns:
        Formatted exception message with traceback and context
    """
    if exc_info is None:
        exc_info = sys.exc_info()
        
    if context is None:
        context = {}
    
    exc_type, exc_value, exc_tb = exc_info
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    # Format context
    context_str = ""
    if context:
        context_str = "\nContext:\n"
        context_str += "\n".join(f"  {k}: {v}" for k, v in context.items())
    
    return f"{tb_str}{context_str}"


def validate_or_raise(
    condition: bool, 
    error_message: str, 
    field_name: str = "input",
    error_class: Type[PRISMAgentError] = ValidationError,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Validate a condition and raise an exception if it fails.
    
    Args:
        condition: The condition to validate
        error_message: Error message to use if validation fails
        field_name: Name of the field being validated (for ValidationError)
        error_class: PRISMAgentError subclass to raise
        details: Additional details to include in the error
        
    Raises:
        PRISMAgentError: If the condition is False
        
    Example:
        validate_or_raise(len(text) > 0, "Text cannot be empty", "text_input")
    """
    if not condition:
        details = details or {}
        
        if error_class == ValidationError:
            raise ValidationError(field_name, error_message, details)
        else:
            raise error_class(error_message, details)
