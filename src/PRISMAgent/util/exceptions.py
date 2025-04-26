"""
PRISMAgent.util.exceptions
-------------------------

Exception classes for the PRISMAgent package.

This module defines custom exceptions that are used throughout the PRISMAgent
package to provide more specific error handling and better error messages.
"""

from typing import Any, Dict, Optional


class PRISMAgentError(Exception):
    """Base exception class for all PRISMAgent errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a new PRISMAgentError.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        """Return a string representation of the error."""
        if not self.details:
            return self.message
        
        detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
        return f"{self.message} [Details: {detail_str}]"


class ConfigurationError(PRISMAgentError):
    """Error raised when there is a problem with configuration."""
    pass


class StorageError(PRISMAgentError):
    """Base class for storage-related errors."""
    pass


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
        super().__init__(f"Agent not found: {agent_name}", details)
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
        super().__init__(f"Agent already exists: {agent_name}", details)
        self.agent_name = agent_name


class ChatStorageError(StorageError):
    """Error related to chat history storage."""
    pass


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
        super().__init__(f"Tool not found: {tool_name}", details)
        self.tool_name = tool_name


class InvalidToolError(ToolError):
    """Error raised when a tool is invalid or improperly configured."""
    pass


class RunnerError(PRISMAgentError):
    """Error related to agent runners."""
    pass


class ExecutionError(PRISMAgentError):
    """Error during agent execution."""
    
    def __init__(self, message: str, agent_name: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
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
            
        super().__init__(f"{prefix}{message}", details)
