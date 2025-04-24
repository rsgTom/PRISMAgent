"""
Unit tests for the registry protocol implementation.

Tests that each registry backend properly implements the new get_agent and list_agents methods.
"""

import pytest
from unittest.mock import MagicMock
from agents import Agent

from PRISMAgent.storage import registry_factory, InMemoryRegistry
from PRISMAgent.storage.vector_backend import VectorStore

# Test data
TEST_AGENTS = {
    "agent1": MagicMock(spec=Agent, name="agent1"),
    "agent2": MagicMock(spec=Agent, name="agent2"),
    "agent3": MagicMock(spec=Agent, name="agent3"),
}


class TestRegistryProtocol:
    """Base test class for testing registry implementations."""
    
    def get_registry(self):
        """Get a registry instance. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement get_registry")
        
    def test_get_agent_exists(self):
        """Test retrieving an agent that exists."""
        registry = self.get_registry()
        
        # Register a test agent
        test_agent = TEST_AGENTS["agent1"]
        registry.register(test_agent)
        
        # Get the agent
        result = registry.get_agent(test_agent.name)
        assert result is test_agent
        
    def test_get_agent_nonexistent(self):
        """Test retrieving an agent that doesn't exist."""
        registry = self.get_registry()
        
        # Get a nonexistent agent
        result = registry.get_agent("nonexistent")
        assert result is None
        
    def test_list_agents_empty(self):
        """Test listing agents when the registry is empty."""
        registry = self.get_registry()
        
        # List agents from an empty registry
        result = registry.list_agents()
        assert isinstance(result, list)
        assert len(result) == 0
        
    def test_list_agents_populated(self):
        """Test listing agents when the registry contains agents."""
        registry = self.get_registry()
        
        # Register test agents
        for agent in TEST_AGENTS.values():
            registry.register(agent)
        
        # List all agents
        result = registry.list_agents()
        assert isinstance(result, list)
        assert len(result) == len(TEST_AGENTS)
        assert set(result) == set(TEST_AGENTS.keys())


class TestInMemoryRegistry(TestRegistryProtocol):
    """Test the InMemoryRegistry implementation."""
    
    def get_registry(self):
        """Get an InMemoryRegistry instance."""
        return InMemoryRegistry()


class TestVectorStore(TestRegistryProtocol):
    """Test the VectorStore implementation."""
    
    def get_registry(self):
        """Get a VectorStore instance with a mocked backend."""
        return VectorStore()
