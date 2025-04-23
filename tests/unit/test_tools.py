"""Unit tests for the agent tools."""

import pytest
from unittest.mock import patch, MagicMock

from PRISMAgent.tools.spawn import spawn_agent


def test_spawn_agent_format():
    """Test that the spawn_agent tool has the correct format."""
    assert spawn_agent.name == "spawn_agent"
    assert "Create a new agent" in spawn_agent.description
    assert "agent_type" in spawn_agent.parameters.get("properties", {})
    assert "system_prompt" in spawn_agent.parameters.get("properties", {})
    assert "task" in spawn_agent.parameters.get("properties", {})


@pytest.mark.asyncio
async def test_spawn_agent_execution():
    """Test that the spawn_agent tool executes correctly."""
    with patch("PRISMAgent.tools.spawn.agent_factory") as mock_factory, \
         patch("PRISMAgent.tools.spawn.runner_factory") as mock_runner_factory:
        
        # Mock the agent and runner
        mock_agent = MagicMock()
        mock_factory.return_value = mock_agent
        
        mock_runner = MagicMock()
        mock_runner.run.return_value = ["Test response"]
        mock_runner_factory.return_value = mock_runner
        
        # Create the arguments for the tool
        kwargs = {
            "agent_type": "assistant",
            "system_prompt": "You are a specialized coding assistant.",
            "task": "Write a Python function to calculate Fibonacci numbers."
        }
        
        # Execute the tool function
        result = await spawn_agent.function(**kwargs)
        
        # Check that the agent factory was called with the correct arguments
        mock_factory.assert_called_once()
        factory_args = mock_factory.call_args[1]
        assert factory_args["system_prompt"] == kwargs["system_prompt"]
        
        # Check that the runner was called with the correct arguments
        mock_runner.run.assert_called_once()
        run_args = mock_runner.run.call_args[1]
        assert run_args["agent"] == mock_agent
        assert isinstance(run_args["messages"], list)
        assert run_args["messages"][0]["content"] == kwargs["task"]
        
        # Check the result format
        assert "response" in result
        assert result["response"] == "Test response" 