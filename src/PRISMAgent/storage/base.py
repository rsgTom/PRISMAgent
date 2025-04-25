"""
PRISMAgent.storage.base
---------------------

Base protocols and abstract classes for storage backends.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Protocol, Optional, runtime_checkable

from agents import Agent


@runtime_checkable
class RegistryProtocol(Protocol):
    """Protocol defining the interface for agent registries."""
    
    async def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        ...
        
    async def get(self, name: str) -> Agent:
        """Get an agent by name. Raises KeyError if not found."""
        ...
    
    async def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name. Returns None if not found.
        
        This is a safer alternative to get() that doesn't raise KeyError.
        """
        ...
        
    async def register(self, agent: Agent) -> None:
        """Register an agent in the registry."""
        ...
    
    async def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        ...


class BaseRegistry(ABC):
    """Abstract base class for agent registries."""
    
    @abstractmethod
    async def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        ...
        
    @abstractmethod
    async def get(self, name: str) -> Agent:
        """Get an agent by name. Should raise KeyError if not found."""
        ...
    
    @abstractmethod
    async def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name. Returns None if not found.
        
        This is a safer alternative to get() that doesn't raise KeyError.
        """
        ...
        
    @abstractmethod
    async def register(self, agent: Agent) -> None:
        """Register an agent in the registry."""
        ...
    
    @abstractmethod
    async def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        ...
