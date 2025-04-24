# Vector Storage Module

The Vector Storage module provides a unified interface for storing and querying vector embeddings using different backend services.

## Overview

The `VectorStore` class allows you to store and query vector embeddings with metadata. The backend service is determined by environment variables, making it easy to switch between development and production environments without changing code.

## Supported Backends

The following vector database backends are supported:

- **In-Memory** (default): A simple in-memory store for development and testing
- **Redis**: Uses Redis with RediSearch for vector storage and retrieval
- **RedisVL**: Uses Redis Vector Library (RedisVL) for vector operations
- **Pinecone**: Uses Pinecone cloud vector database service

## Installation Requirements

Depending on the backend you want to use, you'll need to install the appropriate dependencies:

```bash
# For Redis backend
pip install redis

# For RedisVL backend
pip install redisvl

# For Pinecone backend
pip install pinecone-client
```

## Configuration

The vector store is configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `VECTOR_PROVIDER` | The vector database provider (`memory`, `redis`, `redisvl`, `pinecone`) | `memory` |
| `EMBED_DIM` | The dimension of the embeddings | `1536` |
| `REDIS_URL` | URL for connecting to Redis (required for Redis backends) | `redis://localhost:6379/0` |
| `REDIS_INDEX` | Index name for Redis | `prisma-vector` |
| `REDIS_PREFIX` | Key prefix for Redis | `vec:` |
| `PINECONE_API_KEY` | API key for Pinecone (required for Pinecone backend) | - |
| `PINECONE_INDEX` | Index name for Pinecone (required for Pinecone backend) | - |

## Usage

### Basic Usage

```python
from PRISMAgent.storage import VectorStore

# Create a vector store with the configured backend
vector_store = VectorStore()

# Store a vector with metadata
vector_id = "doc-1"
vector = [0.1, 0.2, 0.3, ..., 0.9]  # Your embedding vector
metadata = {
    "text": "This is a document about vector databases",
    "tags": ["vector", "database", "embedding"],
    "source": "example.txt"
}

vector_store.upsert(vector_id, vector, metadata)

# Query for similar vectors
query_vector = [0.2, 0.3, 0.4, ..., 0.8]  # Query embedding
results = vector_store.query(query_vector, k=5)

# Process results
for match in results.get("matches", []):
    print(f"ID: {match['id']}, Score: {match['score']}")
    print(f"Text: {match['metadata'].get('text')}")
    print(f"Tags: {match['metadata'].get('tags')}")
    print("---")
```

### Using with Agent Memory

The vector store is particularly useful for agent memory systems. Here's a simple example:

```python
from PRISMAgent.storage import VectorStore
import numpy as np

class AgentMemory:
    def __init__(self):
        self.vector_store = VectorStore()
    
    def remember(self, text, metadata=None):
        """Store a memory with its embedding."""
        # Get embedding for the text (using your preferred embedding model)
        embedding = get_embedding(text)
        
        # Store in vector database
        memory_id = f"mem-{uuid.uuid4()}"
        meta = metadata or {}
        meta["text"] = text
        
        self.vector_store.upsert(memory_id, embedding, meta)
        return memory_id
    
    def recall(self, query, k=5):
        """Recall memories similar to the query."""
        # Get embedding for the query
        query_embedding = get_embedding(query)
        
        # Query the vector store
        results = self.vector_store.query(query_embedding, k=k)
        return results.get("matches", [])

# Example helper function (replace with your embedding model)
def get_embedding(text):
    # This is a placeholder - replace with actual embedding logic
    return np.random.random(1536).tolist()
```

## API Reference

### VectorStore

```python
class VectorStore:
    """
    A unified interface for vector storage backends.
    
    Automatically selects the appropriate backend based on environment variables.
    """
    
    def __init__(self):
        """Initialize the vector store with the appropriate backend."""
        # ...
    
    def upsert(self, uid: str, vec: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a vector with its metadata.
        
        Args:
            uid: Unique identifier for this vector
            vec: The embedding vector
            metadata: Optional metadata to store with the vector
            
        Returns:
            bool: True if successful, False otherwise
        """
        # ...
    
    def query(self, vec: List[float], k: int = 5, filter_expr: Optional[str] = None) -> Dict[str, Any]:
        """
        Find the k most similar vectors.
        
        Args:
            vec: The query vector
            k: Number of results to return
            filter_expr: Optional filter expression (backend-specific)
            
        Returns:
            Dictionary with a "matches" list containing the most similar vectors
        """
        # ...
    
    @property
    def backend_name(self) -> str:
        """Return the name of the active backend."""
        # ...
```

## Backend-Specific Features

### Filter Expressions

Some backends support filter expressions to narrow down query results:

- **Redis**: Supports RediSearch query syntax
- **RedisVL**: Supports RedisVL query syntax
- **Pinecone**: Supports Pinecone metadata filtering

Example with filtering:

```python
# Query with filter (Redis backend)
results = vector_store.query(
    query_vector, 
    k=10, 
    filter_expr="@metadata:(tag1 tag2)"
)

# Query with filter (Pinecone backend)
results = vector_store.query(
    query_vector, 
    k=10, 
    filter_expr='{"tags": {"$in": ["important"]}}'
)
```

## Custom Backend Implementation

If you want to implement a custom vector storage backend, create a new class that implements the following methods:

1. `__init__()`: Initialize the backend
2. `upsert(uid, vec, meta)`: Store a vector with metadata
3. `query(vec, k, filter_expr)`: Query for similar vectors

Then you can extend the `VectorStore` class to support your custom backend. 