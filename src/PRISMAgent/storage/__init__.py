"""
PRISMAgent.storage
-----------------

Storage backends for PRISMAgent, providing agent registry and persistence.

This package exports the registry_factory() function, which returns
the appropriate storage backend based on configuration.
"""

import os
from typing import Dict, Type

from .base import BaseRegistry, RegistryProtocol
from .file_backend import InMemoryRegistry

# Registry of available storage backend implementations
_REGISTRY_BACKENDS: Dict[str, Type[BaseRegistry]] = {
    "memory": InMemoryRegistry,
    # Add more backends as they are implemented:
    # "redis": RedisRegistry,
    # "supabase": SupabaseRegistry,
    # "vector": VectorRegistry,
}

# Default registry instance (singleton)
_REGISTRY: BaseRegistry = InMemoryRegistry()


def registry_factory() -> BaseRegistry:
    """
    Factory function to get the configured registry backend.
    
    Returns the global registry instance, which is created based on
    the STORAGE_BACKEND environment variable.
    
    Returns
    -------
    BaseRegistry
        The registry instance
    """
    # In future versions, this will initialize different backends
    # based on the environment configuration.
    return _REGISTRY


__all__ = ["registry_factory", "BaseRegistry", "RegistryProtocol", "InMemoryRegistry"] 