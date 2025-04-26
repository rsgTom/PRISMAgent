"""
PRISMAgent.util
--------------

Utility modules for the PRISMAgent package.
"""

from .logging import (
    get_logger,
    Logger,
    LoggingConfig,
    LogHandlerConfig,
    LogLevel,
    log_context,
    with_log_context,
    init_request_context,
    clear_request_context,
    configure_root_logger,
)

from .exceptions import (
    PRISMAgentError,
    ConfigurationError,
    EnvironmentVariableError,
    InvalidConfigurationError,
    StorageError,
    DatabaseConnectionError,
    RegistryError,
    AgentNotFoundError,
    AgentExistsError,
    ChatStorageError,
    ToolError,
    ToolNotFoundError,
    ToolExecutionError,
    InvalidToolError,
    RunnerError,
    RunnerConfigurationError,
    ExecutionError,
    ModelAPIError,
    ValidationError,
    AuthenticationError,
)

from .error_handling import (
    handle_exceptions,
    error_context,
    format_exception_with_context,
    validate_or_raise,
)

__all__ = [
    # Logging
    "get_logger",
    "Logger",
    "LoggingConfig",
    "LogHandlerConfig",
    "LogLevel",
    "log_context",
    "with_log_context",
    "init_request_context",
    "clear_request_context",
    "configure_root_logger",
    
    # Exceptions
    "PRISMAgentError",
    "ConfigurationError",
    "EnvironmentVariableError",
    "InvalidConfigurationError",
    "StorageError",
    "DatabaseConnectionError",
    "RegistryError",
    "AgentNotFoundError",
    "AgentExistsError", 
    "ChatStorageError",
    "ToolError",
    "ToolNotFoundError",
    "ToolExecutionError",
    "InvalidToolError",
    "RunnerError",
    "RunnerConfigurationError",
    "ExecutionError",
    "ModelAPIError",
    "ValidationError",
    "AuthenticationError",
    
    # Error Handling
    "handle_exceptions",
    "error_context",
    "format_exception_with_context",
    "validate_or_raise",
]
