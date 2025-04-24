"""
Embedding Module

Utilities for generating text embeddings using various embedding models.
"""

import logging
import os
from typing import List, Optional, Union

import numpy as np

from ..config import env

# Configure logger
logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Base class for embedding models."""
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate an embedding for a query text.
        
        Args:
            text: The text to embed
            
        Returns:
            A list of floats representing the embedding
        """
        raise NotImplementedError("Subclasses must implement embed_query")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: The texts to embed
            
        Returns:
            A list of embeddings
        """
        raise NotImplementedError("Subclasses must implement embed_documents")


class OpenAIEmbeddingModel(EmbeddingModel):
    """OpenAI embedding model."""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize the OpenAI embedding model.
        
        Args:
            model_name: The name of the OpenAI model to use
        """
        self.model_name = model_name
        self._client = None
        self._initialized = False
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            # Import OpenAI
            from openai import OpenAI
            
            # Get API key
            api_key = env.OPENAI_API_KEY
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set")
                return
            
            # Initialize client
            self._client = OpenAI(api_key=api_key)
            self._initialized = True
            logger.info(f"Initialized OpenAI embedding model: {self.model_name}")
            
        except ImportError:
            logger.error("OpenAI package not installed. Install with 'pip install openai'")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for a query text."""
        if not self._initialized:
            self._initialize()
            if not self._initialized:
                logger.error("Failed to initialize OpenAI")
                return self._default_embedding()
        
        try:
            response = self._client.embeddings.create(
                model=self.model_name,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            return self._default_embedding()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        if not self._initialized:
            self._initialize()
            if not self._initialized:
                logger.error("Failed to initialize OpenAI")
                return [self._default_embedding() for _ in texts]
        
        try:
            response = self._client.embeddings.create(
                model=self.model_name,
                input=texts,
                encoding_format="float"
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            return [self._default_embedding() for _ in texts]
    
    def _default_embedding(self) -> List[float]:
        """Return a default zero embedding."""
        return [0.0] * env.EMBED_DIM


class SentenceTransformerModel(EmbeddingModel):
    """Sentence Transformer embedding model."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the Sentence Transformer model.
        
        Args:
            model_name: The name of the model to use
        """
        self.model_name = model_name
        self._model = None
        self._initialized = False
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the Sentence Transformer model."""
        try:
            # Import Sentence Transformers
            from sentence_transformers import SentenceTransformer
            
            # Initialize model
            self._model = SentenceTransformer(self.model_name)
            self._initialized = True
            logger.info(f"Initialized Sentence Transformer model: {self.model_name}")
            
        except ImportError:
            logger.error("Sentence Transformers package not installed. "
                        "Install with 'pip install sentence-transformers'")
        except Exception as e:
            logger.error(f"Failed to initialize Sentence Transformer: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for a query text."""
        if not self._initialized:
            self._initialize()
            if not self._initialized:
                logger.error("Failed to initialize Sentence Transformer")
                return self._default_embedding()
        
        try:
            embedding = self._model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating Sentence Transformer embedding: {e}")
            return self._default_embedding()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        if not self._initialized:
            self._initialize()
            if not self._initialized:
                logger.error("Failed to initialize Sentence Transformer")
                return [self._default_embedding() for _ in texts]
        
        try:
            embeddings = self._model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating Sentence Transformer embeddings: {e}")
            return [self._default_embedding() for _ in texts]
    
    def _default_embedding(self) -> List[float]:
        """Return a default zero embedding."""
        return [0.0] * env.EMBED_DIM


class RandomEmbeddingModel(EmbeddingModel):
    """Random embedding model for testing and development."""
    
    def __init__(self, dimension: int = 1536):
        """
        Initialize the random embedding model.
        
        Args:
            dimension: The dimension of the embeddings
        """
        self.dimension = dimension
    
    def embed_query(self, text: str) -> List[float]:
        """Generate a random embedding for a query text."""
        embedding = np.random.normal(0, 0.1, self.dimension)
        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate random embeddings for a list of documents."""
        return [self.embed_query(text) for text in texts]


# Global embedding model instance
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    """
    Get the configured embedding model.
    
    Returns:
        An embedding model instance
    """
    global _embedding_model
    
    if _embedding_model is None:
        # Get model type from environment
        model_type = env.EMBEDDING_MODEL_TYPE.lower()
        
        if model_type == "openai":
            model_name = env.OPENAI_EMBEDDING_MODEL
            _embedding_model = OpenAIEmbeddingModel(model_name=model_name)
        elif model_type == "sentence_transformer":
            model_name = env.SENTENCE_TRANSFORMER_MODEL
            _embedding_model = SentenceTransformerModel(model_name=model_name)
        elif model_type == "random":
            _embedding_model = RandomEmbeddingModel(dimension=env.EMBED_DIM)
        else:
            logger.warning(f"Unknown embedding model type: {model_type}, using random embeddings")
            _embedding_model = RandomEmbeddingModel(dimension=env.EMBED_DIM)
    
    return _embedding_model


def get_embedding(text: str) -> List[float]:
    """
    Generate an embedding for a text.
    
    Args:
        text: The text to embed
        
    Returns:
        A list of floats representing the embedding
    """
    model = get_embedding_model()
    return model.embed_query(text)


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.
    
    Args:
        texts: The texts to embed
        
    Returns:
        A list of embeddings
    """
    model = get_embedding_model()
    return model.embed_documents(texts) 