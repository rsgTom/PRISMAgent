"""
Vector Storage Backend

This module implements a vector storage backend for PRISMAgent using various
providers like Pinecone, Qdrant, or in-memory for testing.
"""

import os
import time
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple

from ..config import env


# Configure logger
logger = logging.getLogger(__name__)


class VectorBackendProtocol(ABC):
    """Abstract interface for vector storage backend implementations."""

    @abstractmethod
    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store or update a vector in the backend.
        
        Args:
            id: Unique identifier for the vector
            vector: The vector data as a list of floats
            metadata: Optional metadata to store with the vector
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def query(self, vector: List[float], k: int = 10, 
              filter_expr: Optional[Dict] = None) -> Dict:
        """
        Find the k nearest neighbors to the given vector.
        
        Args:
            vector: The query vector
            k: Number of results to return
            filter_expr: Optional filter expression
            
        Returns:
            Dictionary containing matches
        """
        pass
    
    @abstractmethod
    def get(self, id: str) -> Optional[Dict]:
        """
        Retrieve a vector by ID.
        
        Args:
            id: The vector ID
            
        Returns:
            Dictionary containing the vector and metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            id: The vector ID
            
        Returns:
            Boolean indicating success
        """
        pass


class InMemoryVectorBackend(VectorBackendProtocol):
    """In-memory vector backend for development and testing."""
    
    def __init__(self, namespace: str = "default"):
        """
        Initialize an in-memory vector store.
        
        Args:
            namespace: Optional namespace for the vectors
        """
        self.namespace = namespace
        self.vectors: Dict[str, Dict] = {}
        logger.info(f"Initialized in-memory vector backend with namespace '{namespace}'")
    
    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store or update a vector in memory."""
        try:
            self.vectors[id] = {
                "id": id,
                "vector": vector,
                "metadata": metadata or {}
            }
            return True
        except Exception as e:
            logger.error(f"Failed to upsert vector {id}: {e}")
            return False
    
    def query(self, vector: List[float], k: int = 10, 
              filter_expr: Optional[Dict] = None) -> Dict:
        """Find the k nearest neighbors to the given vector using cosine similarity."""
        try:
            results = []
            
            # Calculate cosine similarity for each vector
            for vid, data in self.vectors.items():
                # Skip if it doesn't match filter
                if filter_expr and not self._matches_filter(data.get("metadata", {}), filter_expr):
                    continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(vector, data["vector"])
                
                results.append({
                    "id": vid,
                    "score": similarity,
                    "metadata": data.get("metadata", {})
                })
            
            # Sort by score (highest first) and take top k
            results.sort(key=lambda x: x["score"], reverse=True)
            return {"matches": results[:k]}
            
        except Exception as e:
            logger.error(f"Error during vector query: {e}")
            return {"matches": []}
    
    def get(self, id: str) -> Optional[Dict]:
        """Retrieve a vector by ID."""
        return self.vectors.get(id)
    
    def delete(self, id: str) -> bool:
        """Delete a vector by ID."""
        try:
            if id in self.vectors:
                del self.vectors[id]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete vector {id}: {e}")
            return False
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            v1: First vector
            v2: Second vector
            
        Returns:
            Cosine similarity score (between -1 and 1)
        """
        # Check dimensions
        if len(v1) != len(v2):
            raise ValueError(f"Vector dimensions don't match: {len(v1)} vs {len(v2)}")
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(v1, v2))
        
        # Calculate magnitudes
        mag_v1 = sum(a * a for a in v1) ** 0.5
        mag_v2 = sum(b * b for b in v2) ** 0.5
        
        # Avoid division by zero
        if mag_v1 == 0 or mag_v2 == 0:
            return 0
        
        return dot_product / (mag_v1 * mag_v2)
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_expr: Dict) -> bool:
        """
        Check if metadata matches the filter expression.
        
        Args:
            metadata: Metadata to check
            filter_expr: Filter expression
            
        Returns:
            Boolean indicating if the metadata matches the filter
        """
        for key, value in filter_expr.items():
            # Handle complex filters (dict with operators)
            if isinstance(value, dict):
                # Only supporting basic operators for now
                for op, op_value in value.items():
                    if op == "$gt":
                        if key not in metadata or metadata[key] <= op_value:
                            return False
                    elif op == "$gte":
                        if key not in metadata or metadata[key] < op_value:
                            return False
                    elif op == "$lt":
                        if key not in metadata or metadata[key] >= op_value:
                            return False
                    elif op == "$lte":
                        if key not in metadata or metadata[key] > op_value:
                            return False
                    elif op == "$ne":
                        if key in metadata and metadata[key] == op_value:
                            return False
                    else:
                        logger.warning(f"Unsupported operator: {op}")
                        return False
            # Simple equality filter
            elif key not in metadata or metadata[key] != value:
                return False
        
        return True


