"""
PRISMAgent.storage.file_backend
-----------------------------

Simple in-memory registry implementation for development and testing.
For production use, consider using Redis, Supabase, or other persistent backends.
"""

from typing import Dict, ClassVar, List, Optional
from agents import Agent
from .base import BaseRegistry
from PRISMAgent.util import get_logger
from PRISMAgent.util.exceptions import AgentNotFoundError, AgentExistsError

# Get a logger for this module
logger = get_logger(__name__)

class InMemoryRegistry(BaseRegistry):
    """
    In-memory implementation of agent registry.
    
    Warning: All agents are lost when the process restarts.
    Use only for development and testing.
    """
    
    _store: ClassVar[Dict[str, Agent]] = {}
    
    def exists_sync(self, name: str) -> bool:
        """Synchronous version of exists() for synchronous contexts."""
        return name in self._store
    
    async def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        return name in self._store
    
    async def get(self, name: str) -> Agent:
        """
        Get an agent by name.
        
        Raises:
            AgentNotFoundError: If the agent doesn't exist in the registry.
        """
        if not await self.exists(name):
            error_msg = f"Agent with name '{name}' not found in registry"
            logger.warning(error_msg, agent_name=name)
            raise AgentNotFoundError(name)
        
        logger.debug(f"Retrieved agent: {name}", agent_name=name)
        return self._store[name]
    
    async def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name. Returns None if not found."""
        agent = self._store.get(name)
        if agent:
            logger.debug(f"Retrieved agent: {name}", agent_name=name)
        else:
            logger.debug(f"Agent not found: {name}", agent_name=name)
        return agent
    
    async def register(self, agent: Agent) -> None:
        """
        Register an agent in the registry.
        
        Raises:
            AgentExistsError: If an agent with the same name already exists.
        """
        if await self.exists(agent.name):
            error_msg = f"Agent with name '{agent.name}' already exists in registry"
            logger.warning(error_msg, agent_name=agent.name)
            raise AgentExistsError(agent.name)
        
        self._store[agent.name] = agent
        logger.debug(f"Registered agent: {agent.name}", agent_name=agent.name)
    
    async def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        agent_list = list(self._store.keys())
        logger.debug(f"Listed {len(agent_list)} agents", count=len(agent_list))
        return agent_list
