"""Spawn agent tool for PRISMAgent."""

import logging
from typing import Dict, Any, Optional, List, Literal

from agents import function_tool
from ..engine.factory import agent_factory
from ..engine.runner import runner_factory
from ..config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

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
    # Check if API key is available
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not set in environment or .env file")
        return {"response": "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in environment or .env file."}
        
    # Create a specialized system prompt based on the agent type
    if agent_type == "coder":
        full_system_prompt = f"You are a specialized coding assistant. {system_prompt}"
    elif agent_type == "researcher":
        full_system_prompt = f"You are a specialized research agent. {system_prompt}"
    else:
        full_system_prompt = system_prompt
    
    # Derive logical task type from agent_type
    task_type = "code" if agent_type == "coder" else "chat"
    
    # Create an agent using the factory
    agent_name = f"{agent_type}_{hash(system_prompt)}"
    
    # Create an agent with no tools to prevent infinite recursion
    agent = agent_factory(
        name=agent_name,
        instructions=full_system_prompt,
        tools=None,  # No tools for spawned agents to prevent infinite recursion
        task=task_type,
        complexity=complexity,
        model=model,
    )
    
    # Create a non-streaming runner
    runner = runner_factory(stream=False)
    
    # Run the agent with the task
    response = runner.run(agent, task)
    
    return {"response": response}