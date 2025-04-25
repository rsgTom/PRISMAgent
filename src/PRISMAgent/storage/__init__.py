"""
PRISMAgent.storage
-----------------

Storage backends for PRISMAgent, providing agent registry and persistence.

This package exports the registry_factory() function, which returns
the appropriate storage backend based on configuration.
"""

import os
from typing import Dict, Type, Optional

from .base import BaseRegistry, RegistryProtocol
from .file_backend import InMemoryRegistry
from .chat_storage import BaseChatStorage, ChatMessage
from .in_memory_chat_storage import InMemoryChatStorage
from ..config import env
from ..util import get_logger
from .vector_backend import VectorStore 

# Get a logger for this module
logger = get_logger(__name__)

# Registry of available storage backend implementations
_REGISTRY_BACKENDS: Dict[str, Type[BaseRegistry]] = {
   "file": InMemoryRegistry,
   "memory": InMemoryRegistry,
   "vector": VectorStore,
   # Add more backends as they are implemented:
   # "redis": RedisRegistry,
   # "supabase": SupabaseRegistry,

}

# Registry of available chat storage implementations
_CHAT_STORAGE_BACKENDS: Dict[str, Type[BaseChatStorage]] = {
   "file": InMemoryChatStorage,
   "memory": InMemoryChatStorage,
   # Add more backends as they are implemented:
   # "redis": RedisChatStorage,
   # "supabase": SupabaseChatStorage,
}

# Default registry instance (singleton)
_REGISTRY: Optional[BaseRegistry] = None

# Default chat storage instance (singleton)
_CHAT_STORAGE: Optional[BaseChatStorage] = None


def registry_factory(registry_type: Optional[str] = None, **kwargs) -> BaseRegistry:
    """
    Factory function to get the configured registry backend.
    
    Returns the global registry instance, which is created based on
    the STORAGE_BACKEND environment variable or the specified registry_type.
    
    Parameters
    ----------
    registry_type : str, optional
        Override the storage backend type from the environment variable
    **kwargs : dict
        Additional configuration parameters for the registry
        
    Returns
    -------
    BaseRegistry
        The registry instance
        
    Raises
    ------
    ValueError
        If the specified registry type is not supported
    """
    global _REGISTRY
    
    if _REGISTRY is not None:
        logger.debug("Returning existing registry instance")
        return _REGISTRY
    
    # Determine which registry type to use
    backend_type = registry_type or env.STORAGE_BACKEND or "memory"
    logger.info(f"Initializing storage backend: {backend_type}")
    
    if backend_type not in _REGISTRY_BACKENDS:
        error_msg = (f"Unsupported registry type: {backend_type}. "
                     f"Valid types are: {', '.join(_REGISTRY_BACKENDS.keys())}")
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Initialize the registry with the specified backend
    registry_class = _REGISTRY_BACKENDS[backend_type]
    
    # Pass any additional configuration to the registry
    if backend_type == "file" and "storage_path" not in kwargs:
        kwargs["storage_path"] = env.STORAGE_PATH
        logger.debug(f"Using storage path: {env.STORAGE_PATH}")
        
    logger.debug(f"Creating registry with backend type: {backend_type}", 
                 backend_type=backend_type, 
                 registry_class=registry_class.__name__)
    
    try:
        _REGISTRY = registry_class(**kwargs)
        logger.info(f"Storage backend initialized successfully: {backend_type}")
    except Exception as e:
        logger.error(f"Failed to initialize storage backend: {backend_type}", 
                     error=str(e), 
                     exc_info=True)
        raise
    
    return _REGISTRY


def chat_storage_factory(storage_type: Optional[str] = None, **kwargs) -> BaseChatStorage:
    """
    Factory function to get the configured chat storage backend.
    
    Returns the global chat storage instance, which is created based on
    the STORAGE_BACKEND environment variable or the specified storage_type.
    
    Parameters
    ----------
    storage_type : str, optional
        Override the storage backend type from the environment variable
    **kwargs : dict
        Additional configuration parameters for the chat storage
        
    Returns
    -------
    BaseChatStorage
        The chat storage instance
        
    Raises
    ------
    ValueError
        If the specified storage type is not supported
    """
    global _CHAT_STORAGE
    
    if _CHAT_STORAGE is not None:
        logger.debug("Returning existing chat storage instance")
        return _CHAT_STORAGE
    
    # Determine which storage type to use
    backend_type = storage_type or env.STORAGE_BACKEND or "memory"
    logger.info(f"Initializing chat storage backend: {backend_type}")
    
    if backend_type not in _CHAT_STORAGE_BACKENDS:
        error_msg = (f"Unsupported chat storage type: {backend_type}. "
                     f"Valid types are: {', '.join(_CHAT_STORAGE_BACKENDS.keys())}")
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Initialize the chat storage with the specified backend
    storage_class = _CHAT_STORAGE_BACKENDS[backend_type]
    
    # Pass any additional configuration to the chat storage
    if backend_type == "file" and "storage_path" not in kwargs:
        kwargs["storage_path"] = env.STORAGE_PATH
        logger.debug(f"Using storage path: {env.STORAGE_PATH}")
        
    logger.debug(f"Creating chat storage with backend type: {backend_type}", 
                 backend_type=backend_type, 
                 storage_class=storage_class.__name__)
    
    try:
        _CHAT_STORAGE = storage_class(**kwargs)
        logger.info(f"Chat storage backend initialized successfully: {backend_type}")
    except Exception as e:
        logger.error(f"Failed to initialize chat storage backend: {backend_type}", 
                     error=str(e), 
                     exc_info=True)
        raise
    
    return _CHAT_STORAGE


__all__ = ["registry_factory", "chat_storage_factory", "BaseRegistry", "RegistryProtocol", 
           "InMemoryRegistry", "VectorStore", "BaseChatStorage", "ChatMessage", "InMemoryChatStorage"]
