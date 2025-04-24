#!/usr/bin/env python3
"""
Agent with Vector Memory Example

This script demonstrates how to use the VectorStore for agent memory.
It creates an agent that can remember information across interactions.

Usage:
    # To run with in-memory backend (for testing):
    python examples/agent_with_vector_memory.py
    
    # To run with Redis backend:
    VECTOR_PROVIDER=redis REDIS_URL=redis://localhost:6379 python examples/agent_with_vector_memory.py
    
    # To run with Pinecone backend:
    VECTOR_PROVIDER=pinecone PINECONE_API_KEY=your-api-key PINECONE_INDEX=your-index python examples/agent_with_vector_memory.py
"""

import os
import sys
import time
import uuid
import logging
from typing import List, Dict, Any, Optional

# Add the src directory to the path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the VectorStore
from PRISMAgent.storage import VectorStore

# Simulated embedding model (replace with a real embedding model in production)
def get_embedding(text: str, model="text-embedding-3-small") -> List[float]:
    """
    Get an embedding for the given text.
    
    In a real application, this would call an embedding API like OpenAI's.
    For this example, we'll create a very simple embedding.
    """
    import hashlib
    import numpy as np
    
    # Create a deterministic but unique embedding based on the text
    # (This is NOT a real embedding model - just for demonstration)
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert hash to a list of floats
    hash_ints = [int(hash_hex[i:i+2], 16) for i in range(0, len(hash_hex), 2)]
    
    # Normalize to unit length
    embedding = np.array(hash_ints, dtype=float)
    embedding = embedding / np.linalg.norm(embedding)
    
    # Pad or truncate to correct dimension
    dim = int(os.getenv("EMBED_DIM", 1536))
    if len(embedding) < dim:
        embedding = np.pad(embedding, (0, dim - len(embedding)))
    else:
        embedding = embedding[:dim]
    
    return embedding.tolist()

class AgentMemory:
    """
    A simple agent memory system that uses vector storage to remember facts.
    """
    
    def __init__(self):
        """Initialize the agent memory."""
        self.vector_store = VectorStore()
        self.memory_entries = []
        
        # Log which backend we're using
        logging.info(f"Using vector backend: {self.vector_store.backend_name}")
    
    def remember(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory in the vector store.
        
        Args:
            text: The text to remember
            metadata: Additional metadata to store
            
        Returns:
            The memory ID
        """
        # Generate a unique ID for this memory
        memory_id = f"mem-{uuid.uuid4()}"
        
        # Get the embedding for the text
        embedding = get_embedding(text)
        
        # Prepare metadata
        meta = metadata or {}
        meta.update({
            "text": text,
            "timestamp": time.time(),
            "type": "memory"
        })
        
        # Store in vector database
        self.vector_store.upsert(memory_id, embedding, meta)
        
        # Keep track of memories for display purposes
        self.memory_entries.append((memory_id, text))
        
        return memory_id
    
    def recall(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Recall memories similar to the query.
        
        Args:
            query: The query text
            k: Number of results to return
            
        Returns:
            List of memory entries
        """
        # Get the embedding for the query
        query_embedding = get_embedding(query)
        
        # Query the vector store
        results = self.vector_store.query(query_embedding, k=k)
        
        return results.get("matches", [])
    
    def list_memories(self) -> List[tuple]:
        """Return a list of all memories for display purposes."""
        return self.memory_entries

def main():
    # Create an agent memory
    memory = AgentMemory()
    
    # Store some example memories
    memory.remember("My favorite color is blue.")
    memory.remember("I like to eat pizza for dinner.")
    memory.remember("My birthday is on October 15th.")
    memory.remember("I visited Paris last summer and saw the Eiffel Tower.")
    memory.remember("I have a pet cat named Whiskers who is 3 years old.")
    memory.remember("I am learning to play the guitar.")
    memory.remember("My mother's name is Sarah.")
    memory.remember("I graduated from university in 2018.")
    memory.remember("I enjoy hiking in the mountains on weekends.")
    memory.remember("I work as a software engineer at a tech company.")
    
    # User interface loop
    print("\nAgent Memory System")
    print("==================")
    print(f"Using vector backend: {memory.vector_store.backend_name}")
    print("Type 'quit' to exit, 'list' to see all memories, or enter a query to search memories.")
    
    while True:
        user_input = input("\nQuery: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if user_input.lower() == 'list':
            print("\nAll memories:")
            for i, (memory_id, text) in enumerate(memory.list_memories()):
                print(f"{i+1}. {text}")
            continue
            
        if user_input.lower().startswith('add:'):
            # Add a new memory
            new_memory = user_input[4:].strip()
            memory_id = memory.remember(new_memory)
            print(f"Added memory: {new_memory} (ID: {memory_id})")
            continue
        
        # Otherwise, treat as a query
        print("\nSearching for related memories...")
        matches = memory.recall(user_input)
        
        if not matches:
            print("No related memories found.")
        else:
            print("\nRelated memories:")
            for i, match in enumerate(matches):
                score = match.get("score", 0)
                text = match.get("metadata", {}).get("text", "No text")
                print(f"{i+1}. [{score:.4f}] {text}")

if __name__ == "__main__":
    main() 