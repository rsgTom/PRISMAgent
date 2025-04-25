"""\nPRISMAgent.tools.spawn\n----------------------\n\nThis module provides tools for spawning new agents.\n"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Union, Any

from agents import Agent
from .factory import tool_factory
from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)


@tool_factory
@with_log_context(component="spawn_agent_tool")
def spawn_agent(
    name: str,
    instructions: str,
    tools: Optional[List[Union[str, Callable]]] = None,
    handoffs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new agent with the specified parameters.
    
    This tool allows one agent to create another agent with different
    capabilities or specialties.
    
    Args:
        name: Unique identifier for the new agent.
        instructions: System prompt/instructions for the agent.
        tools: Optional list of tool names or callable tool functions to provide to the agent.
        handoffs: Optional list of agent names that this agent can delegate tasks to.
    
    Returns:
        A dictionary with details about the created agent.
    """
    # Import here to avoid circular imports
    from PRISMAgent.tools import list_available_tools
    
    logger.info(f"Spawning new agent: {name}", 
               agent_name=name, 
               tool_count=len(tools) if tools else 0, 
               handoff_count=len(handoffs) if handoffs else 0)
    
    # Validate and process tool specifications
    available_tools = list_available_tools()
    actual_tools: List[Callable] = []
    
    if tools:
        for tool_spec in tools:
            # If it's already a callable, use it directly
            if callable(tool_spec):
                logger.debug(f"Using callable tool: {getattr(tool_spec, '__name__', 'unnamed')}")
                actual_tools.append(tool_spec)
                continue
                
            # If it's a string, try to find the corresponding tool
            if isinstance(tool_spec, str):
                if tool_spec not in available_tools:
                    error_msg = f"Invalid tool name: {tool_spec}"
                    logger.error(error_msg, tool_name=tool_spec)
                    raise ValueError(error_msg)
                    
                # Import the actual tool dynamically
                from importlib import import_module
                
                try:
                    # Assume tools are in modules with the same name
                    logger.debug(f"Importing tool module: {tool_spec}", tool_name=tool_spec)
                    module = import_module(f"PRISMAgent.tools.{tool_spec}")
                    if hasattr(module, tool_spec):
                        tool_func = getattr(module, tool_spec)
                        logger.debug(f"Found tool function: {tool_spec}", tool_name=tool_spec)
                        actual_tools.append(tool_func)
                except ImportError as e:
                    error_msg = f"Could not load tool module for: {tool_spec}"
                    logger.error(error_msg, tool_name=tool_spec, error=str(e), exc_info=True)
                    raise ValueError(error_msg)
    
    # Process handoff specifications
    actual_handoffs: List[Agent] = []
    if handoffs:
        # Import here to avoid circular imports
        from PRISMAgent.storage import registry_factory
        registry = registry_factory()
        
        for agent_name in handoffs:
            logger.debug(f"Resolving handoff agent: {agent_name}", agent_name=agent_name)
            agent = await registry.get_agent(agent_name)
            if not agent:
                error_msg = f"Agent not found for handoff: {agent_name}"
                logger.error(error_msg, agent_name=agent_name)
                raise ValueError(error_msg)
            actual_handoffs.append(agent)
    
    # Create the agent via the factory function
    logger.info(f"Creating agent {name} with {len(actual_tools)} tools and {len(actual_handoffs)} handoffs",
                agent_name=name,
                tool_count=len(actual_tools),
                handoff_count=len(actual_handoffs))
                
    agent = agent_factory(
        name=name,
        instructions=instructions,
        tools=actual_tools if actual_tools else None,
        handoffs=actual_handoffs if actual_handoffs else None,
    )
    
    # Return information about the created agent
    response = {
        "id": agent.name,
        "status": "created",
        "tools": [
            getattr(t, "__prism_name__", t.__name__) 
            for t in actual_tools
        ] if actual_tools else [],
        "handoffs": [a.name for a in actual_handoffs] if actual_handoffs else [],
    }
    
    logger.info(f"Successfully spawned agent: {name}", agent_name=name)
    return response
