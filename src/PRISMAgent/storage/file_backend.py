"""
PRISMAgent.storage.file_backend
--------------------------

Simple in-memory registry implementation for development and testing.
For production use, consider using Redis, Supabase, or other persistent backends.
"""

from typing import Dict, ClassVar, List, Optional
from agents import Agent
from .base import BaseRegistry


class InMemoryRegistry(BaseRegistry):
    """
    In-memory implementation of agent registry.
    
    Warning: All agents are lost when the process restarts.
    Use only for development and testing.
    """
    
    _store: ClassVar[Dict[str, Agent]] = {}
    
    def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        return name in self._store
    
    def get(self, name: str) -> Agent:
        """Get an agent by name. Raises KeyError if not found."""
        if not self.exists(name):
            raise KeyError(f"Agent with name '{name}' not found in registry")
        return self._store[name]
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name. Returns None if not found."""
        return self._store.get(name)
    
    def register(self, agent: Agent) -> None:
        """Register an agent in the registry."""
        self._store[agent.name] = agent 
    
    def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        return list(self._store.keys())