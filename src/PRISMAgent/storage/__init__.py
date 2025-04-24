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
from ..config import env
from .vector_backend import VectorStore 

# Registry of available storage backend implementations
_REGISTRY_BACKENDS: Dict[str, Type[BaseRegistry]] = {
   "file": InMemoryRegistry,
    "memory": InMemoryRegistry,
    "vector": VectorStore,
    # Add more backends as they are implemented:
    # "redis": RedisRegistry,
    # "supabase": SupabaseRegistry,

}

# Default registry instance (singleton)
_REGISTRY: Optional[BaseRegistry] = None


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
        return _REGISTRY
    
    # Determine which registry type to use
    backend_type = registry_type or env.STORAGE_BACKEND or "memory"
    
    if backend_type not in _REGISTRY_BACKENDS:
        raise ValueError(f"Unsupported registry type: {backend_type}. " 
                         f"Valid types are: {', '.join(_REGISTRY_BACKENDS.keys())}")
    
    # Initialize the registry with the specified backend
    registry_class = _REGISTRY_BACKENDS[backend_type]
    
    # Pass any additional configuration to the registry
    if backend_type == "file" and "storage_path" not in kwargs:
        kwargs["storage_path"] = env.STORAGE_PATH
        
    _REGISTRY = registry_class(**kwargs)
    return _REGISTRY


__all__ = ["registry_factory", "BaseRegistry", "RegistryProtocol", "InMemoryRegistry"] 