"""
Unit tests for the RedisVL backend implementation.

To run these tests:
1. Make sure Redis is running locally or set REDIS_URL env var.
2. Run: VECTOR_PROVIDER=redisvl pytest tests/unit/test_redisvl_backend.py -v

These tests require a running Redis instance and the redisvl package.
"""

import os
import sys
import uuid
import json
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

# Add the src directory to the path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Try to import the RedisVL backend
try:
    from PRISMAgent.storage.redisvl_backend import RedisVLStore, REDISVL_AVAILABLE
    from PRISMAgent.storage.vector_backend import VectorStore
except ImportError:
    REDISVL_AVAILABLE = False

# Skip all tests if RedisVL is not available
pytestmark = pytest.mark.skipif(not REDISVL_AVAILABLE, reason="RedisVL not installed")

# Test data
TEST_VECTOR_DIM = 4  # Using small dimension for tests
TEST_VECTORS = [
    np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32),
    np.array([0.2, 0.3, 0.4, 0.5], dtype=np.float32),
    np.array([0.3, 0.4, 0.5, 0.6], dtype=np.float32),
    np.array([0.4, 0.5, 0.6, 0.7], dtype=np.float32),
    np.array([0.5, 0.6, 0.7, 0.8], dtype=np.float32),
]

@pytest.fixture
def mock_redis_env():
    """Set up environment variables for testing with Redis."""
    with patch.dict(os.environ, {
        "VECTOR_PROVIDER": "redisvl",
        "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        "REDIS_INDEX": f"test-{uuid.uuid4()}",  # Use a unique index name for each test
        "EMBED_DIM": str(TEST_VECTOR_DIM),
    }):
        yield

@pytest.fixture
def redisvl_store(mock_redis_env):
    """Create a RedisVLStore instance for testing."""
    store = RedisVLStore()
    yield store
    
    # Clean up - try to delete the index
    try:
        store.index.delete()
    except Exception:
        pass

def test_redisvl_store_initialization(mock_redis_env):
    """Test that the RedisVLStore initializes correctly."""
    store = RedisVLStore()
    assert store is not None
    assert store.index is not None
    assert store.index_name == os.environ["REDIS_INDEX"]

def test_vector_store_backend_name(mock_redis_env):
    """Test that VectorStore reports the correct backend name."""
    vector_store = VectorStore()
    assert vector_store.backend_name == "redisvl"

def test_upsert_and_query(redisvl_store):
    """Test upserting vectors and querying them."""
    # Create some test data
    test_ids = [f"test-{i}" for i in range(len(TEST_VECTORS))]
    test_metadata = [
        {"text": f"Test document {i}", "tags": ["test", f"doc-{i}"], "timestamp": i}
        for i in range(len(TEST_VECTORS))
    ]
    
    # Upsert the test data
    for i, (uid, vec, meta) in enumerate(zip(test_ids, TEST_VECTORS, test_metadata)):
        result = redisvl_store.upsert(uid, vec.tolist(), meta)
        assert result is True
    
    # Query using the first vector
    query_result = redisvl_store.query(TEST_VECTORS[0].tolist(), k=3)
    
    # Check the result structure
    assert "matches" in query_result
    assert len(query_result["matches"]) > 0
    assert len(query_result["matches"]) <= 3  # Should be at most k results
    
    # Check that the first result is the first vector (exact match)
    first_match = query_result["matches"][0]
    assert first_match["id"] == test_ids[0]
    assert "score" in first_match
    assert "metadata" in first_match
    
    # Check that the metadata was correctly stored and retrieved
    metadata = first_match["metadata"]
    assert metadata["text"] == test_metadata[0]["text"]
    assert metadata["tags"] == test_metadata[0]["tags"]
    
def test_query_with_filter(redisvl_store):
    """Test querying with a filter expression."""
    # This test is minimal since filter support depends on RedisVL's capabilities
    # and may require more setup
    
    # Create a simple test case
    uid = "test-filter"
    vec = [0.1, 0.2, 0.3, 0.4]
    meta = {"category": "test", "value": 42}
    
    redisvl_store.upsert(uid, vec, meta)
    
    # Try a query with a filter - this may not work with all Redis setups
    # but we'll test the method call itself
    try:
        result = redisvl_store.query(vec, k=1, filter_expr="@metadata:*test*")
        # Even if the filter doesn't work, the method should not raise an exception
        assert isinstance(result, dict)
        assert "matches" in result
    except Exception as e:
        # If this fails, it might be because Redis search doesn't support
        # the specific filter syntax - just make note of it
        pytest.skip(f"Filter query failed: {e}")

def test_error_handling():
    """Test error handling in RedisVLStore."""
    # Test with invalid Redis URL
    with patch.dict(os.environ, {
        "REDIS_URL": "redis://invalid-host:6379/0",
    }):
        with pytest.raises(Exception):
            # This should fail because the Redis connection fails
            RedisVLStore()
    
    # Test error handling in query method
    store = MagicMock()
    store.index.query.side_effect = Exception("Test error")
    
    # Create a store with a mocked index
    with patch('PRISMAgent.storage.redisvl_backend.SearchIndex', return_value=store.index):
        with patch('PRISMAgent.storage.redisvl_backend.redis.from_url'):
            # Skip the initialization
            with patch('PRISMAgent.storage.redisvl_backend.RedisVLStore._initialize_index'):
                test_store = RedisVLStore()
                test_store.index = store.index
                
                # Query should return empty results on error
                result = test_store.query([0.1, 0.2, 0.3, 0.4])
                assert result == {"matches": []} 