#!/usr/bin/env python
"""
Multi-agent handshake example for PRISMAgent.

This example demonstrates how to create and orchestrate multiple agents.
"""

import asyncio
from typing import Dict, Any, List

from PRISMAgent.config.base import BaseSettings
from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.engine.hooks import hook_factory, DynamicHandoffHook
from PRISMAgent.storage.file_backend import FileStorageBackend
from PRISMAgent.tools.spawn import spawn_agent


async def main() -> None:
    """Run a multi-agent example with handoffs."""
    # Create configuration
    config = BaseSettings(
        api_key="your-openai-api-key",  # Replace with your actual API key
        model_name="gpt-4",
        max_tokens=1000,
    )
    
    # Initialize storage
    storage = FileStorageBackend(data_dir="./data")
    
    # Create the primary agent with spawn tool
    primary_agent = agent_factory(
        config=config,
        storage=storage,
        system_prompt=(
            "You are a helpful assistant that can delegate tasks to specialized agents. "
            "If you need specialist knowledge, use the spawn_agent tool."
        ),
        tools=[spawn_agent],
    )
    
    # Define specialized agents
    specialist_profiles = {
        "coding_agent": {
            "system_prompt": "You are a coding expert. Provide detailed, clean code solutions.",
            "tools": [],
        },
        "research_agent": {
            "system_prompt": "You are a research specialist. Provide well-cited information.",
            "tools": [],
        },
    }
    
    # Create handoff hook
    handoff_hook = hook_factory(hook_type=DynamicHandoffHook)
    
    # Register specialist agents with the hook
    for name, profile in specialist_profiles.items():
        specialist_agent = agent_factory(
            config=config,
            storage=storage,
            system_prompt=profile["system_prompt"],
            tools=profile["tools"],
        )
        handoff_hook.register_agent(name, specialist_agent)
    
    # Create a runner with the handoff hook
    runner = runner_factory(streaming=True, hooks=[handoff_hook])
    
    # Example user query that might require handoff
    user_query = """
    I need help with two things:
    1. Can you write a Python function to calculate the Fibonacci sequence?
    2. What are the key differences between classical and quantum computing?
    """
    
    # Run the agent with possible handoffs
    response = await runner.run(
        agent=primary_agent,
        messages=[{"role": "user", "content": user_query}],
    )
    
    # Print the complete conversation
    for chunk in response:
        # In a real application, you'd handle different chunk formats more robustly
        if isinstance(chunk, Dict) and "content" in chunk:
            print(chunk["role"] if "role" in chunk else "assistant", ": ", chunk["content"])
    

if __name__ == "__main__":
    asyncio.run(main()) 