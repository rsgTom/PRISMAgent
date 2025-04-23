# Tools API

The Tools module provides OpenAI function tools that can be used by agents.

## spawn_agent

```python
spawn_agent = {
    "name": "spawn_agent",
    "description": "Create a new agent to handle a specific task",
    "parameters": {
        "type": "object",
        "properties": {
            "agent_type": {
                "type": "string",
                "description": "Type of agent to create (e.g., assistant, coder, researcher)",
                "enum": ["assistant", "coder", "researcher", "custom"]
            },
            "system_prompt": {
                "type": "string",
                "description": "System prompt for the new agent"
            },
            "task": {
                "type": "string",
                "description": "Task for the new agent to perform"
            }
        },
        "required": ["agent_type", "system_prompt", "task"]
    },
    "function": async_spawn_agent_function
}
```

### async_spawn_agent_function

```python
async def async_spawn_agent_function(
    agent_type: str,
    system_prompt: str,
    task: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new agent and execute a task.
    
    Args:
        agent_type: Type of agent to create
        system_prompt: System prompt for the new agent
        task: Task for the new agent to perform
        **kwargs: Additional arguments
        
    Returns:
        Dict containing the response from the agent
    """
```

## web_search

```python
web_search = {
    "name": "web_search",
    "description": "Search the web for information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 5
            }
        },
        "required": ["query"]
    },
    "function": async_web_search_function
}
```

### async_web_search_function

```python
async def async_web_search_function(
    query: str,
    num_results: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Search the web for information.
    
    Args:
        query: Search query
        num_results: Number of results to return
        **kwargs: Additional arguments
        
    Returns:
        Dict containing search results
    """
```

## Creating Custom Tools

To create a custom tool, you need to define:

1. The OpenAI function schema
2. The implementation function

Example:

```python
from typing import Dict, Any, Callable
import json

def create_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    function: Callable
) -> Dict[str, Any]:
    """Create a custom tool."""
    return {
        "name": name,
        "description": description,
        "parameters": parameters,
        "function": function
    }

async def my_custom_function(**kwargs) -> Dict[str, Any]:
    """Implementation of my custom tool."""
    # ... your implementation ...
    return {"result": "Success!"}

my_custom_tool = create_tool(
    name="my_custom_tool",
    description="A custom tool that does something specific",
    parameters={
        "type": "object",
        "properties": {
            "input_param": {
                "type": "string",
                "description": "Input parameter"
            }
        },
        "required": ["input_param"]
    },
    function=my_custom_function
)
``` 