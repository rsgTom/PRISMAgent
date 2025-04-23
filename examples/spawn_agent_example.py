#!/usr/bin/env python
"""
Spawn Agent Example for PRISMAgent.

This example demonstrates how to use the spawn_agent tool
to create specialized agents for specific tasks.
"""

import asyncio
import os
from typing import Dict, Any, List

from PRISMAgent.config.base import BaseSettings
from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage.file_backend import FileStorageBackend
from PRISMAgent.tools.spawn import spawn_agent


async def main() -> None:
    """Run an example showing the spawn_agent tool usage."""
    # Set up your OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable")
        return

    # Create configuration
    config = BaseSettings(
        api_key=api_key,
        model_name="gpt-4",
        max_tokens=1000,
    )
    
    # Initialize storage
    storage = FileStorageBackend(data_dir="./data")
    
    # Create the primary agent with the spawn_agent tool
    primary_agent = agent_factory(
        config=config,
        storage=storage,
        system_prompt=(
            "You are a workflow coordinator with the ability to delegate specialized tasks. "
            "You can create specialized agents using the spawn_agent tool. "
            "When presented with specific technical challenges, create an appropriate agent "
            "to handle it and then summarize their response."
        ),
        tools=[spawn_agent],
    )
    
    # Create a runner for the agent
    runner = runner_factory(streaming=True)
    
    # Example user query that might require spawning an agent
    user_query = """
    I need to solve this problem:
    Find all pairs of numbers in the array [3, 1, 4, 1, 5, 9, 2, 6, 5] that sum to 10.
    """
    
    # Run the agent
    print("\n=== User Query ===")
    print(user_query)
    print("\n=== Agent Response ===")
    
    # Handle streaming response
    async for chunk in runner.run(
        agent=primary_agent,
        messages=[{"role": "user", "content": user_query}],
    ):
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
    
    print("\n\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main()) 