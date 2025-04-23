"""Agent service for the backend."""

from typing import Dict, Any, List, Optional
import asyncio

from PRISMAgent.config.base import BaseSettings
from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage.file_backend import FileStorageBackend


class AgentService:
    """Service for managing agent interactions."""
    
    def __init__(self, config: Optional[BaseSettings] = None, storage_path: str = "./data"):
        """Initialize the agent service.
        
        Args:
            config: Optional configuration, creates default if None
            storage_path: Path for file storage
        """
        self.config = config or BaseSettings(
            api_key=self._get_api_key(),
            model_name="gpt-4",
            max_tokens=1000,
        )
        self.storage = FileStorageBackend(data_dir=storage_path)
        
    def _get_api_key(self) -> str:
        """Get the API key from environment or fail."""
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return api_key
        
    async def create_agent(
        self, 
        system_prompt: str,
        tools: Optional[List[Any]] = None
    ) -> str:
        """Create a new agent.
        
        Args:
            system_prompt: System prompt for the agent
            tools: Optional tools for the agent
            
        Returns:
            ID of the created agent
        """
        # Generate a random ID for the agent
        import uuid
        agent_id = str(uuid.uuid4())
        
        # Store the agent configuration
        await self.storage.set(f"agent:{agent_id}", {
            "id": agent_id,
            "system_prompt": system_prompt,
            "tools": tools or [],
            "created_at": self._get_timestamp(),
        })
        
        return agent_id
        
    async def run_agent(
        self,
        agent_id: str,
        messages: List[Dict[str, Any]],
        streaming: bool = False
    ) -> Any:
        """Run an agent with the provided messages.
        
        Args:
            agent_id: ID of the agent to run
            messages: Messages to process
            streaming: Whether to use streaming mode
            
        Returns:
            Response from the agent
        """
        # Get the agent configuration
        agent_config = await self.storage.get(f"agent:{agent_id}")
        if not agent_config:
            raise ValueError(f"Agent with ID {agent_id} not found")
            
        # Create the agent
        agent = agent_factory(
            config=self.config,
            storage=self.storage,
            system_prompt=agent_config["system_prompt"],
            tools=agent_config.get("tools", []),
        )
        
        # Create a runner
        runner = runner_factory(streaming=streaming)
        
        # Run the agent
        return await runner.run(agent=agent, messages=messages)
        
    def _get_timestamp(self) -> str:
        """Get a formatted timestamp for the current time."""
        from datetime import datetime
        return datetime.utcnow().isoformat() 