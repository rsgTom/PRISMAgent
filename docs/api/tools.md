# Tools API

The Tools module provides OpenAI function tools that can be used by agents.

## spawn_agent

```python
from agents import function_tool
from typing import Dict, Any, Literal, Optional

@function_tool
async def spawn_agent(
    agent_type: str,
    system_prompt: str,
    task: str,
    complexity: Literal["auto", "basic", "advanced"] = "auto",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new agent and execute a task.
    
    Args:
        agent_type: Type of agent to create (e.g., assistant, coder, researcher)
        system_prompt: System prompt for the new agent
        task: Task for the new agent to perform
        complexity: Complexity level for the task ("auto", "basic", "advanced")
        model: Optional explicit model override
        
    Returns:
        Dict containing the response from the agent
    """
    # Implementation details...
```

> **Note**: This `spawn_agent` is a tool for LLMs to use directly. It's different from the `spawn_agent` function in `PRISMAgent.engine.factory`, which is an internal function used to create agents programmatically. This tool uses `agent_factory` internally to create the agent.

The spawn_agent tool creates a new specialized agent and runs it on a specific task. It offers the following features:

- Creates specialized agents based on type (coder, researcher, etc.)
- Allows customization of system prompt
- Automatically selects appropriate model based on task complexity
- Provides a response from the spawned agent

### Usage Example

```python
from PRISMAgent.tools.spawn import spawn_agent

# In an agent tool execution context
result = await spawn_agent(
    agent_type="coder", 
    system_prompt="You are an expert Python developer.", 
    task="Write a function to calculate the Fibonacci sequence.",
    complexity="advanced"
)

# Access the response
response = result["response"]
```

## web_search

```python
from agents import function_tool

@function_tool
async def web_search(
    query: str,
    num_results: int = 5,
) -> Dict[str, Any]:
    """Search the web for information.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        Dict containing search results
    """
    # Implementation details...
```

## Creating Custom Tools

To create a custom tool using the function_tool decorator:

```python
from agents import function_tool
from typing import Dict, Any

@function_tool
async def my_custom_tool(
    param1: str,
    param2: int = 10,
) -> Dict[str, Any]:
    """
    A custom tool that does something specific.
    
    Args:
        param1: First parameter description
        param2: Second parameter description with default
        
    Returns:
        Dict containing tool result
    """
    # Your implementation here
    return {"result": f"Processed {param1} with value {param2}"}
```