"""
PRISMAgent.storage
--------------

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
from ..util.exceptions import (
    StorageError, 
    DatabaseConnectionError, 
    ChatStorageError,
    ConfigurationError,
    InvalidConfigurationError
)
from ..util.error_handling import handle_exceptions, error_context, validate_or_raise
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


@handle_exceptions(
    error_map={
        ValueError: InvalidConfigurationError,
        FileNotFoundError: StorageError,
        ConnectionError: DatabaseConnectionError,
        OSError: StorageError,
    },
    default_error_class=StorageError
)
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
    InvalidConfigurationError
        If the specified registry type is not supported
    StorageError
        If there's an issue initializing the storage backend
    DatabaseConnectionError
        If there's a connection issue with the database
    """
    global _REGISTRY
    
    if _REGISTRY is not None:
        logger.debug("Returning existing registry instance")
        return _REGISTRY
    
    # Determine which registry type to use
    backend_type = registry_type or env.STORAGE_BACKEND or "memory"
    logger.info(f"Initializing storage backend: {backend_type}")
    
    # Validate backend type
    validate_or_raise(
        backend_type in _REGISTRY_BACKENDS,
        f"Unsupported registry type: {backend_type}. Valid types are: {', '.join(_REGISTRY_BACKENDS.keys())}",
        "registry_type",
        InvalidConfigurationError,
        details={"available_backends": list(_REGISTRY_BACKENDS.keys())}
    )
    
    # Initialize the registry with the specified backend
    registry_class = _REGISTRY_BACKENDS[backend_type]
    
    # Pass any additional configuration to the registry
    if backend_type == "file" and "storage_path" not in kwargs:
        storage_path = env.STORAGE_PATH
        
        # Validate storage path
        if not storage_path:
            raise InvalidConfigurationError(
                "storage_path",
                "string path",
                "empty or missing",
                details={"recommendation": "Set STORAGE_PATH environment variable or provide storage_path parameter"}
            )
            
        kwargs["storage_path"] = storage_path
        logger.debug(f"Using storage path: {env.STORAGE_PATH}")
        
    logger.debug(f"Creating registry with backend type: {backend_type}", 
                 backend_type=backend_type, 
                 registry_class=registry_class.__name__)
    
    with error_context(
        f"Initializing {backend_type} registry",
        error_map={
            ConnectionError: DatabaseConnectionError,
            FileNotFoundError: StorageError,
        },
        context_details={"backend_type": backend_type, "registry_class": registry_class.__name__}
    ):
        _REGISTRY = registry_class(**kwargs)
        logger.info(f"Storage backend initialized successfully: {backend_type}")
    
    return _REGISTRY


@handle_exceptions(
    error_map={
        ValueError: InvalidConfigurationError,
        FileNotFoundError: StorageError,
        ConnectionError: DatabaseConnectionError,
        OSError: StorageError,
    },
    default_error_class=ChatStorageError
)
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
    InvalidConfigurationError
        If the specified storage type is not supported
    ChatStorageError
        If there's an issue initializing the chat storage backend
    DatabaseConnectionError
        If there's a connection issue with the database
    """
    global _CHAT_STORAGE
    
    if _CHAT_STORAGE is not None:
        logger.debug("Returning existing chat storage instance")
        return _CHAT_STORAGE
    
    # Determine which storage type to use
    backend_type = storage_type or env.STORAGE_BACKEND or "memory"
    logger.info(f"Initializing chat storage backend: {backend_type}")
    
    # Validate backend type
    validate_or_raise(
        backend_type in _CHAT_STORAGE_BACKENDS,
        f"Unsupported chat storage type: {backend_type}. Valid types are: {', '.join(_CHAT_STORAGE_BACKENDS.keys())}",
        "storage_type",
        InvalidConfigurationError,
        details={"available_backends": list(_CHAT_STORAGE_BACKENDS.keys())}
    )
    
    # Initialize the chat storage with the specified backend
    storage_class = _CHAT_STORAGE_BACKENDS[backend_type]
    
    # Pass any additional configuration to the chat storage
    if backend_type == "file" and "storage_path" not in kwargs:
        storage_path = env.STORAGE_PATH
        
        # Validate storage path
        if not storage_path:
            raise InvalidConfigurationError(
                "storage_path",
                "string path",
                "empty or missing",
                details={"recommendation": "Set STORAGE_PATH environment variable or provide storage_path parameter"}
            )
            
        kwargs["storage_path"] = storage_path
        logger.debug(f"Using storage path: {env.STORAGE_PATH}")
        
    logger.debug(f"Creating chat storage with backend type: {backend_type}", 
                 backend_type=backend_type, 
                 storage_class=storage_class.__name__)
    
    with error_context(
        f"Initializing {backend_type} chat storage",
        error_map={
            ConnectionError: DatabaseConnectionError,
            FileNotFoundError: ChatStorageError,
        },
        context_details={"backend_type": backend_type, "storage_class": storage_class.__name__}
    ):
        _CHAT_STORAGE = storage_class(**kwargs)
        logger.info(f"Chat storage backend initialized successfully: {backend_type}")
    
    return _CHAT_STORAGE


__all__ = ["registry_factory", "chat_storage_factory", "BaseRegistry", "RegistryProtocol", 
           "InMemoryRegistry", "VectorStore", "BaseChatStorage", "ChatMessage", "InMemoryChatStorage"]
