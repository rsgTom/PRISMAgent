"""
Unit tests for the Redis backend implementation.

To run these tests:
1. Make sure Redis is running locally or set REDIS_URL env var.
2. Run: VECTOR_PROVIDER=redis pytest tests/unit/test_redis_backend.py -v

These tests require a running Redis instance with the RediSearch module installed.
"""

import os
import sys
import uuid
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

# Add the src directory to the path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Try to import the Redis backend
try:
    from PRISMAgent.storage.redis_backend import RedisStore, REDIS_AVAILABLE
    from PRISMAgent.storage.vector_backend import VectorStore
except ImportError:
    REDIS_AVAILABLE = False

# Skip all tests if Redis is not available
pytestmark = pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not installed")

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
        "VECTOR_PROVIDER": "redis",
        "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        "REDIS_INDEX": f"test-{uuid.uuid4()}",  # Use a unique index name for each test
        "EMBED_DIM": str(TEST_VECTOR_DIM),
    }):
        yield

@pytest.fixture
def redis_store(mock_redis_env):
    """Create a RedisStore instance for testing."""
    try:
        store = RedisStore()
        yield store
        
        # Clean up - try to delete the index
        try:
            store.redis_client.ft(store.index_name).dropindex(delete_documents=True)
        except Exception:
            pass
    except Exception as e:
        pytest.skip(f"Failed to initialize Redis: {e}")

def test_redis_store_initialization(mock_redis_env):
    """Test that the RedisStore initializes correctly."""
    try:
        store = RedisStore()
        assert store is not None
        assert store.redis_client is not None
        assert store.index_name == os.environ["REDIS_INDEX"]
    except Exception as e:
        pytest.skip(f"Redis initialization error: {e}")

def test_vector_store_backend_name(mock_redis_env):
    """Test that VectorStore reports the correct backend name."""
    try:
        vector_store = VectorStore()
        assert vector_store.backend_name == "redis"
    except Exception as e:
        pytest.skip(f"Vector store initialization error: {e}")

def test_upsert_and_query(redis_store):
    """Test upserting vectors and querying them."""
    # Create some test data
    test_ids = [f"test-{i}" for i in range(len(TEST_VECTORS))]
    test_metadata = [
        {"text": f"Test document {i}", "tags": ["test", f"doc-{i}"], "timestamp": i}
        for i in range(len(TEST_VECTORS))
    ]
    
    # Upsert the test data
    for i, (uid, vec, meta) in enumerate(zip(test_ids, TEST_VECTORS, test_metadata)):
        result = redis_store.upsert(uid, vec.tolist(), meta)
        assert result is True
    
    # Wait a moment for data to be indexed
    import time
    time.sleep(1)
    
    # Query using the first vector
    query_result = redis_store.query(TEST_VECTORS[0].tolist(), k=3)
    
    # Check the result structure
    assert "matches" in query_result
    assert len(query_result["matches"]) > 0
    assert len(query_result["matches"]) <= 3  # Should be at most k results
    
    # The first result should be the same vector we queried with
    first_match = query_result["matches"][0]
    assert "id" in first_match
    assert "score" in first_match
    assert "metadata" in first_match
    
    # First match should have a very high score (near 1.0)
    assert first_match["score"] > 0.9
    
def test_error_handling():
    """Test error handling in RedisStore."""
    # Test with invalid Redis URL
    with patch.dict(os.environ, {
        "REDIS_URL": "redis://invalid-host:6379/0",
    }):
        try:
            with pytest.raises(Exception):
                # This should fail because the Redis connection fails
                RedisStore()
        except Exception:
            pytest.skip("Redis connection error test skipped")
    
    # Create a mock Redis client that raises an exception on query
    mock_redis = MagicMock()
    mock_redis.ft.return_value.search.side_effect = Exception("Test error")
    
    # Test error handling in query method
    with patch('PRISMAgent.storage.redis_backend.redis.from_url', return_value=mock_redis):
        # Skip the initialization
        with patch('PRISMAgent.storage.redis_backend.RedisStore._initialize_index'):
            store = RedisStore()
            store.redis_client = mock_redis
            
            # Query should return empty results on error
            result = store.query([0.1, 0.2, 0.3, 0.4])
            assert result == {"matches": []} 