class PineconeVectorBackend(VectorBackendProtocol):
    """Pinecone vector backend for production use."""
    
    def __init__(self, namespace: str = "default"):
        """
        Initialize a Pinecone vector store.
        
        Args:
            namespace: Namespace for the vectors
        """
        try:
            import pinecone
            
            # Get API key and environment from env vars
            api_key = env.PINECONE_API_KEY
            if not api_key:
                raise ValueError("PINECONE_API_KEY environment variable not set")
            
            # Initialize Pinecone
            pinecone.init(api_key=api_key)
            
            # Get index name from env vars
            self.index_name = env.PINECONE_INDEX
            if not self.index_name:
                raise ValueError("PINECONE_INDEX environment variable not set")
            
            # Connect to the index
            self.index = pinecone.Index(self.index_name)
            self.namespace = namespace
            
            logger.info(f"Connected to Pinecone index '{self.index_name}' with namespace '{namespace}'")
            
        except ImportError:
            raise ImportError("Pinecone package not installed. Install with 'pip install pinecone-client'")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone backend: {e}")
            raise
    
    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store or update a vector in Pinecone."""
        try:
            # Prepare the vector record
            record = {
                "id": id,
                "values": vector,
                "metadata": metadata or {}
            }
            
            # Upsert the vector
            self.index.upsert(vectors=[record], namespace=self.namespace)
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert vector {id} to Pinecone: {e}")
            return False
    
    def query(self, vector: List[float], k: int = 10, 
              filter_expr: Optional[Dict] = None) -> Dict:
        """Find the k nearest neighbors to the given vector in Pinecone."""
        try:
            # Query the index
            results = self.index.query(
                vector=vector,
                top_k=k,
                namespace=self.namespace,
                filter=filter_expr
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return {"matches": []}
    
    def get(self, id: str) -> Optional[Dict]:
        """Retrieve a vector by ID from Pinecone."""
        try:
            result = self.index.fetch(ids=[id], namespace=self.namespace)
            if id in result.get("vectors", {}):
                vector_data = result["vectors"][id]
                return {
                    "id": id,
                    "vector": vector_data.get("values", []),
                    "metadata": vector_data.get("metadata", {})
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get vector {id} from Pinecone: {e}")
            return None
    
    def delete(self, id: str) -> bool:
        """Delete a vector by ID from Pinecone."""
        try:
            self.index.delete(ids=[id], namespace=self.namespace)
            return True
        except Exception as e:
            logger.error(f"Failed to delete vector {id} from Pinecone: {e}")
            return False


class VectorStore:
    """
    Vector store facade providing unified access to different vector storage backends.
    
    This class selects the appropriate backend based on the VECTOR_PROVIDER
    environment variable.
    """
    
    def __init__(self, namespace: str = "default"):
        """
        Initialize the vector store with the appropriate backend.
        
        Args:
            namespace: Namespace for the vectors
        """
        # Determine which backend to use from environment
        provider = env.VECTOR_PROVIDER or "memory"
        self.backend_name = provider.lower()
        
        if provider.lower() == "pinecone":
            self.backend = PineconeVectorBackend(namespace)
        elif provider.lower() == "memory":
            self.backend = InMemoryVectorBackend(namespace)
        else:
            raise ValueError(f"Unsupported vector provider: {provider}")
        
        logger.info(f"Initialized vector store with {provider} backend")
    
    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store or update a vector.
        
        Args:
            id: Unique identifier for the vector
            vector: The vector data as a list of floats
            metadata: Optional metadata to store with the vector
            
        Returns:
            Boolean indicating success
        """
        return self.backend.upsert(id, vector, metadata)
    
    def query(self, vector: List[float], k: int = 10, 
              filter_expr: Optional[Dict] = None) -> Dict:
        """
        Find the k nearest neighbors to the given vector.
        
        Args:
            vector: The query vector
            k: Number of results to return
            filter_expr: Optional filter expression
            
        Returns:
            Dictionary containing matches
        """
        return self.backend.query(vector, k, filter_expr)
    
    def get(self, id: str) -> Optional[Dict]:
        """
        Retrieve a vector by ID.
        
        Args:
            id: The vector ID
            
        Returns:
            Dictionary containing the vector and metadata if found, None otherwise
        """
        return self.backend.get(id)
    
    def delete(self, id: str) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            id: The vector ID
            
        Returns:
            Boolean indicating success
        """
        return self.backend.delete(id)
