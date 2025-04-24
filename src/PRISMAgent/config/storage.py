"""Storage configuration for PRISMAgent."""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, model_validator


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
    
    @model_validator(mode='after')
    def check_storage_config_consistency(self) -> 'StorageConfig':
        """Ensure only the config corresponding to 'type' is set and validated."""
        if self.type == "file":
            if self.file is None:
                # Initialize with defaults if missing; validation happens automatically
                self.file = FileStorageConfig()
            self.redis = None
            self.supabase = None
            self.vector = None
        elif self.type == "redis":
            if self.redis is None:
                # If type is redis, the redis field should have been populated and validated.
                # If it's None here, it means required fields (like URL env var) might be missing.
                # Pydantic's earlier validation should ideally catch this.
                # We force validation again or raise error if it's None.
                try:
                    self.redis = RedisStorageConfig()
                except ValueError as e:
                    raise ValueError("Redis config is required and validation failed when type is 'redis'. Check REDIS_URL env var.") from e
            self.file = None
            self.supabase = None
            self.vector = None
        elif self.type == "supabase":
            if self.supabase is None:
                 try:
                    self.supabase = SupabaseStorageConfig()
                 except ValueError as e:
                    raise ValueError("Supabase config is required and validation failed when type is 'supabase'. Check SUPABASE_URL/KEY env vars.") from e
            self.file = None
            self.redis = None
            self.vector = None
        elif self.type == "vector":
            if self.vector is None:
                 try:
                    self.vector = VectorStorageConfig()
                 except ValueError as e:
                    raise ValueError("Vector config is required and validation failed when type is 'vector'. Check VECTOR_PROVIDER and related env vars.") from e
            self.file = None
            self.redis = None
            self.supabase = None
        return self 