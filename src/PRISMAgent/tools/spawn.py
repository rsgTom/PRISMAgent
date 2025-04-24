"""
PRISMAgent.tools.spawn
---------------------

This module provides tools for spawning new agents.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Union

from agents import Agent
from .factory import tool_factory
from PRISMAgent.engine.factory import agent_factory


@tool_factory
def spawn_agent(
    name: str,
    instructions: str,
    tools: Optional[List[str]] = None,
) -> Dict[str, str]:
    """
    Create a new agent with the specified parameters.
    
    This tool allows one agent to create another agent with different
    capabilities or specialties.
    
    Args:
        name: Unique identifier for the new agent.
        instructions: System prompt/instructions for the agent.
        tools: Optional list of tool names to provide to the agent.
    
    Returns:
        A dictionary with details about the created agent.
    """
    # Import here to avoid circular imports
    from PRISMAgent.tools import list_available_tools
    
    # Validate tool names if provided
    available_tools = list_available_tools()
    actual_tools = []
    
    if tools:
        for tool_name in tools:
            if tool_name not in available_tools:
                raise ValueError(f"Invalid tool name: {tool_name}")
                
            # Import the actual tool dynamically
            # This is a simplified version - in reality, you'd need
            # to better handle tool resolution
            from importlib import import_module
            
            try:
                # Assume tools are in modules with the same name
                module = import_module(f"PRISMAgent.tools.{tool_name}")
                if hasattr(module, tool_name):
                    tool = getattr(module, tool_name)
                    actual_tools.append(tool)
            except ImportError:
                raise ValueError(f"Could not load tool module for: {tool_name}")
    
    # Create the agent via the factory function
    agent = agent_factory(
        name=name,
        instructions=instructions,
        tools=actual_tools if actual_tools else None,
    )
    
    # Return information about the created agent
    return {
        "id": agent.name,
        "status": "created",
        "tools": [t.__prism_name__ for t in actual_tools] if actual_tools else [],
    }
