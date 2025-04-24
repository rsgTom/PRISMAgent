"""Storage configuration for PRISMAgent."""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator


class FileStorageConfig(BaseModel):
    """Configuration for file-based storage."""
    
    data_dir: str = Field(
        "./data", 
        description="Directory for storing data files"
    )
    create_if_missing: bool = Field(
        True, 
        description="Create directory if it doesn't exist"
    )


class RedisStorageConfig(BaseModel):
    """Configuration for Redis storage."""
    
    url: str = Field(
        ..., 
        description="Redis connection URL", 
        env="REDIS_URL"
    )
    prefix: str = Field(
        "prism:", 
        description="Key prefix for Redis storage"
    )
    ttl: Optional[int] = Field(
        None, 
        description="Time-to-live in seconds for stored data, None for no expiration"
    )


class SupabaseStorageConfig(BaseModel):
    """Configuration for Supabase storage."""
    
    url: str = Field(
        ..., 
        description="Supabase URL", 
        env="SUPABASE_URL"
    )
    key: str = Field(
        ..., 
        description="Supabase API key", 
        env="SUPABASE_KEY"
    )
    table: str = Field(
        "agents", 
        description="Table name for agent data"
    )


class VectorStorageConfig(BaseModel):
    """Configuration for vector storage (Pinecone, etc.)."""
    
    provider: Literal["pinecone", "qdrant", "milvus"] = Field(
        ..., 
        description="Vector store provider"
    )
    api_key: Optional[str] = Field(
        None, 
        description="API key for the vector store", 
        env="PINECONE_API_KEY"
    )
    environment: Optional[str] = Field(
        None, 
        description="Environment for the vector store"
    )
    index_name: str = Field(
        "prism-agent", 
        description="Index name for vector storage"
    )
    namespace: Optional[str] = Field(
        None, 
        description="Namespace for vector storage"
    )
    dimensions: int = Field(
        512, 
        description="Dimensions for vector embeddings"
    )
    metric: Literal["cosine", "euclidean", "dotproduct"] = Field(
        "cosine", 
        description="Distance metric for vector similarity"
    )


class StorageConfig(BaseModel):
    """Configuration for the storage backend."""
    
    type: Literal["file", "redis", "supabase", "vector"] = Field(
        "file", 
        description="Storage backend type", 
        env="STORAGE_TYPE"
    )
    file: Optional[FileStorageConfig] = None
    redis: Optional[RedisStorageConfig] = None
    supabase: Optional[SupabaseStorageConfig] = None
    vector: Optional[VectorStorageConfig] = None
    
    @validator("file", always=True)
    def validate_file_config(cls, v, values):
        """Ensure file config is set when type is file."""
        if values.get("type") == "file" and v is None:
            return FileStorageConfig()
        return v
    
    @validator("redis", always=True)
    def validate_redis_config(cls, v, values):
        """Ensure redis config is set when type is redis."""
        if values.get("type") == "redis" and v is None:
            # This will raise a validation error if REDIS_URL is not set
            return RedisStorageConfig(url="")
        return v
    
    @validator("supabase", always=True)
    def validate_supabase_config(cls, v, values):
        """Ensure supabase config is set when type is supabase."""
        if values.get("type") == "supabase" and v is None:
            # This will raise a validation error if SUPABASE_URL/KEY are not set
            return SupabaseConfig(url="", key="")
        return v
    
    @validator("vector", always=True)
    def validate_vector_config(cls, v, values):
        """Ensure vector config is set when type is vector."""
        if values.get("type") == "vector" and v is None:
            # This will raise a validation error if provider is not specified
            return VectorStorageConfig(provider="pinecone")
        return v 