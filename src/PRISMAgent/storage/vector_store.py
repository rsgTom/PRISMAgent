"""
Vector Store

Provides interfaces for vector storage backends.
Supports storing and retrieving document embeddings.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from ..config import env

# Configure logger
logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Base class for vector stores."""
    
    @abstractmethod
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: List of metadata dictionaries
            ids: List of IDs for the texts
            **kwargs: Additional parameters for the vector store
            
        Returns:
            List of IDs of the added texts
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar texts.
        
        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter
            **kwargs: Additional parameters for the vector store
            
        Returns:
            List of (text, metadata, score) tuples
        """
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """
        Delete texts from the vector store.
        
        Args:
            ids: IDs of texts to delete
        """
        pass


class InMemoryVectorStore(VectorStore):
    """Simple in-memory vector store for testing and development."""
    
    def __init__(
        self,
        embedding_function: Optional[callable] = None,
        **kwargs
    ):
        """
        Initialize in-memory vector store.
        
        Args:
            embedding_function: Function to convert text to embeddings
            **kwargs: Additional parameters
        """
        self.embedding_function = embedding_function or self._default_embedding
        self.texts = []
        self.embeddings = []
        self.metadatas = []
        self.ids = []
    
    def _default_embedding(self, text: str) -> List[float]:
        """
        Generate a simple hash-based embedding for text.
        This is only for testing and should not be used in production.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Create a simple embedding by hashing characters
        vector = np.zeros(100)
        for i, char in enumerate(text):
            vector[i % 100] += ord(char)
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.tolist()
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: List of metadata dictionaries
            ids: List of IDs for the texts
            **kwargs: Additional parameters
            
        Returns:
            List of IDs of the added texts
        """
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        if ids is None:
            ids = [str(i + len(self.ids)) for i in range(len(texts))]
        
        # Convert texts to embeddings
        new_embeddings = [self.embedding_function(text) for text in texts]
        
        # Store in memory
        self.texts.extend(texts)
        self.embeddings.extend(new_embeddings)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
        
        return ids
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar texts.
        
        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter
            **kwargs: Additional parameters
            
        Returns:
            List of (text, metadata, score) tuples
        """
        if not self.texts:
            return []
        
        # Get query embedding
        query_embedding = self.embedding_function(query)
        
        # Convert to numpy for easier calculations
        query_embedding_np = np.array(query_embedding)
        embeddings_np = np.array(self.embeddings)
        
        # Calculate cosine similarity
        similarities = np.dot(embeddings_np, query_embedding_np)
        
        # Apply filter if provided
        filtered_indices = range(len(self.texts))
        if filter:
            filtered_indices = [
                i for i in filtered_indices
                if self._matches_filter(self.metadatas[i], filter)
            ]
        
        # Get top k results
        results = [
            (self.texts[i], self.metadatas[i], float(similarities[i]))
            for i in filtered_indices
        ]
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results[:k]
    
    def _matches_filter(self, metadata: Dict[str, Any], filter: Dict[str, Any]) -> bool:
        """
        Check if metadata matches filter.
        
        Args:
            metadata: Metadata to check
            filter: Filter to apply
            
        Returns:
            True if metadata matches filter
        """
        for key, value in filter.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True
    
    def delete(self, ids: List[str]) -> None:
        """
        Delete texts from the vector store.
        
        Args:
            ids: IDs of texts to delete
        """
        if not ids:
            return
        
        # Find indices to keep
        indices_to_keep = [i for i, id_val in enumerate(self.ids) if id_val not in ids]
        
        # Filter lists
        self.texts = [self.texts[i] for i in indices_to_keep]
        self.embeddings = [self.embeddings[i] for i in indices_to_keep]
        self.metadatas = [self.metadatas[i] for i in indices_to_keep]
        self.ids = [self.ids[i] for i in indices_to_keep]


# Add more vector store implementations as needed:
# - PineconeVectorStore
# - QdrantVectorStore
# - ChromaVectorStore
# etc.


def get_vector_store(
    provider: Optional[str] = None,
    **kwargs
) -> VectorStore:
    """
    Get a vector store instance.
    
    Args:
        provider: Vector store provider (default from env or "memory")
        **kwargs: Additional parameters for the vector store
        
    Returns:
        VectorStore instance
        
    Raises:
        ValueError: If provider is not supported
    """
    # Default provider
    if provider is None:
        provider = env.get("VECTOR_STORE_PROVIDER", "memory")
    
    # Create vector store based on provider
    if provider.lower() == "memory":
        return InMemoryVectorStore(**kwargs)
    # Add more providers here
    else:
        raise ValueError(f"Unsupported vector store provider: {provider}") 