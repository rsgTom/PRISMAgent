"""Spawn agent tool for PRISMAgent."""

import json
from typing import Dict, Any, Optional, List

from ..config.base import BaseSettings
from ..engine.factory import agent_factory
from ..engine.runner import runner_factory


async def async_spawn_agent_function(
    agent_type: str,
    system_prompt: str,
    task: str,
    **kwargs
) -> Dict[str, Any]:
    """Create a new agent and execute a task.
    
    Args:
        agent_type: Type of agent to create
        system_prompt: System prompt for the new agent
        task: Task for the new agent to perform
        **kwargs: Additional arguments
        
    Returns:
        Dict containing the response from the agent
    """
    # Get the agent configuration from context
    # In a real implementation, we would get this from the current context
    # For now, we'll just create a mock config
    config = BaseSettings(
        api_key="mock-api-key",
        model_name="gpt-4",
        max_tokens=1000,
    )
    
    # Get storage from context
    # For now, we'll use a mock
    storage = {}
    
    # Create a specialized system prompt based on the agent type
    if agent_type == "coder":
        full_system_prompt = f"You are a specialized coding assistant. {system_prompt}"
    elif agent_type == "researcher":
        full_system_prompt = f"You are a specialized research agent. {system_prompt}"
    else:
        full_system_prompt = system_prompt
    
    # Create an agent
    agent = agent_factory(
        config=config,
        storage=storage,
        system_prompt=full_system_prompt,
        tools=[],  # No tools for spawned agents to prevent infinite recursion
    )
    
    # Create a non-streaming runner
    runner = runner_factory(streaming=False)
    
    # Run the agent with the task
    response = await runner.run(
        agent=agent,
        messages=[{"role": "user", "content": task}],
    )
    
    # Extract the response content
    if "choices" in response and len(response["choices"]) > 0:
        message_content = response["choices"][0]["message"]["content"]
        return {"response": message_content}
    
    return {"response": "Error: No response from spawned agent."}


# Define the OpenAI function tool schema
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