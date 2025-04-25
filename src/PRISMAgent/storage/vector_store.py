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
from agents import Agent

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
            from .vector_backend import PineconeVectorBackend
            self.backend = PineconeVectorBackend(namespace)
        elif provider.lower() == "memory":
            from .vector_backend import InMemoryVectorBackend
            self.backend = InMemoryVectorBackend(namespace)
        else:
            raise ValueError(f"Unsupported vector provider: {provider}")
        
        # Initialize agent storage
        self._agents = {}
        
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
    
    def exists(self, name: str) -> bool:
        """
        Check if an agent with the given name exists.
        
        Args:
            name: Agent name to check
            
        Returns:
            True if the agent exists, False otherwise
        """
        return name in self._agents
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name. Returns None if not found.
        
        This is a safer alternative to get() that doesn't raise KeyError.
        
        Args:
            name: Agent name to retrieve
            
        Returns:
            Agent object if found, None otherwise
        """
        return self._agents.get(name)
    
    def register(self, agent: Agent) -> None:
        """
        Register an agent in the registry.
        
        Args:
            agent: Agent object to register
        """
        self._agents[agent.name] = agent
    
    def list_agents(self) -> List[str]:
        """
        List all agent names in the registry.
        
        Returns:
            List of agent names
        """
        return list(self._agents.keys())
