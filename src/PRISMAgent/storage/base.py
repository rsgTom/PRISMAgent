"""
PRISMAgent.storage.base
---------------------

Base protocols and abstract classes for storage backends.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Protocol, Optional, runtime_checkable

from agents import Agent
from PRISMAgent.util.exceptions import AgentNotFoundError


@runtime_checkable
class RegistryProtocol(Protocol):
    """Protocol defining the interface for agent registries."""
    
    async def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        ...
        
    async def get(self, name: str) -> Agent:
        """
        Get an agent by name.
        
        Raises:
            AgentNotFoundError: If the agent is not found.
        """
        ...
    
    async def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name. Returns None if not found.
        
        This is a safer alternative to get() that doesn't raise exceptions.
        """
        ...
        
    async def register(self, agent: Agent) -> None:
        """
        Register an agent in the registry.
        
        Raises:
            AgentExistsError: If an agent with the same name already exists.
        """
        ...
        
    async def register_agent(self, agent: Agent) -> None:
        """
        Alias for register() method for backward compatibility.
        
        Raises:
            AgentExistsError: If an agent with the same name already exists.
        """
        ...
    
    async def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        ...
        
    def exists_sync(self, name: str) -> bool:
        """
        Synchronous version of exists() for use in synchronous contexts.
        
        This method should be implemented by all registry backends.
        """
        ...


class BaseRegistry(ABC):
    """Abstract base class for agent registries."""
    
    @abstractmethod
    async def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        ...
        
    @abstractmethod
    async def get(self, name: str) -> Agent:
        """
        Get an agent by name.
        
        Raises:
            AgentNotFoundError: If the agent is not found.
        """
        ...
    
    @abstractmethod
    async def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name. Returns None if not found.
        
        This is a safer alternative to get() that doesn't raise exceptions.
        """
        ...
        
    @abstractmethod
    async def register(self, agent: Agent) -> None:
        """
        Register an agent in the registry.
        
        Raises:
            AgentExistsError: If an agent with the same name already exists.
        """
        ...
    
    async def register_agent(self, agent: Agent) -> None:
        """
        Alias for register() method for backward compatibility.
        
        Raises:
            AgentExistsError: If an agent with the same name already exists.
        """
        return await self.register(agent)
    
    @abstractmethod
    async def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        ...
    
    def exists_sync(self, name: str) -> bool:
        """
        Synchronous version of exists() for use in synchronous contexts.
        
        Default implementation using asyncio.run() which may not be ideal.
        Subclasses should override with a more efficient implementation when possible.
        """
        import asyncio
        try:
            # Use a new event loop to avoid issues with nested event loops
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(self.exists(name))
        finally:
            loop.close()
