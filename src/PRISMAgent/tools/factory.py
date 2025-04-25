"""
PRISMAgent.tools.factory
-----------------------

Factory function for creating function tools that can be used by agents.

This module provides the tool_factory function, which converts regular Python
functions into OpenAI function tools. It's a thin wrapper around 
the OpenAI Agents SDK function_tool decorator.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints

from agents import function_tool as agents_function_tool
from pydantic import create_model, BaseModel, Field
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)

__all__ = ["tool_factory", "list_available_tools"]


def _get_param_info(func: Callable) -> Dict[str, Any]:
    """Extract parameter information from a function's signature and docstring."""
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    # Get parameter information from signature
    params_info = {}
    for name, param in signature.parameters.items():
        # Skip 'self' parameter for methods
        if name == "self":
            continue
        
        param_info = {
            "required": param.default is param.empty,
            "default": None if param.default is param.empty else param.default,
        }
        
        # Add type hint if available
        if name in type_hints:
            param_info["type"] = type_hints[name]
        
        params_info[name] = param_info
    
    return params_info


def tool_factory(
    func: Callable,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable:
    """
    Convert a Python function into an OpenAI function tool.
    
    This factory wraps the OpenAI Agents SDK's function_tool decorator,
    adding additional validation and metadata extraction.
    
    Args:
        func: The function to convert into a tool.
        name: Optional override for the tool's name (defaults to function name).
        description: Optional override for the tool's description 
               (defaults to function docstring).
    
    Returns:
        The wrapped function that can be used as a tool by agents.
    
    Example:
        ```python
        def search(query: str) -> List[Dict]:
            """Search for information online."""
            # Implementation...
            return results
        
        search_tool = tool_factory(search)
        ```
    """
    # Use function name if not provided
    if name is None:
        name = func.__name__
    
    # Use function docstring if description not provided
    if description is None and func.__doc__:
        description = inspect.cleandoc(func.__doc__).split("\n\n")[0]
    elif description is None:
        description = f"Tool for {name}"
    
    # Get parameter information
    params_info = _get_param_info(func)
    
    logger.debug(f"Creating tool: {name}", tool_name=name)
    
    # Apply the OpenAI function_tool decorator
    wrapped_func = agents_function_tool(func)
    
    # Add extra metadata for PRISMAgent
    wrapped_func.__prism_tool__ = True
    wrapped_func.__prism_name__ = name
    wrapped_func.__prism_description__ = description
    wrapped_func.__prism_params__ = params_info
    
    logger.info(f"Tool {name} created successfully", 
                tool_name=name, 
                description=description)
    
    return wrapped_func


def list_available_tools() -> List[str]:
    """List all available tools registered in the system."""
    # Import here to avoid circular imports
    from importlib import import_module
    from pkgutil import iter_modules
    from PRISMAgent.tools import __path__ as tools_path
    
    tools = []
    
    # Discover tools in the tools package
    for _, module_name, _ in iter_modules(tools_path):
        # Skip special modules
        if module_name in ("__init__", "factory"):
            continue
        
        try:
            module = import_module(f"PRISMAgent.tools.{module_name}")
            
            # Check for decorated functions
            for item_name in dir(module):
                item = getattr(module, item_name)
                
                if callable(item) and hasattr(item, "__agents_tool__"):
                    tools.append(item_name)
        except ImportError as e:
            logger.warning(f"Could not import tool module {module_name}: {e}", 
                           module=module_name, 
                           error=str(e),
                           exc_info=True)
    
    logger.debug(f"Found {len(tools)} available tools", tool_count=len(tools))
    return tools