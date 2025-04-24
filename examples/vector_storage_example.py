#!/usr/bin/env python3
"""
Vector Storage Example

This example demonstrates how to use the PRISMAgent vector storage backends.

To run with Pinecone:
    VECTOR_PROVIDER=pinecone PINECONE_API_KEY=your-api-key PINECONE_INDEX=your-index python examples/vector_storage_example.py

To run with in-memory backend:
    VECTOR_PROVIDER=memory python examples/vector_storage_example.py
"""

import os
import sys
import time
import uuid
import random
import numpy as np
from typing import List, Dict

# Add the src directory to the path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the vector backend
from PRISMAgent.storage import vector_backend
from PRISMAgent.storage.vector_backend import VectorStore

def generate_random_vector(dim: int = 4) -> List[float]:
    """Generate a random unit vector of the specified dimension."""
    vec = [random.random() for _ in range(dim)]
    # Normalize to unit length
    magnitude = sum(x*x for x in vec) ** 0.5
    return [x/magnitude for x in vec]

def store_sample_vectors(store: VectorStore, num_vectors: int = 5, dim: int = 4) -> List[str]:
    """
    Store sample vectors in the vector store.
    
    Args:
        store: The vector store instance
        num_vectors: Number of vectors to generate
        dim: Dimension of vectors
        
    Returns:
        List of vector IDs
    """
    vector_ids = []
    
    print(f"Storing {num_vectors} sample vectors...")
    for i in range(num_vectors):
        # Generate a unique ID
        vector_id = f"test-{uuid.uuid4()}"
        vector_ids.append(vector_id)
        
        # Generate a random vector
        vector = generate_random_vector(dim)
        
        # Create sample metadata
        metadata = {
            "title": f"Test Document {i+1}",
            "tags": ["test", f"doc-{i+1}"],
            "category": random.choice(["A", "B", "C"]),
            "importance": random.randint(1, 5),
            "timestamp": time.time()
        }
        
        # Store the vector
        success = store.upsert(vector_id, vector, metadata)
        if success:
            print(f"  ✓ Stored vector {i+1}/{num_vectors} with ID: {vector_id}")
        else:
            print(f"  ✗ Failed to store vector {i+1}/{num_vectors}")
    
    return vector_ids

def run_sample_queries(store: VectorStore, vector_dim: int = 4):
    """
    Run some sample queries against the vector store.
    
    Args:
        store: The vector store instance
        vector_dim: Dimension of vectors in the store
    """
    print("\nRunning sample queries...")
    
    # Query 1: Basic similarity search
    query_vector = generate_random_vector(vector_dim)
    print("\nQuery 1: Basic similarity search (top 3 results)")
    results = store.query(query_vector, k=3)
    display_results(results)
    
    # Query 2: With filter
    query_vector = generate_random_vector(vector_dim)
    print("\nQuery 2: Filtered search (category = 'A', top 3 results)")
    filter_expr = {"category": "A"}
    results = store.query(query_vector, k=3, filter_expr=filter_expr)
    display_results(results)
    
    # Query 3: Different filter
    query_vector = generate_random_vector(vector_dim)
    print("\nQuery 3: Filtered search (importance >= 4, top 3 results)")
    # Note: Filter syntax varies by backend
    # This works for in-memory backend, but may need adjustment for other backends
    filter_expr = {"importance": {"$gte": 4}} if store.backend_name != "memory" else {"importance": 4}
    results = store.query(query_vector, k=3, filter_expr=filter_expr)
    display_results(results)

def display_results(results: Dict):
    """
    Display query results in a readable format.
    
    Args:
        results: The query results from the vector store
    """
    matches = results.get("matches", [])
    
    if not matches:
        print("  No results found")
        return
    
    print(f"  Found {len(matches)} results:")
    for i, match in enumerate(matches):
        print(f"  Result {i+1}:")
        print(f"    ID: {match.get('id')}")
        print(f"    Score: {match.get('score', 0):.4f}")
        
        metadata = match.get("metadata", {})
        if metadata:
            print(f"    Metadata:")
            for key, value in metadata.items():
                print(f"      {key}: {value}")
        print()

def main():
    """Run the vector storage example."""
    # Determine vector dimension from environment or use default
    vector_dim = int(os.getenv("EMBED_DIM", "4"))
    
    print(f"Vector Storage Example (dimension: {vector_dim})")
    print(f"Provider: {os.getenv('VECTOR_PROVIDER', 'memory')}")
    
    # Initialize the vector store
    try:
        store = VectorStore()
        print(f"Successfully initialized {store.backend_name} backend")
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        return
    
    # Store sample vectors
    vector_ids = store_sample_vectors(store, num_vectors=10, dim=vector_dim)
    
    # Wait a moment for vectors to be indexed (especially for cloud services)
    if store.backend_name != "memory":
        print("\nWaiting for vectors to be indexed...")
        time.sleep(2)
    
    # Run sample queries
    run_sample_queries(store, vector_dim)
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main() 