"""
Mock agents package for testing.

This is a placeholder for the actual agents implementation.
"""

from typing import Callable, List, Any, Protocol


class AgentHooks(Protocol):
    """Protocol for agent hooks."""
    pass


class Tool:
    """Mock Tool class for testing."""
    
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func


class Agent:
    """Mock Agent class for testing."""
    
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str = "gpt-3.5-turbo",
        tools: List[Tool] = None,
        hooks: List[AgentHooks] = None,
    ):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []
        self.hooks = hooks or []


def function_tool(func: Callable) -> Tool:
    """Mock function_tool decorator for testing."""
    return Tool(name=func.__name__, func=func) 