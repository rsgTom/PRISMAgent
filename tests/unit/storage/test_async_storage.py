"""
Unit tests for async storage backends.

These tests verify that storage backends properly implement the async interface
and operate correctly in asynchronous contexts.
"""

import pytest
import asyncio
from typing import Dict, Any, Optional

from agents import Agent
from PRISMAgent.storage.base import BaseRegistry, RegistryProtocol
from PRISMAgent.storage.file_backend import InMemoryRegistry
from PRISMAgent.storage.vector_backend import VectorStore, InMemoryVectorBackend


# Mock agent class for testing
class MockAgent:
    def __init__(self, name: str):
        self.name = name


@pytest.mark.asyncio
async def test_inmemory_registry_async():
    """Test that InMemoryRegistry works properly with async methods."""
    registry = InMemoryRegistry()
    
    # Test agent registration
    agent = MockAgent("test_agent")
    await registry.register(agent)
    
    # Test exists method
    assert await registry.exists("test_agent")
    assert not await registry.exists("nonexistent_agent")
    
    # Test get_agent method
    retrieved_agent = await registry.get_agent("test_agent")
    assert retrieved_agent.name == "test_agent"
    
    # Test get method with nonexistent agent should raise KeyError
    with pytest.raises(KeyError):
        await registry.get("nonexistent_agent")
    
    # Test list_agents method
    agents = await registry.list_agents()
    assert "test_agent" in agents
    assert len(agents) == 1


@pytest.mark.asyncio
async def test_vector_store_async():
    """Test that VectorStore works properly with async methods."""
    vector_store = VectorStore()
    
    # Test agent registration
    agent = MockAgent("vector_agent")
    await vector_store.register(agent)
    
    # Test exists method
    assert await vector_store.exists("vector_agent")
    assert not await vector_store.exists("nonexistent_agent")
    
    # Test get_agent method
    retrieved_agent = await vector_store.get_agent("vector_agent")
    assert retrieved_agent.name == "vector_agent"
    
    # Test list_agents method
    agents = await vector_store.list_agents()
    assert "vector_agent" in agents
    assert len(agents) == 1


@pytest.mark.asyncio
async def test_inmemory_vector_backend_async():
    """Test that InMemoryVectorBackend works properly with async methods."""
    backend = InMemoryVectorBackend()
    
    # Test upsert and get method
    vector = [0.1, 0.2, 0.3, 0.4]
    metadata = {"key": "value"}
    
    success = await backend.upsert("test_vector", vector, metadata)
    assert success
    
    # Test get method
    retrieved = await backend.get("test_vector")
    assert retrieved is not None
    assert retrieved["id"] == "test_vector"
    assert retrieved["vector"] == vector
    assert retrieved["metadata"] == metadata
    
    # Test query method
    query_vector = [0.1, 0.2, 0.3, 0.4]  # Same vector for simplicity
    results = await backend.query(query_vector, k=1)
    
    assert "matches" in results
    assert len(results["matches"]) == 1
    assert results["matches"][0]["id"] == "test_vector"
    assert results["matches"][0]["score"] == 1.0  # Perfect match
    
    # Test delete method
    success = await backend.delete("test_vector")
    assert success
    
    # Verify deletion
    retrieved = await backend.get("test_vector")
    assert retrieved is None


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent operations on async storage backends."""
    registry = InMemoryRegistry()
    
    # Create multiple agents
    agents = [MockAgent(f"agent_{i}") for i in range(10)]
    
    # Register agents concurrently
    await asyncio.gather(*(registry.register(agent) for agent in agents))
    
    # Verify all agents were registered
    agent_names = await registry.list_agents()
    assert len(agent_names) == 10
    
    # Retrieve agents concurrently
    retrieved_agents = await asyncio.gather(
        *(registry.get_agent(f"agent_{i}") for i in range(10))
    )
    
    # Verify all agents were retrieved correctly
    for i, agent in enumerate(retrieved_agents):
        assert agent.name == f"agent_{i}"
