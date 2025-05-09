"""
Pinecone Vector Database Backend

This module provides a Pinecone implementation for vector storage.
It supports both the new (v3+) and legacy Pinecone Python SDKs.
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

# Check if Pinecone is available, first trying new API then legacy
PINECONE_AVAILABLE = False
PINECONE_VERSION = None

try:
    # Try new Pinecone client first (v3+)
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
    PINECONE_VERSION = "new"
    logger.info("Using new Pinecone SDK (v3+)")
except ImportError:
    try:
        # Try legacy Pinecone client
        import pinecone
        PINECONE_AVAILABLE = True
        PINECONE_VERSION = "legacy"
        logger.info("Using legacy Pinecone SDK")
    except ImportError:
        logger.warning("Pinecone SDK not available. Install with: pip install pinecone-client")

class PineconeStore:
    """
    Pinecone vector database implementation.
    
    This class supports both the new (v3+) and legacy Pinecone SDKs.
    """
    
    def __init__(self):
        """
        Initialize the Pinecone vector store.
        
        Required environment variables:
        - PINECONE_API_KEY: Your Pinecone API key
        - PINECONE_INDEX: Name of the Pinecone index to use
        - PINECONE_ENV: (Legacy only) Pinecone environment (e.g., us-east-1)
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone SDK not installed. Run 'pip install pinecone-client'")
        
        # Get configuration from environment
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX")
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable must be set")
        
        if not self.index_name:
            raise ValueError("PINECONE_INDEX environment variable must be set")
        
        # Initialize the appropriate client
        if PINECONE_VERSION == "new":
            self._init_new_pinecone()
        else:
            self._init_legacy_pinecone()
    
    def _init_new_pinecone(self):
        """Initialize using the new Pinecone SDK."""
        try:
            # Initialize the client
            pc = Pinecone(api_key=self.api_key)
            
            # Get the index
            self.index = pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone (new SDK): {e}")
            raise
    
    def _init_legacy_pinecone(self):
        """Initialize using the legacy Pinecone SDK."""
        try:
            # Get the environment from env vars
            environment = os.getenv("PINECONE_ENV")
            
            if not environment:
                raise ValueError("PINECONE_ENV environment variable must be set for legacy Pinecone SDK")
            
            # Initialize the client
            pinecone.init(api_key=self.api_key, environment=environment)
            
            # Get the index
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name} in environment: {environment}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone (legacy SDK): {e}")
            raise
    
    async def upsert(self, 
               uid: str, 
               vec: List[float], 
               metadata: Dict[str, Any] = None) -> bool:
        """
        Insert or update a vector in the Pinecone index.
        
        Args:
            uid: Unique ID for the vector
            vec: Vector data (list of floats)
            metadata: Optional metadata associated with the vector
            
        Returns:
            bool: True if successful
        """
        try:
            metadata = metadata or {}
            
            # Pinecone operations are synchronous, so wrap in asyncio.to_thread 
            # to avoid blocking the event loop in async environments
            
            # Upsert the vector - API is the same for both SDK versions
            if PINECONE_VERSION == "new":
                await asyncio.to_thread(
                    self.index.upsert,
                    vectors=[{
                        "id": uid,
                        "values": vec,
                        "metadata": metadata
                    }]
                )
            else:
                # Legacy SDK doesn't work well with to_thread due to global state,
                # so we'll run it directly but with a warning about blocking
                logger.warning("Legacy Pinecone SDK operations are synchronous and may block the event loop")
                self.index.upsert(
                    vectors=[{
                        "id": uid,
                        "values": vec,
                        "metadata": metadata
                    }]
                )
            
            return True
        except Exception as e:
            logger.error(f"Error upserting vector to Pinecone: {e}")
            return False
    
    async def query(self, 
             vec: List[float], 
             k: int = 5, 
             filter_expr: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query vectors from Pinecone.
        
        Args:
            vec: Query vector
            k: Number of results to return
            filter_expr: Optional filter expression in Pinecone format
            
        Returns:
            dict: Query results with matches
        """
        try:
            # Query the vector - API is slightly different between versions
            if PINECONE_VERSION == "new":
                # Wrap in to_thread to avoid blocking
                results = await asyncio.to_thread(
                    self.index.query,
                    vector=vec,
                    top_k=k,
                    include_metadata=True,
                    filter=filter_expr
                )
            else:
                # Legacy SDK - direct call with warning
                logger.warning("Legacy Pinecone SDK operations are synchronous and may block the event loop")
                results = self.index.query(
                    vector=vec,
                    top_k=k,
                    include_metadata=True,
                    filter=filter_expr
                )
            
            return results
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return {"matches": []}
            
    async def delete(self, uid: str) -> bool:
        """
        Delete a vector from the Pinecone index.
        
        Args:
            uid: Unique ID for the vector to delete
            
        Returns:
            bool: True if successful
        """
        try:
            if PINECONE_VERSION == "new":
                await asyncio.to_thread(self.index.delete, ids=[uid])
            else:
                logger.warning("Legacy Pinecone SDK operations are synchronous and may block the event loop")
                self.index.delete(ids=[uid])
            return True
        except Exception as e:
            logger.error(f"Error deleting vector from Pinecone: {e}")
            return False
            
    async def clear(self) -> bool:
        """
        Delete all vectors from the index with the same namespace.
        
        Returns:
            bool: True if successful
        """
        try:
            if PINECONE_VERSION == "new":
                # New SDK supports deleteAll
                await asyncio.to_thread(self.index.delete, delete_all=True)
            else:
                # Legacy SDK - get all IDs and delete
                logger.warning("Legacy Pinecone SDK operations are synchronous and may block the event loop")
                # This is a simplification - in practice, we'd need to paginate through
                # all vectors in the index, which could be millions
                stats = self.index.describe_index_stats()
                if stats.get("total_vector_count", 0) > 0:
                    # We can't easily get all IDs, so we'll just log a warning
                    logger.warning("Legacy Pinecone SDK doesn't support clearing the entire index easily")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error clearing Pinecone index: {e}")
            return False
            
    async def count(self) -> int:
        """
        Count the number of vectors in the index.
        
        Returns:
            int: Number of vectors
        """
        try:
            if PINECONE_VERSION == "new":
                stats = await asyncio.to_thread(self.index.describe_index_stats)
                return stats.get("total_vector_count", 0)
            else:
                logger.warning("Legacy Pinecone SDK operations are synchronous and may block the event loop")
                stats = self.index.describe_index_stats()
                return stats.get("total_vector_count", 0)
        except Exception as e:
            logger.error(f"Error counting vectors in Pinecone: {e}")
            return 0
