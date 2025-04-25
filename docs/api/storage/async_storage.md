# Async Storage Backends

The PRISMAgent storage backends have been implemented with async/await patterns to ensure non-blocking I/O operations when used with FastAPI or other async frameworks.

## Why Async Storage?

Modern web applications often use asynchronous frameworks like FastAPI to handle concurrent requests efficiently. When storage operations block the event loop, it can lead to performance bottlenecks, especially under high load. Implementing async patterns in storage backends ensures:

1. Non-blocking I/O operations
2. Better resource utilization
3. Improved scalability
4. Consistent performance under load

## Using Async Storage

All storage operations return awaitable coroutines that must be awaited in an async context:

```python
# Example of using the registry with async/await
from PRISMAgent.storage import registry_factory

async def get_agent_by_name(name: str):
    registry = registry_factory()
    
    # Check if agent exists
    if not await registry.exists(name):
        return None
    
    # Get and return the agent
    return await registry.get_agent(name)
```

## Async Registry Protocol

The `RegistryProtocol` defines the async interface that all storage backends must implement:

```python
class RegistryProtocol(Protocol):
    """Protocol defining the interface for agent registries."""
    
    async def exists(self, name: str) -> bool:
        """Check if an agent with the given name exists."""
        ...
        
    async def get(self, name: str) -> Agent:
        """Get an agent by name. Raises KeyError if not found."""
        ...
    
    async def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name. Returns None if not found."""
        ...
        
    async def register(self, agent: Agent) -> None:
        """Register an agent in the registry."""
        ...
    
    async def list_agents(self) -> List[str]:
        """List all agent names in the registry."""
        ...
```

## Available Async Storage Backends

### InMemoryRegistry

An in-memory implementation of the registry interface. All operations are performed in memory and are very fast, but data is lost when the application restarts.

```python
from PRISMAgent.storage.file_backend import InMemoryRegistry

registry = InMemoryRegistry()
await registry.register(my_agent)
```

### VectorStore

A vector database backend that supports storing and retrieving high-dimensional vectors alongside metadata. VectorStore also implements the registry interface for storing agents.

```python
from PRISMAgent.storage.vector_backend import VectorStore

# Initialize with default namespace
vector_store = VectorStore()

# Store a vector with metadata
await vector_store.upsert("doc-1", embedding_vector, {"text": "Sample document"})

# Query for similar vectors
results = await vector_store.query(query_vector, k=5)
```

## Implementing Custom Async Storage Backends

To implement a custom storage backend, extend `BaseRegistry` and implement all required async methods:

```python
from PRISMAgent.storage.base import BaseRegistry
from typing import Dict, List, Optional
from agents import Agent

class MyCustomRegistry(BaseRegistry):
    """Custom registry implementation."""
    
    def __init__(self):
        """Initialize the custom registry."""
        self._data = {}  # Internal storage
    
    async def exists(self, name: str) -> bool:
        """Check if an agent exists."""
        return name in self._data
    
    async def get(self, name: str) -> Agent:
        """Get an agent by name."""
        if not await self.exists(name):
            raise KeyError(f"Agent '{name}' not found")
        return self._data[name]
    
    async def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name, returns None if not found."""
        return self._data.get(name)
    
    async def register(self, agent: Agent) -> None:
        """Register an agent."""
        self._data[agent.name] = agent
    
    async def list_agents(self) -> List[str]:
        """List all agent names."""
        return list(self._data.keys())
```

## Working with External Services

When implementing async storage backends that interact with external services (databases, APIs, etc.), use `asyncio.run_in_executor()` to run blocking I/O operations in a thread pool:

```python
import asyncio

async def fetch_data_from_external_service(key: str) -> dict:
    """Fetch data from an external service asynchronously."""
    loop = asyncio.get_event_loop()
    # Run the blocking operation in a thread pool
    result = await loop.run_in_executor(
        None,  # Use the default executor
        lambda: external_service.get(key)  # This is a blocking call
    )
    return result
```

This approach ensures that blocking I/O doesn't halt the event loop, maintaining responsive application behavior even when external services are slow to respond.
