"""
PRISMAgent.storage.base
-------------------

Base protocols and abstract classes for storage backends.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Protocol, Optional, runtime_checkable

from agents import Agent


@runtime_checkable
class RegistryProtocol(Protocol):
    """Protocol defining the interface for agent registries."""
    
    def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        ...
        
    def get(self, name: str) -> Agent:
        """Get an agent by name. Raises KeyError if not found."""
        ...
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name. Returns None if not found.
        
        This is a safer alternative to get() that doesn't raise KeyError.
        """
        ...
        
    def register(self, agent: Agent) -> None:
        """Register an agent in the registry."""
        ...
    
    def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        ...


class BaseRegistry(ABC):
    """Abstract base class for agent registries."""
    
    @abstractmethod
    def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        ...
        
    @abstractmethod
    def get(self, name: str) -> Agent:
        """Get an agent by name. Should raise KeyError if not found."""
        ...
    
    @abstractmethod
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name. Returns None if not found.
        
        This is a safer alternative to get() that doesn't raise KeyError.
        """
        ...
        
    @abstractmethod
    def register(self, agent: Agent) -> None:
        """Register an agent in the registry."""
        ...
    
    @abstractmethod
    def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        ...