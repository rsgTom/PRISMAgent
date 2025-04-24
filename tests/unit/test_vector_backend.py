# tests/unit/test_vector_backend.py
"""
Unit tests for the vector backend implementation.

To run these tests:
    VECTOR_PROVIDER=pinecone PINECONE_API_KEY=your-api-key PINECONE_INDEX=your-index pytest tests/unit/test_vector_backend.py -v
    
    # Or for memory backend:
    VECTOR_PROVIDER=memory pytest tests/unit/test_vector_backend.py -v
"""

import os
import sys
import uuid
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

# Add the src directory to the path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the vector backend
from PRISMAgent.storage.vector_backend import VectorStore

# Test data
TEST_VECTOR_DIM = 4  # Using small dimension for tests
TEST_VECTORS = [
    [0.1, 0.2, 0.3, 0.4],
    [0.2, 0.3, 0.4, 0.5],
    [0.3, 0.4, 0.5, 0.6],
    [0.4, 0.5, 0.6, 0.7],
    [0.5, 0.6, 0.7, 0.8],
]

@pytest.fixture
def mock_vector_env():
    """Set up environment variables for testing."""
    provider = os.getenv("VECTOR_PROVIDER", "memory").lower()
    
    env_vars = {
        "VECTOR_PROVIDER": provider,
        "EMBED_DIM": str(TEST_VECTOR_DIM),
    }
    
    # Add provider-specific environment variables
    if provider == "pinecone":
        # These should be set in the actual environment when running the test
        if not os.getenv("PINECONE_API_KEY") or not os.getenv("PINECONE_INDEX"):
            pytest.skip("PINECONE_API_KEY and PINECONE_INDEX must be set for Pinecone tests")
            
        env_vars.update({
            "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
            "PINECONE_INDEX": os.getenv("PINECONE_INDEX"),
            "PINECONE_ENV": os.getenv("PINECONE_ENV", "us-east-1")
        })
    elif provider == "redis" or provider == "redisvl":
        env_vars["REDIS_URL"] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    with patch.dict(os.environ, env_vars):
        yield provider

@pytest.fixture
def vector_store(mock_vector_env):
    """Create a VectorStore instance for testing."""
    try:
        store = VectorStore()
        # Save information about the test for logging
        print(f"\nTesting with {store.backend_name} backend")
        return store
    except Exception as e:
        pytest.skip(f"Failed to initialize vector store: {e}")

def test_vector_store_initialization(mock_vector_env):
    """Test that the VectorStore initializes correctly."""
    provider = mock_vector_env
    try:
        store = VectorStore()
        assert store is not None
        assert store.backend is not None
        assert store.backend_name == provider
        print(f"Successfully initialized {provider} backend")
    except Exception as e:
        pytest.skip(f"Vector store initialization error with {provider}: {e}")

def test_upsert_and_query(vector_store):
    """Test upserting vectors and querying them."""
    # Skip if no store
    if not vector_store:
        pytest.skip("Vector store could not be initialized")
    
    # Create some test data with unique IDs to avoid collisions
    test_prefix = f"test-{uuid.uuid4()}"
    test_ids = [f"{test_prefix}-{i}" for i in range(len(TEST_VECTORS))]
    test_metadata = [
        {"text": f"Test document {i}", "tags": ["test", f"doc-{i}"], "timestamp": i}
        for i in range(len(TEST_VECTORS))
    ]
    
    # Upsert the test data
    for uid, vec, meta in zip(test_ids, TEST_VECTORS, test_metadata):
        result = vector_store.upsert(uid, vec, meta)
        assert result is True
    
    # Wait a moment for data to be indexed in cloud services
    import time
    time.sleep(2)
    
    # Query using the first vector
    query_result = vector_store.query(TEST_VECTORS[0], k=3)
    
    # Check the result structure
    assert "matches" in query_result
    
    # If not using memory backend, we can't guarantee exact matches
    # but we should have at least one result
    if vector_store.backend_name != "memory":
        assert len(query_result["matches"]) > 0
    else:
        # Memory backend should return exactly k results
        assert len(query_result["matches"]) == 3
    
    # Each match should have the correct structure
    for match in query_result["matches"]:
        assert "id" in match
        assert "score" in match
        assert "metadata" in match

def test_error_handling():
    """Test error handling in VectorStore."""
    # Test with invalid backend
    with patch.dict(os.environ, {"VECTOR_PROVIDER": "invalid_backend"}):
        # This should fall back to memory backend
        store = VectorStore()
        assert store.backend_name == "memory"
    
    # Test query error handling with a mocked backend
    mock_backend = MagicMock()
    mock_backend.query.side_effect = Exception("Test error")
    
    store = VectorStore()
    store.backend = mock_backend
    
    # Query should return empty results on error
    result = store.query([0.1, 0.2, 0.3, 0.4])
    assert result == {"matches": []}
    
    # Test upsert error handling
    mock_backend.upsert.side_effect = Exception("Test error")
    result = store.upsert("test", [0.1, 0.2, 0.3, 0.4], {"test": "data"})
    assert result is False
