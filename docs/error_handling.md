# Error Handling Guidelines

PRISMAgent provides a comprehensive error handling framework to ensure that errors are:

1. Clearly communicated to users and developers
2. Easy to debug with detailed context
3. Consistent across the codebase
4. Actionable with suggestions for resolution

## Exception Hierarchy

All PRISMAgent exceptions inherit from `PRISMAgentError`, which provides the base functionality:

```
PRISMAgentError
├── ConfigurationError
│   ├── EnvironmentVariableError
│   └── InvalidConfigurationError
├── StorageError
│   ├── DatabaseConnectionError
│   ├── RegistryError
│   │   ├── AgentNotFoundError
│   │   └── AgentExistsError
│   └── ChatStorageError
├── ToolError
│   ├── ToolNotFoundError
│   ├── InvalidToolError
│   └── ToolExecutionError
├── RunnerError
│   └── RunnerConfigurationError
├── ExecutionError
│   └── ModelAPIError
├── ValidationError
└── AuthenticationError
```

## Error Structure

Each error includes:

- **Message**: A human-readable description of what went wrong
- **Details**: A dictionary of context related to the error
- **Suggestions**: Actionable guidance on how to resolve the error

Example error message:

```
Error executing agent 'sql_expert': API key not found [Details: agent_name=sql_expert, error_type=AuthenticationError]

Suggested solutions:
- Check your API key in the environment variables
- Ensure your API key has not expired
- Verify you're using the correct authentication method
```

## Using the Error Handling Framework

### 1. Raising Specific Exceptions

When raising exceptions, use the most specific exception class that applies:

```python
from PRISMAgent.util.exceptions import AgentNotFoundError

def get_agent(agent_name):
    if agent_name not in registry:
        available_agents = list(registry.keys())
        raise AgentNotFoundError(
            agent_name, 
            details={"available_agents": available_agents}
        )
    return registry[agent_name]
```

### 2. Using the `handle_exceptions` Decorator

The `handle_exceptions` decorator standardizes exception handling across functions:

```python
from PRISMAgent.util.error_handling import handle_exceptions
from PRISMAgent.util.exceptions import ValidationError, StorageError

@handle_exceptions(
    error_map={
        ValueError: ValidationError,
        OSError: StorageError,
    },
    default_error_class=ExecutionError
)
def process_data(data):
    # Function implementation
    # Any exceptions will be caught and converted based on error_map
```

### 3. Using the `error_context` Context Manager

The `error_context` context manager adds context to exceptions raised within a block:

```python
from PRISMAgent.util.error_handling import error_context

def initialize_database(config):
    with error_context(
        "Database initialization failed",
        error_map={ConnectionError: DatabaseConnectionError},
        context_details={"db_host": config.host}
    ):
        # Connect to database
        # Any exceptions will include the context message and details
```

### 4. Using `validate_or_raise` for Validation

The `validate_or_raise` utility is useful for validation checks:

```python
from PRISMAgent.util.error_handling import validate_or_raise

def set_max_tokens(value):
    validate_or_raise(
        isinstance(value, int) and value > 0,
        "Max tokens must be a positive integer",
        "max_tokens",
        details={"provided_value": value, "expected_type": "positive integer"}
    )
    # Continue with implementation
```

## Logging with Errors

PRISMAgent integrates error handling with a robust logging system:

```python
from PRISMAgent.util import get_logger

logger = get_logger(__name__)

try:
    # Operation that might fail
except PRISMAgentError as e:
    logger.error(
        f"Operation failed: {e.message}",
        error_type=type(e).__name__,
        **e.details
    )
    raise
```

## Error Handling Best Practices

1. **Be Specific**: Use the most specific exception class that applies to your situation
2. **Include Context**: Always include relevant details that will help diagnose the issue
3. **Add Suggestions**: Where possible, include actionable suggestions for resolving the error
4. **Log Comprehensively**: Log errors with context before raising them
5. **Validate Early**: Use `validate_or_raise` to catch invalid inputs early
6. **Use Decorators**: Apply the `handle_exceptions` decorator to standardize error handling

## Example: Complete Error Handling Flow

```python
from PRISMAgent.util import get_logger
from PRISMAgent.util.exceptions import ValidationError, ExecutionError
from PRISMAgent.util.error_handling import handle_exceptions, error_context, validate_or_raise

logger = get_logger(__name__)

@handle_exceptions(
    error_map={
        ValueError: ValidationError,
        ConnectionError: ExecutionError
    }
)
def execute_query(db_client, query, timeout=30):
    # Validate inputs
    validate_or_raise(
        isinstance(timeout, (int, float)) and timeout > 0,
        "Timeout must be a positive number",
        "timeout",
        details={"provided": timeout}
    )
    
    validate_or_raise(
        query and isinstance(query, str),
        "Query must be a non-empty string",
        "query",
        details={"provided_type": type(query).__name__}
    )
    
    # Execute the query with error context
    with error_context(
        "Failed to execute database query",
        context_details={"query_length": len(query), "timeout": timeout}
    ):
        logger.debug(f"Executing query with timeout {timeout}s")
        return db_client.execute(query, timeout=timeout)
```

## Error Codes (Future Enhancement)

In future releases, PRISMAgent will include standardized error codes for error categorization:

- **CONF-001**: Configuration errors
- **STRG-001**: Storage-related errors
- **TOOL-001**: Tool-related errors
- **EXEC-001**: Execution errors
- **AUTH-001**: Authentication/authorization errors

These codes will help with error tracking and documentation.
