"""Logger implementation."""

import logging
from typing import Any, Optional

from PRISMAgent.config import env

from .constants import DEFAULT_FORMAT, JSON_FORMAT, LogLevel
from .context import log_context
from .formatters import ContextFilter
from .handlers import create_handler_from_config as create_handler
from .models import LoggingConfig, LogHandlerConfig


class Logger:
    """
    Main logger class that wraps Python's logging system with additional features.
    """
    
    def __init__(
        self, 
        name: str,
        config: Optional[LoggingConfig] = None,
    ):
        """
        Initialize a logger with the given name and configuration.
        
        Parameters
        ----------
        name : str
            Logger name, typically the module name
        config : LoggingConfig, optional
            Logging configuration
        """
        self.name = name
        self.config = config or Logger.get_default_config()
        self.logger = logging.getLogger(name)
        
        # Set level based on config
        level = getattr(logging, self.config.level, logging.INFO)
        self.logger.setLevel(level)
        
        # Add a context filter to every handler
        context_filter = ContextFilter()
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Configure handlers based on config
        for handler_config in self.config.handlers:
            # Handle type mismatch between LogHandlerConfig classes
            handler = create_handler(handler_config)  # type: ignore
            if handler:
                handler.addFilter(context_filter)
                self.logger.addHandler(handler)
        
        # Set propagate based on config
        self.logger.propagate = self.config.propagate
    
    @staticmethod
    def get_default_config() -> LoggingConfig:
        """
        Get the default logging configuration from environment variables.
        
        Returns
        -------
        LoggingConfig
            Default logging configuration
        """
        log_level = env.get_env("LOG_LEVEL", LogLevel.INFO).upper()
        log_format = env.get_env("LOG_FORMAT", DEFAULT_FORMAT)
        log_file = env.get_env("LOG_FILE")
        log_json = env.get_env_bool("LOG_JSON", False)
        
        handlers = [
            LogHandlerConfig(
                type="console", 
                level=log_level, 
                format=log_format,
                filename=None,
                max_bytes=None,
                backup_count=None,
                url=None,
                token=None
            )
        ]
        
        if log_json:
            handlers[0].format = JSON_FORMAT
        
        if log_file:
            file_handler = LogHandlerConfig(
                type="file",
                level=log_level,
                format=log_format,
                filename=log_file,
                max_bytes=10 * 1024 * 1024,
                backup_count=5,
                url=None,
                token=None
            )
            if log_json:
                file_handler.format = JSON_FORMAT
            handlers.append(file_handler)
        
        return LoggingConfig(
            level=log_level,
            handlers=handlers,
            capture_warnings=True,
            propagate=True,
            include_context=True,
            log_file_path=env.get_env("LOG_PATH", "./logs"),
        )
    
    def debug(self, msg: str, **kwargs: Any) -> None:
        """
        Log a debug message.
        
        Parameters
        ----------
        msg : str
            Message to log
        **kwargs : Any
            Additional context to include in the log
        """
        with log_context(**kwargs):
            self.logger.debug(msg)
    
    def info(self, msg: str, **kwargs: Any) -> None:
        """
        Log an info message.
        
        Parameters
        ----------
        msg : str
            Message to log
        **kwargs : Any
            Additional context to include in the log
        """
        with log_context(**kwargs):
            self.logger.info(msg)
    
    def warning(self, msg: str, **kwargs: Any) -> None:
        """
        Log a warning message.
        
        Parameters
        ----------
        msg : str
            Message to log
        **kwargs : Any
            Additional context to include in the log
        """
        with log_context(**kwargs):
            self.logger.warning(msg)
    
    def error(self, msg: str, exc_info: bool = False, **kwargs: Any) -> None:
        """
        Log an error message.
        
        Parameters
        ----------
        msg : str
            Message to log
        exc_info : bool, optional
            Whether to include exception information in the log
        **kwargs : Any
            Additional context to include in the log
        """
        with log_context(**kwargs):
            self.logger.error(msg, exc_info=exc_info)
    
    def critical(self, msg: str, exc_info: bool = True, **kwargs: Any) -> None:
        """
        Log a critical message.
        
        Parameters
        ----------
        msg : str
            Message to log
        exc_info : bool, optional
            Whether to include exception information in the log
        **kwargs : Any
            Additional context to include in the log
        """
        with log_context(**kwargs):
            self.logger.critical(msg, exc_info=exc_info)
    
    def exception(self, msg: str, **kwargs: Any) -> None:
        """
        Log an exception message (includes exception info).
        
        Parameters
        ----------
        msg : str
            Message to log
        **kwargs : Any
            Additional context to include in the log
        """
        with log_context(**kwargs):
            self.logger.exception(msg)
    
    def log(self, level: str, msg: str, **kwargs: Any) -> None:
        """
        Log a message with the specified level.
        
        Parameters
        ----------
        level : str
            Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        msg : str
            Message to log
        **kwargs : Any
            Additional context to include in the log
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        with log_context(**kwargs):
            self.logger.log(numeric_level, msg)


# Configure the root logger
def configure_root_logger(config: Optional[LoggingConfig] = None) -> None:
    """
    Configure the root logger with the given configuration.
    
    Parameters
    ----------
    config : LoggingConfig, optional
        Logging configuration
    """
    config = config or Logger.get_default_config()
    
    # Reset root logger
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    # Set level
    level = getattr(logging, config.level, logging.INFO)
    root_logger.setLevel(level)
    
    # Add handlers
    for handler_config in config.handlers:
        # Handle type mismatch between LogHandlerConfig classes
        handler = create_handler(handler_config)  # type: ignore
        if handler:
            handler.addFilter(ContextFilter())
            root_logger.addHandler(handler)
    
    # Capture warnings
    logging.captureWarnings(config.capture_warnings)


# Global function to get a logger
def get_logger(name: str, config: Optional[LoggingConfig] = None) -> Logger:
    """
    Get a logger with the given name and configuration.
    
    Parameters
    ----------
    name : str
        Logger name, typically the module name
    config : LoggingConfig, optional
        Logging configuration
    
    Returns
    -------
    Logger
        Configured logger
    """
    return Logger(name, config) 