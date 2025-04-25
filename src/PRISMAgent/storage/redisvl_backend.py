# redisvl_backend.py
"""
RedisVL Backend for Vector Storage

This module provides integration with Redis Vector Library (RedisVL) for vector storage and search.
It implements a simple interface that matches the other vector store backends.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union

# Global flag to track if RedisVL is available
REDISVL_AVAILABLE = False

try:
    from redisvl.index import SearchIndex
    from redisvl.schema import IndexSchema, TextField, TagField, VectorField
    from redisvl.query import Query
    import redis
    import redis.asyncio as aioredis
    REDISVL_AVAILABLE = True
except ImportError:
    # RedisVL is not available
    pass

logger = logging.getLogger(__name__)

class RedisVLStore:
    """
    Vector store implementation using RedisVL.
    
    This class provides an interface for storing and querying vector embeddings
    using the Redis Vector Library (RedisVL).
    """
    
    def __init__(self):
        """
        Initialize the RedisVL store.
        
        Connects to Redis and ensures the vector index exists.
        """
        if not REDISVL_AVAILABLE:
            raise ImportError("RedisVL is not available. Please install with: pip install redisvl")
        
        # Get configuration from environment
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.index_name = os.getenv("REDIS_INDEX", "prisma-memory")
        self.embed_dim = int(os.getenv("EMBED_DIM", 1536))
        self.prefix = os.getenv("REDIS_PREFIX", "mem:")
        
        # Connect to Redis (sync client for initialization)
        self.redis_client = redis.from_url(self.redis_url)
        
        # Async Redis client for operations
        self.async_redis_client = aioredis.from_url(self.redis_url)
        
        # Initialize/get the index
        self._initialize_index()
    
    def _initialize_index(self) -> None:
        """
        Initialize the vector index if it doesn't exist.
        """
        try:
            # Define schema for the index
            schema = IndexSchema([
                # Metadata fields
                TextField(name="metadata", sortable=False, no_index=False),
                # Vector field for similarity search
                VectorField(
                    name="vector",
                    algorithm="HNSW",  # Hierarchical Navigable Small World
                    attributes={
                        "TYPE": "FLOAT32",
                        "DIM": self.embed_dim,
                        "DISTANCE_METRIC": "COSINE",
                        "EF_CONSTRUCTION": 200,
                        "M": 16,
                        "EF_RUNTIME": 10,
                    }
                )
            ])
            
            # Create index object
            self.index = SearchIndex(
                name=self.index_name,
                schema=schema,
                prefix=self.prefix,
                client=self.redis_client
            )
            
            # Create async index object for operations
            # Note: RedisVL doesn't have a native async client, so we'll use our own wrappers
            
            # Check if index exists, create if it doesn't
            try:
                self.index.info()
                logger.info(f"Using existing RedisVL index: {self.index_name}")
            except Exception:
                # Create the index
                self.index.create()
                logger.info(f"Created new RedisVL index: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize RedisVL index: {e}")
            raise
    
    async def upsert(self, uid: str, vec: List[float], meta: Dict[str, Any]) -> bool:
        """
        Store a vector with its metadata.
        
        Args:
            uid: Unique identifier for this vector
            vec: The embedding vector
            meta: Metadata to store with the vector
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert vector to numpy array
            vector_data = np.array(vec).astype(np.float32)
            
            # Prepare document for storage
            document = {
                "vector": vector_data,
                "metadata": json.dumps(meta)
            }
            
            # Store the document
            # Note: RedisVL doesn't have native async support, so we're using the sync client
            # in an async function. In a production environment, we'd want to use
            # asyncio.to_thread() to avoid blocking the event loop.
            self.index.load(
                [{"id": uid, **document}]
            )
            
            return True
        except Exception as e:
            logger.error(f"Error upserting document {uid}: {e}")
            return False
    
    async def query(self, 
             vec: List[float], 
             k: int = 5, 
             filter_expr: Optional[str] = None) -> Dict[str, Any]:
        """
        Find the k most similar vectors.
        
        Args:
            vec: The query vector
            k: Number of results to return
            filter_expr: Optional filter expression
            
        Returns:
            Dictionary with a "matches" list containing the most similar vectors
        """
        try:
            # Convert vector to numpy array
            vector_data = np.array(vec).astype(np.float32)
            
            # Create query
            query = Query(
                vector=vector_data,
                vector_field_name="vector",
                return_fields=["metadata", "vector_score"],
                num_results=k
            )
            
            # Add filter if provided
            if filter_expr:
                query.filter(filter_expr)
            
            # Execute query
            # Note: RedisVL doesn't have native async support, so we're using the sync client 
            # in an async function.
            response = self.index.query(query)
            
            # Format results to match other backends
            matches = []
            for result in response.docs:
                try:
                    match = {
                        "id": result.id,
                        "score": 1.0 - float(result.vector_score),  # Convert distance to similarity
                        "metadata": json.loads(result.metadata)
                    }
                    matches.append(match)
                except Exception as e:
                    logger.error(f"Error processing result {result.id}: {e}")
            
            return {"matches": matches}
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return {"matches": []}

    async def delete(self, uid: str) -> bool:
        """Delete a vector from the index.
        
        Args:
            uid: Unique identifier for the vector to delete
            
        Returns:
            Boolean indicating success
        """
        if not REDISVL_AVAILABLE or self.index is None:
            logger.warning("RedisVL not available. No data will be deleted.")
            return False
            
        try:
            self.index.delete(uid)
            return True
        except Exception as e:
            logger.error(f"Error deleting from RedisVL: {e}")
            return False
            
    async def clear(self) -> bool:
        """Clear all vectors from the index.
        
        Returns:
            Boolean indicating success
        """
        if not REDISVL_AVAILABLE or self.index is None:
            logger.warning("RedisVL not available. No data will be cleared.")
            return False
            
        try:
            # Drop and recreate the index
            self.index.delete()
            self.index.create()
            return True
        except Exception as e:
            logger.error(f"Error clearing RedisVL index: {e}")
            return False
            
    async def count(self) -> int:
        """Return the number of vectors in the index.
        
        Returns:
            int: Number of vectors
        """
        if not REDISVL_AVAILABLE or self.index is None:
            logger.warning("RedisVL not available. Cannot count vectors.")
            return 0
            
        try:
            # Note: RedisVL doesn't have a direct count method
            # We use a query with high limit to get all documents and count them
            query = Query(
                vector=np.zeros(self.embed_dim).astype(np.float32),
                vector_field_name="vector",
                return_fields=["id"],
                num_results=10000  # Large number to get all documents
            )
            response = self.index.query(query)
            return len(response.docs)
        except Exception as e:
            logger.error(f"Error counting vectors in RedisVL: {e}")
            return 0
