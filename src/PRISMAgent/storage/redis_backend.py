"""
Redis Backend for Vector Storage

This module provides integration with Redis for vector storage and search.
It implements a simple interface that matches the other vector store backends.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union

# Global flag to track if Redis is available
REDIS_AVAILABLE = False

try:
    import redis
    from redis.commands.search.field import TextField, TagField, VectorField
    from redis.commands.search.indexDefinition import IndexDefinition, IndexType
    from redis.commands.search.query import Query
    REDIS_AVAILABLE = True
except ImportError:
    # Redis is not available
    pass

logger = logging.getLogger(__name__)

class RedisStore:
    """
    Vector store implementation using Redis with RediSearch.
    
    This class provides an interface for storing and querying vector embeddings
    using Redis and the RediSearch module.
    """
    
    def __init__(self):
        """
        Initialize the Redis store.
        
        Connects to Redis and ensures the vector index exists.
        """
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is not available. Please install with: pip install redis")
        
        # Get configuration from environment
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.index_name = os.getenv("REDIS_INDEX", "prisma-vector")
        self.embed_dim = int(os.getenv("EMBED_DIM", 1536))
        self.prefix = os.getenv("REDIS_PREFIX", "vec:")
        
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url)
        
        # Initialize/get the index
        self._initialize_index()
    
    def _initialize_index(self) -> None:
        """
        Initialize the vector index if it doesn't exist.
        """
        try:
            # Check if index exists
            try:
                self.redis_client.ft(self.index_name).info()
                logger.info(f"Using existing Redis index: {self.index_name}")
                return
            except Exception:
                # Index doesn't exist, create it
                pass
            
            # Define schema for the index
            schema = (
                # Metadata field
                TextField("$.metadata", as_name="metadata"),
                # Vector field for similarity search
                VectorField(
                    "$.vector",
                    "HNSW",  # Hierarchical Navigable Small World
                    {
                        "TYPE": "FLOAT32",
                        "DIM": self.embed_dim,
                        "DISTANCE_METRIC": "COSINE",
                        "INITIAL_CAP": 1000,
                        "M": 16,
                        "EF_CONSTRUCTION": 200,
                    },
                    as_name="vector"
                )
            )
            
            # Create the index
            self.redis_client.ft(self.index_name).create_index(
                schema,
                definition=IndexDefinition(
                    prefix=[self.prefix],
                    index_type=IndexType.JSON
                )
            )
            
            logger.info(f"Created new Redis index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis index: {e}")
            raise
    
    def upsert(self, uid: str, vec: List[float], meta: Dict[str, Any]) -> bool:
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
                "vector": vector_data.tolist(),
                "metadata": meta
            }
            
            # Store the document as JSON
            key = f"{self.prefix}{uid}"
            self.redis_client.json().set(key, "$", document)
            
            return True
        except Exception as e:
            logger.error(f"Error upserting document {uid}: {e}")
            return False
    
    def query(self, 
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
            
            # Create the base query
            query_str = f"*=>[KNN {k} @vector $vector_param AS score]"
            
            # Add filter if provided
            if filter_expr:
                query_str = f"({filter_expr}) {query_str}"
                
            # Create the query object
            query = Query(query_str)\
                .dialect(2)\
                .return_fields("id", "score", "metadata")\
                .sort_by("score", asc=False)\
                .paging(0, k)
            
            # Prepare parameters
            params = {"vector_param": vector_data.tobytes()}
            
            # Execute the query
            result = self.redis_client.ft(self.index_name).search(query, params)
            
            # Format results to match other backends
            matches = []
            for doc in result.docs:
                try:
                    # Extract the ID from the key
                    doc_id = doc.id.replace(self.prefix, "")
                    
                    # Parse metadata (stored as JSON string)
                    metadata = json.loads(doc.metadata) if isinstance(doc.metadata, str) else doc.metadata
                    
                    match = {
                        "id": doc_id,
                        "score": float(doc.score),
                        "metadata": metadata
                    }
                    matches.append(match)
                except Exception as e:
                    logger.error(f"Error processing result {doc.id}: {e}")
            
            return {"matches": matches}
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return {"matches": []} 