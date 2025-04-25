# PRISMAgent Logging System

This document provides an overview of the PRISMAgent logging system, including how to use it in your code.

## Overview

PRISMAgent includes a standardized, context-aware logging system that supports multiple output formats and destinations. The logging system is built on top of Python's standard `logging` module but provides additional features such as:

- Context-aware logging (request IDs, session info, etc.)
- Structured JSON logging
- Multiple output destinations (console, file, external services)
- Configurable log levels and formats
- Thread-local context storage

## Quick Start

To use the logging system in your code, simply import and use the `get_logger` function:

```python
from PRISMAgent.util import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Including Context Data

One of the most powerful features of the logging system is the ability to include context data in logs:

```python
from PRISMAgent.util import get_logger, log_context

logger = get_logger(__name__)

# Using the context manager
with log_context(user_id="123", action="login"):
    logger.info("User logged in")  # Will include user_id and action in log

# Including context directly in log calls
logger.info("Processing payment", payment_id="xyz-123", amount=99.99)
```

You can also use the `with_log_context` decorator to automatically add context to all logs within a function:

```python
from PRISMAgent.util import get_logger, with_log_context

logger = get_logger(__name__)

@with_log_context(component="auth")
def authenticate_user(username):
    logger.info(f"Authenticating user", username=username)
    # All logs in this function will include component="auth"
```

## Request Context

For web applications or APIs, you can use request context to automatically include request-specific information in all logs:

```python
from PRISMAgent.util import get_logger, init_request_context, clear_request_context

logger = get_logger(__name__)

# Initialize request context at the start of a request
request_id = init_request_context(user_agent="Mozilla/5.0", user_ip="192.168.1.1")

# All logs will now include the request_id and other context
logger.info("Processing request")

# Clear request context at the end of the request
clear_request_context()
```

## Configuration

The logging system can be configured through environment variables or programmatically.

### Environment Variables

The following environment variables can be used to configure logging:

- `LOG_LEVEL`: Minimum log level to output (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT`: Format style (default, detailed, json)
- `LOG_FILE`: Path to log file (empty for console only)
- `LOG_PATH`: Directory for log files
- `LOG_JSON`: Whether to use JSON format for logs (true/false)
- `LOG_ROTATE_MAX_BYTES`: Maximum size of log file before rotation
- `LOG_ROTATE_BACKUP_COUNT`: Number of backup files to keep
- `LOG_INCLUDE_CONTEXT`: Whether to include context information in logs (true/false)
- `LOG_EXTERNAL_URL`: URL for external logging service
- `LOG_EXTERNAL_TOKEN`: Auth token for external logging service

### Programmatic Configuration

You can also configure the logging system programmatically:

```python
from PRISMAgent.util import get_logger, LoggingConfig, LogHandlerConfig, LogLevel, configure_root_logger

# Create custom configuration
config = LoggingConfig(
    level=LogLevel.DEBUG,
    handlers=[
        LogHandlerConfig(
            type="console",
            level=LogLevel.INFO,
            format="default"
        ),
        LogHandlerConfig(
            type="file",
            level=LogLevel.DEBUG,
            format="detailed",
            filename="./logs/app.log",
            max_bytes=10 * 1024 * 1024,  # 10MB
            backup_count=5
        )
    ],
    capture_warnings=True,
    propagate=True,
    include_context=True,
    log_file_path="./logs"
)

# Configure root logger with custom config
configure_root_logger(config)

# Create logger with custom config
logger = get_logger("my_module", config)
```

## Log Formats

The system supports three predefined formats:

1. **default**: Simple format with timestamp, logger name, level, and message

   ```text
   2024-04-25 03:30:00,123 - my_module - INFO - User logged in
   ```

2. **detailed**: More detailed format with file, line number, and thread

   ```text
   2024-04-25 03:30:00,123 - my_module - INFO - [file.py:123] - MainThread - User logged in
   ```

3. **json**: Structured JSON format for machine parsing

   ```json
   {
     "timestamp": "2024-04-25 03:30:00,123",
     "level": "INFO",
     "name": "my_module",
     "message": "User logged in",
     "context": {
       "request_id": "c8f9e1a2-3b4c-5d6e-7f8a-9b0c1d2e3f4a",
       "user_id": "123",
       "action": "login"
     }
   }
   ```

## Best Practices

1. **Logger Naming**: Use `__name__` for logger names to automatically follow the Python module hierarchy.

2. **Log Levels**:
   - `DEBUG`: Detailed information, typically of interest only for diagnostics
   - `INFO`: Confirmation that things are working as expected
   - `WARNING`: Indication that something unexpected happened or may happen
   - `ERROR`: Due to a more serious problem, some functionality could not be performed
   - `CRITICAL`: A very serious error, indicating that the program itself may be unable to continue running

3. **Context Data**: Include relevant context in logs to make debugging easier.

4. **Sensitive Data**: Be careful not to log sensitive information such as passwords, API keys, or personal data.

5. **Performance**: Set appropriate log levels in production to avoid performance impact.

## Implementation

The PRISMAgent logging system has been implemented according to this documentation. The implementation includes:

1. A comprehensive logging system in `src/PRISMAgent/util/logging.py`
2. Configuration in `src/PRISMAgent/config/logging.py`
3. Integration with the application initialization in `src/PRISMAgent/__init__.py`

### Key Features Implemented

- ✅ Context-aware logging
- ✅ Structured JSON logging
- ✅ Multiple output destinations (console, file)
- ✅ Configurable log levels and formats
- ✅ Thread-local context storage
- ✅ Automatic log file directory creation
- ✅ Log file rotation

### How to Use

The logging system is automatically initialized when you import the PRISMAgent package. Logs are written to both the console and a file in the `logs` directory.

You can see a complete example of how to use the logging system in `examples/logging_example.py`.

### Logging Environment Variables

The logging system can be configured through environment variables in your `.env` file. See the `.env.example` file for all available options.

### Example Usage

```python
from PRISMAgent.util import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.info("User logged in", user_id="123")
logger.warning("Database connection slow", latency_ms=250)
logger.error("Failed to process payment", payment_id="xyz-123", error="Insufficient funds")
```

## Integration with External Services

The logging system can be configured to send logs to external services by implementing a custom handler or using the built-in "external" handler type.

To use the built-in external handler, set the `LOG_EXTERNAL_URL` and `LOG_EXTERNAL_TOKEN` environment variables or add an `LogHandlerConfig` with `type="external"` to your configuration.

## Troubleshooting

1. **No logs are appearing**: Check that your log level is not higher than the level of messages you're trying to log.

2. **Context data not appearing**: Make sure you're using the `log_context` context manager, `with_log_context` decorator, or `init_request_context` function properly.

3. **JSON logs not properly formatted**: If using JSON logging in files, ensure the log file has the correct permissions and that the application has write access.

## Further Reading

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Structured Logging](https://www.structlog.org/en/stable/)
- [12-Factor App: Logs](https://12factor.net/logs)
