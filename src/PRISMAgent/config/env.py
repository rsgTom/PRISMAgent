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
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

# General configuration
DEBUG = os.getenv('DEBUG', 'false').lower() in ('true', '1', 't')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENV = os.getenv('ENV', 'development')

# API configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
API_PREFIX = os.getenv('API_PREFIX', '/api/v1')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///prism_agent.db')

# Vector storage configuration
VECTOR_PROVIDER = os.getenv('VECTOR_PROVIDER', 'memory')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'prism-agent')
EMBED_DIM = int(os.getenv('EMBED_DIM', '1536'))

# LLM configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gpt-4o')

# Auth configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

# Supabase configuration (optional)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

# Storage paths
STORAGE_PATH = os.getenv('STORAGE_PATH', './data')
TEMP_PATH = os.getenv('TEMP_PATH', './tmp')

def is_production() -> bool:
    """Check if environment is production."""
    return ENV.lower() == 'production'

def is_development() -> bool:
    """Check if environment is development."""
    return ENV.lower() == 'development'

def is_testing() -> bool:
    """Check if environment is testing."""
    return ENV.lower() == 'testing'

def get_optional_setting(key: str) -> Optional[str]:
    """Get an optional setting, returning None if not set."""
    return os.getenv(key)

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
MODEL_TEMPERATURE = get_env_float("MODEL_TEMPERATURE", 0.7)
MODEL_MAX_TOKENS = get_env_int("MODEL_MAX_TOKENS", 1000)
STORAGE_BACKEND = get_env("STORAGE_BACKEND", "memory")
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
    "is_production",
    "is_development",
    "is_testing",
    "get_optional_setting",
] 