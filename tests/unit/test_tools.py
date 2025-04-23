"""Unit tests for the agent tools."""

import pytest
from unittest.mock import patch, MagicMock

from PRISMAgent.tools.spawn import spawn_agent


def test_spawn_agent_format():
    """Test that the spawn_agent tool has the correct format."""
    assert spawn_agent.name == "spawn_agent"
    assert "Create a new agent" in spawn_agent.description
    assert callable(spawn_agent.func)


@pytest.mark.asyncio
async def test_spawn_agent_execution():
    """Test that the spawn_agent tool executes correctly."""
    with patch("PRISMAgent.tools.spawn.agent_factory") as mock_factory, \
         patch("PRISMAgent.tools.spawn.runner_factory") as mock_runner_factory:
        
        # Mock the agent and runner
        mock_agent = MagicMock()
        mock_factory.return_value = mock_agent
        
        mock_runner = MagicMock()
        mock_runner.run.return_value = "Test response"
        mock_runner_factory.return_value = mock_runner
        
        # Execute the tool function
        result = await spawn_agent(
            agent_type="coder",
            system_prompt="You are a specialized coding assistant.",
            task="Write a Python function to calculate Fibonacci numbers.",
            complexity="advanced"
        )
        
        # Check that the agent factory was called with the correct arguments
        mock_factory.assert_called_once()
        factory_args = mock_factory.call_args[0]
        factory_kwargs = mock_factory.call_args[1]
        
        # Verify agent name format includes the agent type
        assert "coder_" in factory_args[0]
        
        # Check instructions contains the specialized prompt
        assert "You are a specialized coding assistant" in factory_args[1]
        
        # Verify complexity was passed through
        assert factory_kwargs["complexity"] == "advanced"
        assert factory_kwargs["task"] == "code"
        
        # Check that the runner was created with stream=False
        mock_runner_factory.assert_called_once_with(stream=False)
        
        # Check that the runner was called with the correct arguments
        mock_runner.run.assert_called_once_with(mock_agent, "Write a Python function to calculate Fibonacci numbers.")
        
        # Check the result format
        assert "response" in result
        assert result["response"] == "Test response"


@pytest.mark.asyncio
async def test_spawn_agent_researcher():
    """Test that the spawn_agent properly configures a researcher agent."""
    with patch("PRISMAgent.tools.spawn.agent_factory") as mock_factory, \
         patch("PRISMAgent.tools.spawn.runner_factory") as mock_runner_factory:
        
        # Mock the agent and runner
        mock_agent = MagicMock()
        mock_factory.return_value = mock_agent
        
        mock_runner = MagicMock()
        mock_runner.run.return_value = "Research response"
        mock_runner_factory.return_value = mock_runner
        
        # Execute the tool function
        result = await spawn_agent(
            agent_type="researcher",
            system_prompt="Research quantum computing.",
            task="What are the latest developments in quantum computing?",
            complexity="auto"
        )
        
        # Check that the specialized system prompt was created
        factory_args = mock_factory.call_args[0]
        assert "You are a specialized research agent" in factory_args[1]
        
        # Verify task type is chat for researcher
        factory_kwargs = mock_factory.call_args[1]
        assert factory_kwargs["task"] == "chat"
        
        # Check the result
        assert result["response"] == "Research response" 