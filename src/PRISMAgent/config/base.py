"""
PRISMAgent.config.base
---------------------

Base settings and configuration for the PRISMAgent package.
"""

from typing import Any, Dict, Optional
from . import env


class BaseSettings:
    """Base settings class for PRISMAgent configuration."""
    
    def __init__(
        self,
        api_key: str = None,
        model_name: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs: Any,
    ):
        """
        Initialize base settings.
        
        Parameters
        ----------
        api_key : str, optional
            API key for OpenAI, defaults to env value
        model_name : str, optional
            Model name to use, defaults to env value
        max_tokens : int, optional
            Maximum tokens to generate, defaults to env value
        temperature : float, optional
            Temperature for generation, defaults to env value
        **kwargs : Any
            Additional keyword arguments
        """
        self.api_key = api_key or env.OPENAI_API_KEY
        self.model_name = model_name or env.DEFAULT_MODEL
        self.max_tokens = max_tokens or env.MODEL_MAX_TOKENS
        self.temperature = temperature or env.MODEL_TEMPERATURE
        self._extra_settings = kwargs
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting by key.
        
        Parameters
        ----------
        key : str
            Setting key
        default : Any
            Default value if key not found
            
        Returns
        -------
        Any
            Setting value
        """
        if hasattr(self, key):
            return getattr(self, key)
        return self._extra_settings.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.
        
        Returns
        -------
        Dict[str, Any]
            Settings as dictionary
        """
        result = {
            "api_key": "***",  # Don't include actual API key
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        result.update(self._extra_settings)
        return result 