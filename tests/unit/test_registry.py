"""
Unit tests for PRISMAgent.storage package.

Tests the registry implementation and factory.
"""

import pytest
import os
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any
from PRISMAgent.engine import agent_factory
from PRISMAgent.storage import registry_factory, InMemoryRegistry


def test_registry_factory_returns_singleton():
    """Test that registry_factory returns a singleton instance."""
    registry1 = registry_factory()
    registry2 = registry_factory()
    assert registry1 is registry2
    assert isinstance(registry1, InMemoryRegistry)


def test_registry_cycle():
    """Test that agent_factory uses the registry for caching and retrieval."""
    # Create an agent
    a1 = agent_factory("foo", instructions="hi")
    
    # Request the same agent again with different instructions
    a2 = agent_factory("foo", instructions="ignored")
    
    # Should get the same agent instance
    assert a1 is a2
    
    # Instructions should be from the first creation
    assert a1.instructions == "hi"


def test_registry_different_agents():
    """Test that different agent names don't conflict."""
    a1 = agent_factory("agent1", instructions="first agent")
    a2 = agent_factory("agent2", instructions="second agent")
    
    # Should be different instances
    assert a1 is not a2
    assert a1.name != a2.name
    assert a1.instructions != a2.instructions
    
    # Retrieving again should get the same instances
    retrieved_a1 = agent_factory("agent1", instructions="ignored")
    retrieved_a2 = agent_factory("agent2", instructions="ignored")
    
    assert a1 is retrieved_a1
    assert a2 is retrieved_a2


class TestInMemoryRegistry:
    """Test the InMemoryRegistry implementation."""
    
    def test_registry_init(self):
        """Test registry initialization."""
        registry = InMemoryRegistry()
        assert registry.data == {}
        
    def test_set_get(self):
        """Test setting and getting values."""
        registry = InMemoryRegistry()
        registry.set("test_key", "test_value")
        assert registry.get("test_key") == "test_value"
        
    def test_get_nonexistent(self):
        """Test getting a nonexistent key."""
        registry = InMemoryRegistry()
        assert registry.get("nonexistent") is None
        assert registry.get("nonexistent", "default") == "default"
        
    def test_delete(self):
        """Test deleting a key."""
        registry = InMemoryRegistry()
        registry.set("test_key", "test_value")
        registry.delete("test_key")
        assert registry.get("test_key") is None
        
    def test_list_keys(self):
        """Test listing keys."""
        registry = InMemoryRegistry()
        registry.set("key1", "value1")
        registry.set("key2", "value2")
        keys = registry.list_keys()
        assert set(keys) == {"key1", "key2"}
        
    def test_clear(self):
        """Test clearing the registry."""
        registry = InMemoryRegistry()
        registry.set("key1", "value1")
        registry.set("key2", "value2")
        registry.clear()
        assert registry.data == {}


class TestFileRegistry:
    """Test the FileRegistry implementation."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_registry_init(self, temp_dir):
        """Test registry initialization."""
        registry = InMemoryRegistry(storage_path=temp_dir)
        assert registry.storage_path == Path(temp_dir)
        assert registry.data == {}
        
    def test_load_save(self, temp_dir):
        """Test loading and saving data."""
        registry = InMemoryRegistry(storage_path=temp_dir)
        registry.set("test_key", "test_value")
        
        # Create a new registry instance to test loading
        registry2 = InMemoryRegistry(storage_path=temp_dir)
        assert registry2.get("test_key") == "test_value"
        
    def test_set_get(self, temp_dir):
        """Test setting and getting values."""
        registry = InMemoryRegistry(storage_path=temp_dir)
        registry.set("test_key", "test_value")
        assert registry.get("test_key") == "test_value"
        
        # Complex data
        complex_data = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        registry.set("complex", complex_data)
        assert registry.get("complex") == complex_data
        
    def test_delete(self, temp_dir):
        """Test deleting a key."""
        registry = InMemoryRegistry(storage_path=temp_dir)
        registry.set("test_key", "test_value")
        registry.delete("test_key")
        assert registry.get("test_key") is None
        
        # Verify it's also gone from disk
        assert not os.path.exists(os.path.join(temp_dir, "test_key.json"))
        
    def test_list_keys(self, temp_dir):
        """Test listing keys."""
        registry = InMemoryRegistry(storage_path=temp_dir)
        registry.set("key1", "value1")
        registry.set("key2", "value2")
        keys = registry.list_keys()
        assert set(keys) == {"key1", "key2"}
        
    def test_clear(self, temp_dir):
        """Test clearing the registry."""
        registry = InMemoryRegistry(storage_path=temp_dir)
        registry.set("key1", "value1")
        registry.set("key2", "value2")
        registry.clear()
        assert registry.data == {}
        
        # Verify files are gone from disk
        assert len(os.listdir(temp_dir)) == 0


class TestRegistryFactory:
    """Test the registry_factory function."""
    
    def test_factory_inmemory(self):
        """Test creating an in-memory registry."""
        registry = registry_factory(registry_type="memory")
        assert isinstance(registry, InMemoryRegistry)
        
    def test_factory_file(self, tmp_path):
        """Test creating a file registry."""
        registry = registry_factory(registry_type="file", storage_path=str(tmp_path))
        assert isinstance(registry, InMemoryRegistry)
        assert registry.storage_path == tmp_path
        
    def test_factory_default(self):
        """Test the default registry type."""
        registry = registry_factory()
        assert isinstance(registry, InMemoryRegistry)
        
    def test_factory_invalid(self):
        """Test an invalid registry type."""
        with pytest.raises(ValueError):
            registry_factory(registry_type="invalid")
