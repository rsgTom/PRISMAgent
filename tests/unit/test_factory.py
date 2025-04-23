"""Unit tests for the agent factory module."""

import pytest
from unittest.mock import patch, MagicMock

from PRISMAgent.engine.factory import agent_factory


@pytest.fixture
def mock_storage():
    """Return a mock storage backend."""
    storage = MagicMock()
    storage.get.return_value = None
    return storage


def test_agent_factory_creates_agent(base_settings, mock_storage):
    """Test that agent_factory creates an agent with the provided settings."""
    with patch("PRISMAgent.engine.factory.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        system_prompt = "You are a helpful assistant."
        agent = agent_factory(
            config=base_settings,
            storage=mock_storage,
            system_prompt=system_prompt,
            tools=[],
        )
        
        assert agent is not None
        assert agent.system_prompt == system_prompt
        assert agent.config == base_settings
        assert agent.storage == mock_storage
        assert len(agent.tools) == 0


def test_agent_factory_with_tools(base_settings, mock_storage):
    """Test that agent_factory creates an agent with the provided tools."""
    with patch("PRISMAgent.engine.factory.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        
        agent = agent_factory(
            config=base_settings,
            storage=mock_storage,
            system_prompt="You are a helpful assistant.",
            tools=[mock_tool],
        )
        
        assert agent is not None
        assert len(agent.tools) == 1
        assert agent.tools[0] == mock_tool 