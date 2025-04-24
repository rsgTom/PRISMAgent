#!/usr/bin/env python3
"""
Vector Store Usage Example

This script demonstrates how to use the VectorStore class with different
backends (Pinecone, Redis, RedisVL).

Usage:
    # To run with in-memory backend (for testing):
    python examples/vector_store_example.py
    
    # To run with Redis backend:
    VECTOR_PROVIDER=redis REDIS_URL=redis://localhost:6379 python examples/vector_store_example.py
    
    # To run with RedisVL backend:
    VECTOR_PROVIDER=redisvl REDIS_URL=redis://localhost:6379 python examples/vector_store_example.py
    
    # To run with Pinecone backend:
    VECTOR_PROVIDER=pinecone PINECONE_API_KEY=your-api-key PINECONE_INDEX=your-index python examples/vector_store_example.py
"""

import os
import sys
import time
import uuid
import numpy as np
from typing import List, Dict, Any

# Add the src directory to the path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the VectorStore
from PRISMAgent.storage import VectorStore

def generate_random_vector(dim: int = 1536) -> List[float]:
    """Generate a random vector with the specified dimension."""
    return list(np.random.random(dim).astype(float))

def generate_sample_metadata() -> Dict[str, Any]:
    """Generate sample metadata for a vector."""
    return {
        "text": f"Sample document {uuid.uuid4()}",
        "tags": ["sample", "example", "vector"],
        "timestamp": time.time(),
        "source": "vector_store_example.py",
        "category": "test"
    }

def main():
    # Create a VectorStore instance
    vector_store = VectorStore()
    
    # Print the backend being used
    print(f"Using vector backend: {vector_store.backend_name}")
    
    # Generate some sample vectors
    vector_dim = int(os.getenv("EMBED_DIM", 1536))
    num_vectors = 5
    
    vectors = []
    for i in range(num_vectors):
        # Generate a unique ID
        uid = f"example-{uuid.uuid4()}"
        
        # Generate a random vector
        vec = generate_random_vector(vector_dim)
        
        # Generate sample metadata
        meta = generate_sample_metadata()
        meta["index"] = i
        
        # Store the vector
        print(f"Storing vector {i+1}/{num_vectors} with ID: {uid}")
        vector_store.upsert(uid, vec, meta)
        
        # Remember the vector for querying
        vectors.append((uid, vec, meta))
    
    # Wait a moment for data to be indexed
    print("Waiting for vectors to be indexed...")
    time.sleep(3)
    
    # Query for similar vectors
    print("\nQuerying for similar vectors:")
    
    # Use the first vector as the query
    query_vec = vectors[0][1]
    
    # Query the vector store
    results = vector_store.query(query_vec, k=3)
    
    # Print the results
    for i, match in enumerate(results.get("matches", [])):
        print(f"Match {i+1}:")
        print(f"  ID: {match.get('id')}")
        print(f"  Score: {match.get('score')}")
        meta = match.get("metadata", {})
        print(f"  Text: {meta.get('text', 'N/A')}")
        print(f"  Tags: {meta.get('tags', [])}")
        print()

if __name__ == "__main__":
    main() 