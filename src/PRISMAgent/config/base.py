"""
PRISMAgent.config.base
---------------------

Base settings and configuration for the PRISMAgent package.
"""

from typing import Any, Dict, Optional


class BaseSettings:
    """Base settings class for PRISMAgent configuration."""
    
    def __init__(
        self,
        api_key: str = "mock-api-key",
        model_name: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        """
        Initialize base settings.
        
        Parameters
        ----------
        api_key : str
            API key for OpenAI
        model_name : str
            Model name to use
        max_tokens : int
            Maximum tokens to generate
        temperature : float
            Temperature for generation
        **kwargs : Any
            Additional keyword arguments
        """
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
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