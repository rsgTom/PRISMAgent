"""
PRISMAgent.config.env
---------------------

Environment variable configuration and loading.

This module handles loading environment variables from .env files
and provides a consistent interface for accessing them throughout
the application.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Try to import dotenv, but don't fail if it's not installed
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)

# Load environment variables from .env file if available
if DOTENV_AVAILABLE:
    env_path = Path('.') / '.env'
    load_result = load_dotenv(dotenv_path=env_path)
    if load_result:
        logger.info("Loaded environment variables from .env file")
    else:
        logger.info("No .env file found or unable to load it")
else:
    logger.info("python-dotenv not installed. Skipping .env file loading.")


def get_env(key: str, default: Any = None) -> Any:
    """
    Get an environment variable.
    
    Parameters
    ----------
    key : str
        Environment variable name
    default : Any, optional
        Default value if environment variable is not set
        
    Returns
    -------
    Any
        Environment variable value or default
    """
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.
    
    Parameters
    ----------
    key : str
        Environment variable name
    default : bool, optional
        Default value if environment variable is not set
        
    Returns
    -------
    bool
        Environment variable value as boolean
    """
    value = get_env(key, None)
    if value is None:
        return default
    return value.lower() in ('true', 'yes', '1', 't', 'y')


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get an integer environment variable.
    
    Parameters
    ----------
    key : str
        Environment variable name
    default : int, optional
        Default value if environment variable is not set
        
    Returns
    -------
    int
        Environment variable value as integer
    """
    value = get_env(key, None)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Environment variable {key} is not a valid integer. Using default: {default}")
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """
    Get a float environment variable.
    
    Parameters
    ----------
    key : str
        Environment variable name
    default : float, optional
        Default value if environment variable is not set
        
    Returns
    -------
    float
        Environment variable value as float
    """
    value = get_env(key, None)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        logger.warning(f"Environment variable {key} is not a valid float. Using default: {default}")
        return default


def get_all_env_vars() -> Dict[str, str]:
    """
    Get all environment variables.
    
    Returns
    -------
    Dict[str, str]
        Dictionary of all environment variables
    """
    return dict(os.environ)


# Module-level constants for commonly used environment variables
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
DEFAULT_MODEL = get_env("DEFAULT_MODEL", "o3-mini")
MODEL_TEMPERATURE = get_env_float("MODEL_TEMPERATURE", 0.7)
MODEL_MAX_TOKENS = get_env_int("MODEL_MAX_TOKENS", 1000)
STORAGE_BACKEND = get_env("STORAGE_BACKEND", "memory")
STORAGE_PATH = get_env("STORAGE_PATH", "./data")
LOG_LEVEL = get_env("LOG_LEVEL", "INFO")

__all__ = [
    "get_env", 
    "get_env_bool", 
    "get_env_int", 
    "get_env_float", 
    "get_all_env_vars",
    "OPENAI_API_KEY",
    "DEFAULT_MODEL",
    "MODEL_TEMPERATURE",
    "MODEL_MAX_TOKENS",
    "STORAGE_BACKEND",
    "STORAGE_PATH",
    "LOG_LEVEL",
] 