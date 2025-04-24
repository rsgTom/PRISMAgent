# PRISM Agent Examples

This directory contains example scripts demonstrating how to use various features of the PRISM Agent framework.

## Vector Storage Examples

- [Vector Store Example](vector_store_example.py) - Basic example of using the vector store with different backends.
- [Agent with Vector Memory](agent_with_vector_memory.py) - Example of using the vector store for agent memory.

## Running the Examples

### Vector Store Example

```bash
# To run with in-memory backend (for testing):
python examples/vector_store_example.py

# To run with Redis backend:
VECTOR_PROVIDER=redis REDIS_URL=redis://localhost:6379 python examples/vector_store_example.py

# To run with RedisVL backend:
VECTOR_PROVIDER=redisvl REDIS_URL=redis://localhost:6379 python examples/vector_store_example.py

# To run with Pinecone backend:
VECTOR_PROVIDER=pinecone PINECONE_API_KEY=your-api-key PINECONE_INDEX=your-index python examples/vector_store_example.py
```

### Agent with Vector Memory

```bash
# To run with in-memory backend (for testing):
python examples/agent_with_vector_memory.py

# To run with Redis backend:
VECTOR_PROVIDER=redis REDIS_URL=redis://localhost:6379 python examples/agent_with_vector_memory.py

# To run with Pinecone backend:
VECTOR_PROVIDER=pinecone PINECONE_API_KEY=your-api-key PINECONE_INDEX=your-index python examples/agent_with_vector_memory.py
```

## Prerequisites

The examples require the PRISM Agent package to be installed or accessible in the Python path. Each example script adds the `src` directory to the Python path automatically.

Depending on the backend you want to use, you'll need to install the appropriate dependencies:

```bash
# For Redis backend
pip install redis

# For RedisVL backend
pip install redisvl

# For Pinecone backend
pip install pinecone-client
```

## Directory Structure

```
examples/
├── README.md                    # This file
├── agent_with_vector_memory.py  # Example of agent memory with vector storage
└── vector_store_example.py      # Basic vector store usage example
```

## Additional Resources

- [Vector Storage Documentation](../docs/api/storage/vector_storage.md) - Documentation for the vector storage module. 