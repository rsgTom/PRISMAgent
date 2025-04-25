"""
PRISMAgent.util.logging
----------------------

A standardized logging system for the PRISMAgent package.

This module provides a consistent interface for logging throughout the application,
with support for different log levels, formats, and outputs.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import inspect
import threading
from contextlib import contextmanager
import uuid
from functools import wraps

from pydantic import BaseModel, Field

from PRISMAgent.config import env


# Define log levels
class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Log format constants
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
JSON_FORMAT = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": %(message)s}'
DETAILED_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - "
    "%(threadName)s - %(message)s"
)


# Pydantic models for logging configuration
class LogHandlerConfig(BaseModel):
    """Configuration for a log handler."""
    
    type: str = Field(..., description="Handler type: console, file, or external")
    level: str = Field(LogLevel.INFO, description="Minimum log level for this handler")
    format: str = Field(DEFAULT_FORMAT, description="Log format string")
    
    # File handler specific fields
    filename: Optional[str] = Field(None, description="Path to log file (for file handler)")
    max_bytes: Optional[int] = Field(10 * 1024 * 1024, description="Maximum size for log file before rotation")
    backup_count: Optional[int] = Field(5, description="Number of backup files to keep")
    
    # External handler specific fields
    url: Optional[str] = Field(None, description="URL for external log service")
    token: Optional[str] = Field(None, description="Auth token for external log service")


class LoggingConfig(BaseModel):
    """Configuration for the logging system."""
    
    level: str = Field(LogLevel.INFO, description="Global minimum log level")
    handlers: List[LogHandlerConfig] = Field(
        default_factory=lambda: [LogHandlerConfig(type="console")]
    )
    capture_warnings: bool = Field(True, description="Capture Python warnings in logs")
    propagate: bool = Field(True, description="Propagate logs to parent loggers")
    include_context: bool = Field(True, description="Include context data in logs")
    log_file_path: Optional[str] = Field(None, description="Default path for log files")


# Thread-local storage for context information
_thread_local = threading.local()


def _get_context() -> Dict[str, Any]:
    """Get the current context data from thread-local storage."""
    if not hasattr(_thread_local, "context"):
        _thread_local.context = {}
    return _thread_local.context


def _generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


class ContextFilter(logging.Filter):
    """Filter that adds context information to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to the log record."""
        context = _get_context()
        for key, value in context.items():
            setattr(record, key, value)
        
        # Add request_id if not present
        if not hasattr(record, "request_id") and context.get("request_id"):
            record.request_id = context.get("request_id")
        
        # Add caller information
        if not hasattr(record, "caller"):
            frame = inspect.currentframe()
            # Go back 2 frames to get the caller of the logging function
            if frame:
                try:
                    frame = frame.f_back
                    if frame:
                        frame = frame.f_back
                        if frame:
                            caller = f"{frame.f_globals['__name__']}:{frame.f_lineno}"
                            record.caller = caller
                except (AttributeError, KeyError):
                    record.caller = "unknown"
            else:
                record.caller = "unknown"
        
        return True


class JsonFormatter(logging.Formatter):
    """Formatter that outputs log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add context data if present
        context = _get_context()
        if context:
            log_data["context"] = context.copy()
        
        # Add any other attributes from the record
        for key, value in record.__dict__.items():
            if key not in ("args", "asctime", "created", "exc_info", "exc_text", 
                          "filename", "funcName", "id", "levelname", "levelno",
                          "lineno", "module", "msecs", "message", "msg", 
                          "name", "pathname", "process", "processName", 
                          "relativeCreated", "stack_info", "thread", "threadName"):
                log_data[key] = value
        
        return json.dumps(log_data)


@contextmanager
def log_context(**kwargs: Any) -> None:
    """
    Context manager for adding context to logs.
    
    Example:
        with log_context(user_id="123", action="login"):
            logger.info("User logged in")
    """
    old_context = _get_context().copy()
    _thread_local.context = {**old_context, **kwargs}
    try:
        yield
    finally:
        _thread_local.context = old_context


def with_log_context(**context_kwargs: Any):
    """
    Decorator to add context to logs in a function.
    
    Example:
        @with_log_context(component="authentication")
        def authenticate_user(username, password):
            logger.info(f"Authenticating user {username}")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with log_context(**context_kwargs):
                return func(*args, **kwargs)
        return wrapper
    return decorator


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
            handler = self._create_handler(handler_config)
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
        
        handlers = [LogHandlerConfig(type="console", level=log_level, format=log_format)]
        
        if log_json:
            handlers[0].format = JSON_FORMAT
        
        if log_file:
            file_handler = LogHandlerConfig(
                type="file",
                level=log_level,
                format=log_format,
                filename=log_file,
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
    
    def _create_handler(self, config: LogHandlerConfig) -> Optional[logging.Handler]:
        """
        Create a log handler from the given configuration.
        
        Parameters
        ----------
        config : LogHandlerConfig
            Handler configuration
        
        Returns
        -------
        logging.Handler, optional
            Configured handler, or None if the handler type is invalid
        """
        handler = None
        level = getattr(logging, config.level, logging.INFO)
        
        if config.type == "console":
            handler = logging.StreamHandler(sys.stdout)
        elif config.type == "file":
            if not config.filename:
                log_dir = Path(self.config.log_file_path or "./logs")
                log_dir.mkdir(exist_ok=True, parents=True)
                config.filename = str(log_dir / f"{self.name}.log")
            
            # Use rotating file handler if max_bytes is set
            if config.max_bytes:
                from logging.handlers import RotatingFileHandler
                handler = RotatingFileHandler(
                    config.filename,
                    maxBytes=config.max_bytes,
                    backupCount=config.backup_count or 5,
                )
            else:
                handler = logging.FileHandler(config.filename)
        elif config.type == "external":
            # This would integrate with external logging services
            # For demonstration, we'll just log to a file named 'external.log'
            handler = logging.FileHandler("external.log")
        else:
            self.logger.warning(f"Invalid handler type: {config.type}")
            return None
        
        handler.setLevel(level)
        
        # Configure the formatter
        if config.format == JSON_FORMAT:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(config.format)
        
        handler.setFormatter(formatter)
        return handler
    
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
        handler = Logger("root")._create_handler(handler_config)
        if handler:
            root_logger.addHandler(handler)
    
    # Capture warnings
    logging.captureWarnings(config.capture_warnings)


# Initialize request context for the current thread
def init_request_context(request_id: Optional[str] = None, **kwargs: Any) -> str:
    """
    Initialize a new request context with an optional request ID.
    
    Parameters
    ----------
    request_id : str, optional
        Request ID to use, or generate a new one if not provided
    **kwargs : Any
        Additional context to include in the log
    
    Returns
    -------
    str
        The request ID
    """
    request_id = request_id or _generate_request_id()
    context = {"request_id": request_id, "timestamp": datetime.now().isoformat()}
    context.update(kwargs)
    _thread_local.context = context
    return request_id


# Clear request context for the current thread
def clear_request_context() -> None:
    """Clear the request context for the current thread."""
    if hasattr(_thread_local, "context"):
        delattr(_thread_local, "context")


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


# Initialize the logging system
configure_root_logger()
