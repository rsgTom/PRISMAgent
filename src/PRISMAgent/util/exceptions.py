"""
PRISMAgent.util.exceptions
---------------------

Exception classes for the PRISMAgent package.

This module defines custom exceptions that are used throughout the PRISMAgent
package to provide more specific error handling and better error messages.
Each exception includes contextual information and suggestions for resolution
when applicable.
"""

from typing import Any, Dict, Optional, List, Union


class PRISMAgentError(Exception):
    """Base exception class for all PRISMAgent errors."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        """
        Initialize a new PRISMAgentError.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
            suggestions: Optional list of suggestions to resolve the error
        """
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []
        super().__init__(message)
    
    def __str__(self) -> str:
        """Return a string representation of the error."""
        result = self.message
        
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            result += f" [Details: {detail_str}]"
        
        if self.suggestions:
            suggestions_str = "\n- " + "\n- ".join(self.suggestions)
            result += f"\n\nSuggested solutions:{suggestions_str}"
            
        return result


# Configuration Errors
class ConfigurationError(PRISMAgentError):
    """Error raised when there is a problem with configuration."""
    pass


class EnvironmentVariableError(ConfigurationError):
    """Error raised when required environment variables are missing or invalid."""
    
    def __init__(
        self, 
        variable_name: str, 
        message: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new EnvironmentVariableError.
        
        Args:
            variable_name: Name of the environment variable causing the error
            message: Custom error message (optional)
            details: Optional dictionary with additional error details
        """
        if message is None:
            message = f"Missing or invalid environment variable: {variable_name}"
        
        details = details or {}
        details["variable_name"] = variable_name
        
        suggestions = [
            f"Make sure {variable_name} is set in your environment",
            f"Check .env.example for the correct format of {variable_name}",
            "Run the application with the correct environment configuration"
        ]
        
        super().__init__(message, details, suggestions)


