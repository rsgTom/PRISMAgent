# Storage API

The Storage module provides different backends for persisting agent data.

## Base Classes and Protocols

### MemoryProvider

```python
class MemoryProvider(Protocol):
    """Protocol for memory providers."""
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from storage."""
        ...
        
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set a value in storage."""
        ...
        
    async def delete(self, key: str) -> None:
        """Delete a value from storage."""
        ...
```

### Registry

```python
class Registry:
    """Registry for backend storage providers."""
    
    @classmethod
    def register(cls, name: str, provider_class: Type[MemoryProvider]) -> None:
        """Register a provider class."""
        
    @classmethod
    def get_provider(cls, name: str) -> Type[MemoryProvider]:
        """Get a provider class by name."""
        
    @classmethod
    def create(cls, provider_type: str, **kwargs) -> MemoryProvider:
        """Create a provider instance."""
```

## File Storage

```python
class FileStorageBackend(MemoryProvider):
    """File-based storage backend."""
    
    def __init__(self, data_dir: str = "./data", create_if_missing: bool = True):
        """
        Initialize file storage.
        
        Args:
            data_dir: Directory to store data files
            create_if_missing: Whether to create the directory if it doesn't exist
        """
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from file storage."""
        
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set a value in file storage."""
        
    async def delete(self, key: str) -> None:
        """Delete a value from file storage."""
```

## Redis Storage

```python
class RedisStorageBackend(MemoryProvider):
    """Redis-based storage backend."""
    
    def __init__(self, url: str, prefix: str = "prism:", ttl: Optional[int] = None):
        """
        Initialize Redis storage.
        
        Args:
            url: Redis connection URL
            prefix: Key prefix for Redis storage
            ttl: Time-to-live in seconds for stored data, None for no expiration
        """
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from Redis storage."""
        
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set a value in Redis storage."""
        
    async def delete(self, key: str) -> None:
        """Delete a value from Redis storage."""
```

## Supabase Storage

```python
class SupabaseStorageBackend(MemoryProvider):
    """Supabase-based storage backend."""
    
    def __init__(self, url: str, key: str, table: str = "agents"):
        """
        Initialize Supabase storage.
        
        Args:
            url: Supabase URL
            key: Supabase API key
            table: Table name for agent data
        """
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from Supabase storage."""
        
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set a value in Supabase storage."""
        
    async def delete(self, key: str) -> None:
        """Delete a value from Supabase storage."""
```

## Vector Storage

```python
class VectorStorageBackend(MemoryProvider):
    """Vector-based storage backend."""
    
    def __init__(
        self,
        provider: Literal["pinecone", "qdrant", "milvus"],
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: str = "prism-agent",
        namespace: Optional[str] = None,
        dimensions: int = 1536,
        metric: Literal["cosine", "euclidean", "dotproduct"] = "cosine"
    ):
        """
        Initialize vector storage.
        
        Args:
            provider: Vector store provider
            api_key: API key for the vector store
            environment: Environment for the vector store
            index_name: Index name for vector storage
            namespace: Namespace for vector storage
            dimensions: Dimensions for vector embeddings
            metric: Distance metric for vector similarity
        """
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from vector storage."""
        
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set a value in vector storage."""
        
    async def delete(self, key: str) -> None:
        """Delete a value from vector storage."""
        
    async def search(self, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
```

## Usage Example

```python
# Using file storage
file_storage = FileStorageBackend(data_dir="./data")
await file_storage.set("agent_1", {"messages": [{"role": "user", "content": "Hello"}]})
data = await file_storage.get("agent_1")

# Using Redis storage
redis_storage = RedisStorageBackend(url="redis://localhost:6379/0")
await redis_storage.set("agent_1", {"messages": [{"role": "user", "content": "Hello"}]})
data = await redis_storage.get("agent_1")

# Dynamic creation through registry
storage = Registry.create(
    provider_type="redis",
    url="redis://localhost:6379/0"
)
``` 