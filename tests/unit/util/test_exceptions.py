"""
Tests for PRISMAgent.util.exceptions module.

This test suite covers the custom exception classes and their functionality.
"""

import pytest

from PRISMAgent.util.exceptions import (
    PRISMAgentError,
    ConfigurationError,
    EnvironmentVariableError,
    InvalidConfigurationError,
    StorageError,
    AgentNotFoundError,
    ToolNotFoundError,
    ExecutionError,
    ModelAPIError,
    ValidationError
)


class TestExceptions:
    """Test custom exception classes."""
    
    def test_base_exception(self):
        """Test PRISMAgentError base exception class."""
        # Simple message
        error = PRISMAgentError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == {}
        assert error.suggestions == []
        
        # With details
        error = PRISMAgentError(
            "Test error", 
            details={"key1": "value1", "key2": 123}
        )
        assert "Test error" in str(error)
        assert "key1=value1" in str(error)
        assert "key2=123" in str(error)
        
        # With suggestions
        error = PRISMAgentError(
            "Test error",
            suggestions=["Fix this", "Check that"]
        )
        assert "Test error" in str(error)
        assert "Suggested solutions:" in str(error)
        assert "- Fix this" in str(error)
        assert "- Check that" in str(error)
        
        # With both details and suggestions
        error = PRISMAgentError(
            "Test error",
            details={"key": "value"},
            suggestions=["Fix this"]
        )
        assert "Test error" in str(error)
        assert "key=value" in str(error)
        assert "Suggested solutions:" in str(error)
        assert "- Fix this" in str(error)
    
    def test_configuration_errors(self):
        """Test configuration error classes."""
        # EnvironmentVariableError
        env_error = EnvironmentVariableError("API_KEY")
        assert "API_KEY" in str(env_error)
        assert env_error.details.get("variable_name") == "API_KEY"
        assert any("API_KEY" in suggestion for suggestion in env_error.suggestions)
        
        # With custom message
        env_error = EnvironmentVariableError(
            "API_KEY", 
            message="API key is required for authentication"
        )
        assert "API key is required" in str(env_error)
        
        # InvalidConfigurationError
        config_error = InvalidConfigurationError("max_tokens", "integer", "string")
        assert "max_tokens" in str(config_error)
        assert "expected integer" in str(config_error)
        assert "received string" in str(config_error)
        assert config_error.details.get("config_key") == "max_tokens"
        assert config_error.details.get("expected_type") == "integer"
    
    def test_storage_errors(self):
        """Test storage error classes."""
        # AgentNotFoundError
        agent_error = AgentNotFoundError("sql_expert")
        assert "Agent not found: sql_expert" in str(agent_error)
        assert agent_error.agent_name == "sql_expert"
        
        # With available agents
        agent_error = AgentNotFoundError(
            "sql_expert", 
            details={"available_agents": ["code_assistant", "researcher"]}
        )
        assert "Agent not found: sql_expert" in str(agent_error)
        assert any("available_agents" in suggestion for suggestion in agent_error.suggestions)
    
    def test_tool_errors(self):
        """Test tool error classes."""
        # ToolNotFoundError
        tool_error = ToolNotFoundError("search_tool")
        assert "Tool not found: search_tool" in str(tool_error)
        assert tool_error.tool_name == "search_tool"
        
        # With available tools
        tool_error = ToolNotFoundError(
            "search_tool", 
            details={"available_tools": ["calculator", "web_browser"]}
        )
        assert "Tool not found: search_tool" in str(tool_error)
        assert any("calculator" in suggestion for suggestion in tool_error.suggestions)
    
    def test_execution_errors(self):
        """Test execution error classes."""
        # ExecutionError
        exec_error = ExecutionError("Failed to execute", "test_agent")
        assert "Error executing agent 'test_agent'" in str(exec_error)
        assert exec_error.agent_name == "test_agent"
        
        # ModelAPIError
        api_error = ModelAPIError(
            "Rate limit exceeded",
            "gpt-4",
            status_code=429,
            agent_name="test_agent"
        )
        assert "Model API error with gpt-4" in str(api_error)
        assert "Rate limit exceeded" in str(api_error)
        assert "Status: 429" in str(api_error)
        assert any("rate limits" in suggestion.lower() for suggestion in api_error.suggestions)
        
        # Different status codes should provide different suggestions
        api_error_401 = ModelAPIError(
            "Invalid API key",
            "gpt-4",
            status_code=401
        )
        assert any("API key" in suggestion for suggestion in api_error_401.suggestions)
        
        api_error_500 = ModelAPIError(
            "Server error",
            "gpt-4",
            status_code=500
        )
        assert any("service may be experiencing issues" in suggestion 
                  for suggestion in api_error_500.suggestions)
    
    def test_validation_error(self):
        """Test validation error class."""
        val_error = ValidationError("username", "Must be at least 3 characters")
        assert "Validation error for field 'username'" in str(val_error)
        assert "Must be at least 3 characters" in str(val_error)
        assert val_error.details.get("field_name") == "username"
        assert val_error.details.get("error_details") == "Must be at least 3 characters"
        assert any("username" in suggestion for suggestion in val_error.suggestions)
