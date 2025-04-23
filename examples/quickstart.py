#!/usr/bin/env python
"""
Quickstart example for PRISMAgent.

This example demonstrates how to create and run a simple agent using PRISMAgent.
"""

import asyncio
from typing import Dict, Any

from PRISMAgent.config.base import BaseSettings
from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage.file_backend import FileStorageBackend


async def main() -> None:
    """Run a simple agent example."""
    # Create configuration
    config = BaseSettings(
        api_key="your-openai-api-key",  # Replace with your actual API key
        model_name="gpt-4",
        max_tokens=1000,
    )
    
    # Initialize storage
    storage = FileStorageBackend(data_dir="./data")
    
    # Create an agent
    agent = agent_factory(
        config=config,
        storage=storage,
        system_prompt="You are a helpful assistant that provides concise answers.",
        tools=[],  # No tools for this simple example
    )
    
    # Create a runner
    runner = runner_factory(streaming=True)
    
    # User query
    user_query = "What are three benefits of using a modular architecture in software design?"
    
    # Run the agent
    response = await runner.run(
        agent=agent,
        messages=[{"role": "user", "content": user_query}],
    )
    
    # Print the response
    for chunk in response:
        if isinstance(chunk, Dict) and "content" in chunk:
            print(chunk["content"], end="", flush=True)
    print("\n")


if __name__ == "__main__":
    asyncio.run(main()) 