class InvalidConfigurationError(ConfigurationError):
    """Error raised when the configuration is invalid."""
    
    def __init__(
        self, 
        config_key: str, 
        expected_type: Optional[Any] = None, 
        received_value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new InvalidConfigurationError.
        
        Args:
            config_key: The configuration key that is invalid
            expected_type: The expected type or value (optional)
            received_value: The received invalid value (optional)
            details: Optional dictionary with additional error details
        """
        message = f"Invalid configuration for '{config_key}'"
        
        details = details or {}
        details["config_key"] = config_key
        
        if expected_type is not None:
            details["expected_type"] = str(expected_type)
            message += f", expected {expected_type}"
            
        if received_value is not None:
            details["received_value"] = str(received_value)
            message += f", received {received_value}"
            
        suggestions = [
            f"Check the configuration for '{config_key}'",
            "Refer to the documentation for valid configuration values"
        ]
        
        super().__init__(message, details, suggestions)


# Storage Errors
class StorageError(PRISMAgentError):
    """Base class for storage-related errors."""
    pass


class DatabaseConnectionError(StorageError):
    """Error raised when unable to connect to a database."""
    
    def __init__(
        self, 
        db_name: str, 
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new DatabaseConnectionError.
        
        Args:
            db_name: Name or type of the database
            error_message: The original error message
            details: Optional dictionary with additional error details
        """
        message = f"Failed to connect to {db_name} database: {error_message}"
        
        details = details or {}
        details["db_name"] = db_name
        details["original_error"] = error_message
        
        suggestions = [
            "Check that the database server is running",
            "Verify database connection credentials in your environment variables",
            "Make sure the database exists and is accessible from your network",
            "Check for firewall or network restrictions"
        ]
        
        super().__init__(message, details, suggestions)


class RegistryError(StorageError):
    """Error related to the agent registry."""
    pass


class AgentNotFoundError(RegistryError):
    """Error raised when an agent is not found in the registry."""
    
    def __init__(self, agent_name: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a new AgentNotFoundError.
        
        Args:
            agent_name: Name of the agent that was not found
            details: Optional dictionary with additional error details
        """
        message = f"Agent not found: {agent_name}"
        
        details = details or {}
        details["agent_name"] = agent_name
        
        available_agents = details.get("available_agents", [])
        
        suggestions = [
            "Check that the agent name is spelled correctly",
            "Make sure the agent has been registered before use",
            "Use agent_factory to create and register the agent first"
        ]
        
        if available_agents:
            agents_str = ", ".join(available_agents)
            suggestions.append(f"Available agents: {agents_str}")
        
        super().__init__(message, details, suggestions)
        self.agent_name = agent_name


class AgentExistsError(RegistryError):
    """Error raised when trying to register an agent that already exists."""
    
    def __init__(self, agent_name: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a new AgentExistsError.
        
        Args:
            agent_name: Name of the agent that already exists
            details: Optional dictionary with additional error details
        """
        message = f"Agent already exists: {agent_name}"
        
        details = details or {}
        details["agent_name"] = agent_name
        
        suggestions = [
            f"Use a different name for the new agent",
            f"If you need to replace the existing agent, unregister it first",
            f"Access the existing agent through the registry instead of creating a new one"
        ]
        
        super().__init__(message, details, suggestions)
        self.agent_name = agent_name


class ChatStorageError(StorageError):
    """Error related to chat history storage."""
    
    def __init__(
        self, 
        operation: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ChatStorageError.
        
        Args:
            operation: The storage operation that failed (e.g., "read", "write")
            message: Specific error message
            details: Optional dictionary with additional error details
        """
        full_message = f"Chat storage {operation} operation failed: {message}"
        
        details = details or {}
        details["operation"] = operation
        
        suggestions = [
            "Check that the storage backend is properly configured",
            "Verify you have the necessary permissions for the operation"
        ]
        
        super().__init__(full_message, details, suggestions)


# Tool-related Errors
class ToolError(PRISMAgentError):
    """Base class for tool-related errors."""
    pass


class ToolNotFoundError(ToolError):
    """Error raised when a tool is not found."""
    
    def __init__(self, tool_name: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a new ToolNotFoundError.
        
        Args:
            tool_name: Name of the tool that was not found
            details: Optional dictionary with additional error details
        """
        message = f"Tool not found: {tool_name}"
        
        details = details or {}
        details["tool_name"] = tool_name
        
        available_tools = details.get("available_tools", [])
        
        suggestions = [
            "Check that the tool name is spelled correctly",
            "Make sure the tool has been registered before use",
            "Use tool_factory to create and register the tool first"
        ]
        
        if available_tools:
            tools_str = ", ".join(available_tools)
            suggestions.append(f"Available tools: {tools_str}")
        
        super().__init__(message, details, suggestions)
        self.tool_name = tool_name


class InvalidToolError(ToolError):
    """Error raised when a tool is invalid or improperly configured."""
    
    def __init__(
        self, 
        tool_name: str, 
        reason: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new InvalidToolError.
        
        Args:
            tool_name: Name of the invalid tool
            reason: Reason why the tool is invalid
            details: Optional dictionary with additional error details
        """
        message = f"Invalid tool '{tool_name}': {reason}"
        
        details = details or {}
        details["tool_name"] = tool_name
        details["reason"] = reason
        
        suggestions = [
            "Check the tool configuration for syntax errors",
            "Ensure the tool has all required parameters set",
            "Verify that all dependencies for the tool are installed"
        ]
        
        super().__init__(message, details, suggestions)


class ToolExecutionError(ToolError):
    """Error raised when tool execution fails."""
    
    def __init__(
        self, 
        tool_name: str, 
        error_message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ToolExecutionError.
        
        Args:
            tool_name: Name of the tool that failed
            error_message: The error message from the tool
            details: Optional dictionary with additional error details
        """
        message = f"Tool '{tool_name}' execution failed: {error_message}"
        
        details = details or {}
        details["tool_name"] = tool_name
        details["error_message"] = error_message
        
        suggestions = [
            "Check the input parameters passed to the tool",
            "Verify that any external services the tool depends on are available",
            "Check the logs for more detailed error information"
        ]
        
        super().__init__(message, details, suggestions)


# Runner Errors
class RunnerError(PRISMAgentError):
    """Error related to agent runners."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        """
        Initialize a new RunnerError.
        
        Args:
            message: Error message
            details: Optional dictionary with additional error details
            suggestions: Optional list of suggestions to resolve the error
        """
        if suggestions is None:
            suggestions = [
                "Check that the runner configuration is valid",
                "Verify that all required components are available",
                "Ensure the model settings are properly configured"
            ]
        
        super().__init__(message, details, suggestions)


class RunnerConfigurationError(RunnerError):
    """Error raised when the runner configuration is invalid."""
    
    def __init__(
        self, 
        config_issue: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new RunnerConfigurationError.
        
        Args:
            config_issue: Description of the configuration issue
            details: Optional dictionary with additional error details
        """
        message = f"Invalid runner configuration: {config_issue}"
        
        suggestions = [
            "Review the runner settings in your configuration",
            "Check model settings and availability"
        ]
        
        super().__init__(message, details, suggestions)


# Execution Errors
class ExecutionError(PRISMAgentError):
    """Error during agent execution."""
    
    def __init__(
        self, 
        message: str, 
        agent_name: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ExecutionError.
        
        Args:
            message: Human-readable error message
            agent_name: Optional name of the agent that encountered the error
            details: Optional dictionary with additional error details
        """
        self.agent_name = agent_name
        details = details or {}
        
        if agent_name:
            details["agent_name"] = agent_name
            prefix = f"Error executing agent '{agent_name}': "
        else:
            prefix = "Execution error: "
            
        suggestions = [
            "Check the agent's configuration and tools",
            "Verify the input meets the agent's requirements",
            "Review the logs for detailed error information"
        ]
            
        super().__init__(f"{prefix}{message}", details, suggestions)


class ModelAPIError(ExecutionError):
    """Error during interaction with the language model API."""
    
    def __init__(
        self, 
        api_error: str, 
        model_name: str,
        status_code: Optional[int] = None,
        agent_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ModelAPIError.
        
        Args:
            api_error: Error message from the API
            model_name: Name of the model being used
            status_code: HTTP status code (if applicable)
            agent_name: Optional name of the agent that encountered the error
            details: Optional dictionary with additional error details
        """
        message = f"Model API error with {model_name}: {api_error}"
        
        details = details or {}
        details["model_name"] = model_name
        details["api_error"] = api_error
        
        if status_code is not None:
            details["status_code"] = status_code
            message = f"{message} (Status: {status_code})"
        
        suggestions = []
        
        if status_code == 401 or status_code == 403:
            suggestions.append("Check your API key and permissions")
        elif status_code == 429:
            suggestions.append("You've hit rate limits. Try again later or increase your quota")
        elif status_code and status_code >= 500:
            suggestions.append("The model service may be experiencing issues. Try again later")
        elif status_code and status_code >= 400:
            suggestions.append("Check your request parameters for errors")
        
        suggestions.extend([
            "Verify your model settings in the configuration",
            "Ensure your network connection to the API is stable"
        ])
        
        super().__init__(message, agent_name, details)
        # Override the default suggestions
        self.suggestions = suggestions


class ValidationError(PRISMAgentError):
    """Error raised when input validation fails."""
    
    def __init__(
        self, 
        field_name: str, 
        error_details: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new ValidationError.
        
        Args:
            field_name: Name of the field that failed validation
            error_details: Details about the validation error
            details: Optional dictionary with additional error details
        """
        message = f"Validation error for field '{field_name}': {error_details}"
        
        details = details or {}
        details["field_name"] = field_name
        details["error_details"] = error_details
        
        suggestions = [
            f"Check the input value for '{field_name}'",
            "Refer to the documentation for valid input formats"
        ]
        
        super().__init__(message, details, suggestions)


class AuthenticationError(PRISMAgentError):
    """Error raised when authentication fails."""
    
    def __init__(
        self, 
        reason: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new AuthenticationError.
        
        Args:
            reason: Reason for the authentication failure
            details: Optional dictionary with additional error details
        """
        message = f"Authentication failed: {reason}"
        
        details = details or {}
        details["reason"] = reason
        
        suggestions = [
            "Check your credentials and permissions",
            "Verify your token hasn't expired",
            "Ensure you're using the correct authentication method"
        ]
        
        super().__init__(message, details, suggestions)
