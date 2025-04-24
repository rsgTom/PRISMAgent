"""
Unit tests for the in-memory backend implementation.

To run these tests:
    pytest tests/unit/test_memory_backend.py -v
"""

import os
import sys
import pytest
import numpy as np
from unittest.mock import patch

# Add the src directory to the path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the memory backend
from PRISMAgent.storage.memory_backend import InMemoryStore
from PRISMAgent.storage.vector_backend import VectorStore

# Test data
TEST_VECTOR_DIM = 4
TEST_VECTORS = [
    [0.1, 0.2, 0.3, 0.4],
    [0.2, 0.3, 0.4, 0.5],
    [0.3, 0.4, 0.5, 0.6],
    [0.4, 0.5, 0.6, 0.7],
    [0.5, 0.6, 0.7, 0.8],
]

@pytest.fixture
def mock_memory_env():
    """Set up environment variables for testing with memory backend."""
    with patch.dict(os.environ, {
        "VECTOR_PROVIDER": "memory",
        "EMBED_DIM": str(TEST_VECTOR_DIM),
    }):
        yield

@pytest.fixture
def memory_store():
    """Create an InMemoryStore instance for testing."""
    return InMemoryStore()

def test_memory_store_initialization():
    """Test that the InMemoryStore initializes correctly."""
    store = InMemoryStore()
    assert store is not None
    assert isinstance(store.vectors, dict)
    assert isinstance(store.metadata, dict)
    assert len(store.vectors) == 0
    assert len(store.metadata) == 0

def test_vector_store_backend_name(mock_memory_env):
    """Test that VectorStore reports the correct backend name."""
    vector_store = VectorStore()
    assert vector_store.backend_name == "memory"

def test_upsert_and_query(memory_store):
    """Test upserting vectors and querying them."""
    # Create some test data
    test_ids = [f"test-{i}" for i in range(len(TEST_VECTORS))]
    test_metadata = [
        {"text": f"Test document {i}", "tags": ["test", f"doc-{i}"], "timestamp": i}
        for i in range(len(TEST_VECTORS))
    ]
    
    # Upsert the test data
    for uid, vec, meta in zip(test_ids, TEST_VECTORS, test_metadata):
        result = memory_store.upsert(uid, vec, meta)
        assert result is True
    
    # Check that we have the right number of vectors
    assert len(memory_store.vectors) == len(TEST_VECTORS)
    assert len(memory_store.metadata) == len(TEST_VECTORS)
    
    # Query using the first vector
    query_result = memory_store.query(TEST_VECTORS[0], k=3)
    
    # Check the result structure
    assert "matches" in query_result
    assert len(query_result["matches"]) == 3  # Should be exactly k results
    
    # First match should be the same vector we queried with
    first_match = query_result["matches"][0]
    assert first_match["id"] == test_ids[0]
    assert first_match["score"] == 1.0  # Perfect match (identical vector)
    assert first_match["metadata"] == test_metadata[0]
    
    # Test with a smaller k
    query_result = memory_store.query(TEST_VECTORS[0], k=2)
    assert len(query_result["matches"]) == 2
    
    # Test with a larger k (should be capped at the number of vectors)
    query_result = memory_store.query(TEST_VECTORS[0], k=10)
    assert len(query_result["matches"]) == len(TEST_VECTORS)

def test_delete(memory_store):
    """Test deleting vectors."""
    # Add a vector
    memory_store.upsert("test-id", [0.1, 0.2, 0.3, 0.4], {"test": "metadata"})
    assert len(memory_store.vectors) == 1
    
    # Delete the vector
    result = memory_store.delete("test-id")
    assert result is True
    
    # Check it's gone
    assert len(memory_store.vectors) == 0
    assert len(memory_store.metadata) == 0
    
    # Try to delete a non-existent vector
    result = memory_store.delete("nonexistent")
    assert result is False

def test_clear(memory_store):
    """Test clearing all vectors."""
    # Add some vectors
    for i in range(5):
        memory_store.upsert(f"test-{i}", [0.1, 0.2, 0.3, 0.4], {"test": i})
    
    assert len(memory_store.vectors) == 5
    
    # Clear the store
    memory_store.clear()
    
    # Check it's empty
    assert len(memory_store.vectors) == 0
    assert len(memory_store.metadata) == 0

def test_count(memory_store):
    """Test counting vectors."""
    assert memory_store.count() == 0
    
    # Add some vectors
    for i in range(3):
        memory_store.upsert(f"test-{i}", [0.1, 0.2, 0.3, 0.4], {"test": i})
    
    assert memory_store.count() == 3
    
    # Delete one
    memory_store.delete("test-1")
    assert memory_store.count() == 2

def test_query_with_empty_store(memory_store):
    """Test querying an empty store."""
    result = memory_store.query([0.1, 0.2, 0.3, 0.4])
    assert result == {"matches": []}

def test_query_with_filter_expr(memory_store):
    """Test querying with a filter expression (should be ignored)."""
    # Add a vector
    memory_store.upsert("test-id", [0.1, 0.2, 0.3, 0.4], {"test": "metadata"})
    
    # Query with a filter expression
    result = memory_store.query([0.1, 0.2, 0.3, 0.4], filter_expr="test filter")
    
    # Should still return results (filter is ignored)
    assert len(result["matches"]) == 1

def test_zero_vector_handling(memory_store):
    """Test handling of zero vectors."""
    # Add a zero vector
    memory_store.upsert("zero-vec", [0, 0, 0, 0], {"test": "zero"})
    
    # Add a normal vector
    memory_store.upsert("normal-vec", [0.1, 0.2, 0.3, 0.4], {"test": "normal"})
    
    # Query with a zero vector
    result = memory_store.query([0, 0, 0, 0])
    
    # Should handle this case without errors
    assert len(result["matches"]) == 2
    
    # Zero vectors should have similarity of 0
    zero_matches = [m for m in result["matches"] if m["id"] == "zero-vec"]
    assert len(zero_matches) == 1
    assert zero_matches[0]["score"] == 0.0 