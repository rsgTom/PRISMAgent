"""
Embeddings

Handles generation of vector embeddings from text.
Supports multiple embedding models.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Union

import numpy as np

from ..config import env

# Configure logger
logger = logging.getLogger(__name__)


class EmbeddingModel(ABC):
    """
    Abstract embedding model interface.
    
    Provides a common interface for all embedding model implementations.
    """
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embeddings for a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass


class OpenAIEmbeddingModel(EmbeddingModel):
    """
    OpenAI API-based embedding model.
    
    Requires:
    - OPENAI_API_KEY in environment
    - openai package installed
    """
    
    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        dimensions: int = 1536,
        **kwargs
    ):
        """
        Initialize OpenAI embedding model.
        
        Args:
            model_name: OpenAI embedding model name
            api_key: OpenAI API key (defaults to env)
            dimensions: Embedding dimensions (default: 1536)
            **kwargs: Additional OpenAI client options
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not found. Please install it with: pip install openai"
            )
        
        # Get API key from environment if not provided
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key, **kwargs)
        self.model_name = model_name
        self.dimensions = dimensions
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embeddings for a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        # Ensure text is not empty
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimensions
        
        # Call OpenAI embedding API
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            # Return zero vector on error
            return [0.0] * self.dimensions
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Handle empty input
        if not texts:
            return []
        
        # Replace empty texts with space to avoid API errors
        processed_texts = [text if text and text.strip() else " " for text in texts]
        
        # Call OpenAI embedding API
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=processed_texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            # Return zero vectors on error
            return [[0.0] * self.dimensions for _ in texts]


class LocalEmbeddingModel(EmbeddingModel):
    """
    Local embedding model using sentence-transformers.
    
    Requires:
    - sentence-transformers package installed
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize local embedding model.
        
        Args:
            model_name: Sentence-transformers model name
            device: Device to run model on (cpu, cuda, etc.)
            **kwargs: Additional model options
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "Sentence-transformers package not found. Please install it with: "
                "pip install sentence-transformers"
            )
        
        # Set device from environment or auto-detect
        if device is None:
            device = os.environ.get("EMBEDDING_DEVICE", "auto")
        
        # Initialize model
        self.model = SentenceTransformer(model_name, device=device)
        self.dimensions = self.model.get_sentence_embedding_dimension()
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embeddings for a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        # Ensure text is not empty
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimensions
        
        # Generate embedding
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating local embedding: {e}")
            # Return zero vector on error
            return [0.0] * self.dimensions
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Handle empty input
        if not texts:
            return []
        
        # Replace empty texts with space to avoid errors
        processed_texts = [text if text and text.strip() else " " for text in texts]
        
        # Generate embeddings
        try:
            embeddings = self.model.encode(processed_texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating local embeddings: {e}")
            # Return zero vectors on error
            return [[0.0] * self.dimensions for _ in texts]


class DummyEmbeddingModel(EmbeddingModel):
    """
    Dummy embedding model that returns random vectors.
    
    Useful for testing without external dependencies.
    """
    
    def __init__(self, dimensions: int = 1536, seed: Optional[int] = None):
        """
        Initialize dummy embedding model.
        
        Args:
            dimensions: Embedding dimensions
            seed: Random seed for reproducibility
        """
        self.dimensions = dimensions
        self.random = np.random.RandomState(seed)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate a random embedding for a query.
        
        Args:
            text: Text to embed (ignored)
            
        Returns:
            Random unit vector
        """
        vector = self.random.randn(self.dimensions)
        normalized = vector / np.linalg.norm(vector)
        return normalized.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate random embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed (ignored)
            
        Returns:
            List of random unit vectors
        """
        return [self.embed_query(text) for text in texts]


# Global embedding model instance
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model(provider: Optional[str] = None, **kwargs) -> EmbeddingModel:
    """
    Get an embedding model instance based on provider.
    
    Args:
        provider: Embedding model provider (openai, local, dummy, etc.)
        **kwargs: Additional provider-specific arguments
        
    Returns:
        EmbeddingModel instance
    """
    global _embedding_model
    
    # Return existing instance if already initialized
    if _embedding_model is not None:
        return _embedding_model
    
    # Get provider from environment if not specified
    if provider is None:
        provider = env.get("EMBEDDING_MODEL_PROVIDER", "openai").lower()
    
    # Create appropriate embedding model
    if provider == "openai":
        _embedding_model = OpenAIEmbeddingModel(**kwargs)
    elif provider == "local":
        _embedding_model = LocalEmbeddingModel(**kwargs)
    elif provider == "dummy":
        _embedding_model = DummyEmbeddingModel(**kwargs)
    else:
        logger.warning(f"Unknown embedding model provider: {provider}. Using dummy model.")
        _embedding_model = DummyEmbeddingModel(**kwargs)
    
    return _embedding_model


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector
    """
    model = get_embedding_model()
    return model.embed_query(text)


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    model = get_embedding_model()
    return model.embed_documents(texts) 