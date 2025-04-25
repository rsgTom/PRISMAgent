"""
In-Memory Vector Storage Backend

This module provides a simple in-memory implementation of the vector storage interface
for development and testing purposes.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class InMemoryStore:
    """
    A simple in-memory vector store for development and testing.
    
    This class implements the same interface as the other vector store backends
    but stores all data in memory. This is useful for development and testing
    but should not be used in production as all data is lost when the process
    terminates.
    """
    
    def __init__(self):
        """
        Initialize an empty in-memory vector store.
        """
        self.vectors = {}  # Maps ID to vector
        self.metadata = {}  # Maps ID to metadata
        logger.info("Initialized in-memory vector store (for development/testing only)")
    
    async def upsert(self, uid: str, vec: List[float], meta: Dict[str, Any]) -> bool:
        """
        Store a vector with its metadata.
        
        Args:
            uid: Unique identifier for this vector
            vec: The embedding vector
            meta: Metadata to store with the vector
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert to numpy array for efficient operations
            vector_array = np.array(vec, dtype=np.float32)
            
            # Store vector and metadata
            self.vectors[uid] = vector_array
            self.metadata[uid] = meta
            
            return True
        except Exception as e:
            logger.error(f"Error upserting vector {uid}: {e}")
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
            filter_expr: Optional filter expression (not supported in memory backend)
            
        Returns:
            Dictionary with a "matches" list containing the most similar vectors
        """
        try:
            # If filter_expr is provided, log a warning
            if filter_expr:
                logger.warning("Filter expressions are not supported in the in-memory backend")
            
            # No vectors stored yet
            if not self.vectors:
                return {"matches": []}
            
            # Convert query vector to numpy array
            query_vec = np.array(vec, dtype=np.float32)
            
            # Calculate cosine similarity for all vectors
            results = []
            
            for uid, vector in self.vectors.items():
                # Ensure vectors are not zero (would cause division by zero)
                query_norm = np.linalg.norm(query_vec)
                vector_norm = np.linalg.norm(vector)
                
                if query_norm == 0 or vector_norm == 0:
                    similarity = 0.0
                else:
                    # Calculate cosine similarity
                    similarity = np.dot(query_vec, vector) / (query_norm * vector_norm)
                
                results.append({
                    "id": uid,
                    "score": float(similarity),
                    "metadata": self.metadata.get(uid, {})
                })
            
            # Sort by similarity score (highest first)
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # Return top k results
            return {"matches": results[:k]}
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return {"matches": []}
    
    async def delete(self, uid: str) -> bool:
        """
        Delete a vector and its metadata.
        
        Args:
            uid: Unique identifier for the vector to delete
            
        Returns:
            bool: True if successful, False if the vector doesn't exist
        """
        if uid in self.vectors:
            del self.vectors[uid]
            del self.metadata[uid]
            return True
        return False
    
    async def clear(self) -> None:
        """
        Delete all vectors and metadata from the store.
        """
        self.vectors.clear()
        self.metadata.clear()
    
    async def count(self) -> int:
        """
        Return the number of vectors in the store.
        
        Returns:
            int: Number of vectors
        """
        return len(self.vectors)
