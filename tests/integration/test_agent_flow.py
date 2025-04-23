"""Integration tests for agent flow."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from PRISMAgent.config.base import BaseSettings
from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage.file_backend import FileStorageBackend


@pytest.mark.asyncio
async def test_basic_agent_flow(temp_data_dir, mock_openai_response):
    """Test a basic agent flow from config to response."""
    # Create configuration
    config = BaseSettings(
        api_key="test-api-key",
        model_name="gpt-4",
        max_tokens=100,
    )
    
    # Initialize storage
    storage = FileStorageBackend(data_dir=str(temp_data_dir))
    
    # Create an agent
    with patch("PRISMAgent.engine.factory.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        # Configure the mock client to return the mock response
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_get_client.return_value = mock_client
        
        agent = agent_factory(
            config=config,
            storage=storage,
            system_prompt="You are a helpful assistant.",
            tools=[],
        )
        
        # Create a runner
        runner = runner_factory(streaming=False)
        
        # User query
        user_query = "What is the capital of France?"
        
        # Run the agent
        response = await runner.run(
            agent=agent,
            messages=[{"role": "user", "content": user_query}],
        )
        
        # Verify the mock was called with the expected parameters
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        
        # Check that the model matches
        assert call_args["model"] == config.model_name
        
        # Check that the messages include the system prompt and user query
        messages = call_args["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant."
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == user_query
        
        # Check response
        assert response is not None
        assert isinstance(response, list)
        assert len(response) > 0 