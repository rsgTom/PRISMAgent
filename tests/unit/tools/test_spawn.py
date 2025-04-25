"""Unit tests for the spawn_agent function tool."""

from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from PRISMAgent.tools.spawn import spawn_agent
from agents import Agent


@pytest.fixture
def mock_registry():
    """Create a mock registry that can be used to test agent spawning."""
    with patch("PRISMAgent.storage.registry_factory") as mock_registry_factory:
        registry_mock = AsyncMock()
        mock_registry_factory.return_value = registry_mock
        yield registry_mock


@pytest.fixture
def mock_agent_factory():
    """Create a mock agent_factory that can be injected for testing."""
    with patch("PRISMAgent.tools.spawn.agent_factory") as mock_factory:
        # Configure the mock to return a Mock agent
        agent_mock = MagicMock(spec=Agent)
        agent_mock.name = "test_agent"
        mock_factory.return_value = agent_mock
        yield mock_factory, agent_mock


@pytest.fixture
def mock_available_tools():
    """Create a mock for the list_available_tools function."""
    with patch("PRISMAgent.tools.list_available_tools") as mock_tools_list:
        mock_tools_list.return_value = ["test_tool", "another_tool"]
        yield mock_tools_list


@pytest.fixture
def mock_import_module():
    """Create a mock for importlib.import_module."""
    with patch("importlib.import_module") as mock_import:
        module_mock = MagicMock()
        # Create a mock tool function to return
        tool_function = MagicMock()
        tool_function.__name__ = "test_tool"
        tool_function.__prism_name__ = "test_tool"
        
        # Set up the module mock to return the tool function
        module_mock.test_tool = tool_function
        mock_import.return_value = module_mock
        
        yield mock_import, tool_function


@pytest.mark.asyncio
async def test_spawn_agent_with_string_tools(mock_registry, mock_agent_factory, mock_available_tools, mock_import_module):
    """Test spawn_agent when passed tool names as strings."""
    mock_factory, mock_agent = mock_agent_factory
    _, tool_function = mock_import_module
    
    # Call the spawn_agent function with a tool name
    result = await spawn_agent(
        name="new_agent",
        instructions="You are a test agent",
        tools=["test_tool"]
    )
    
    # Verify it correctly creates the agent
    mock_factory.assert_called_once()
    factory_args = mock_factory.call_args[1]
    assert factory_args["name"] == "new_agent"
    assert factory_args["instructions"] == "You are a test agent"
    assert len(factory_args["tools"]) == 1
    assert factory_args["tools"][0] == tool_function
    
    # Verify the result is as expected
    assert result["id"] == "test_agent"
    assert result["status"] == "created"
    assert "test_tool" in result["tools"]


@pytest.mark.asyncio
async def test_spawn_agent_with_callable_tools(mock_registry, mock_agent_factory):
    """Test spawn_agent when passed tool functions directly."""
    mock_factory, mock_agent = mock_agent_factory
    
    # Create a mock tool
    mock_tool = MagicMock()
    mock_tool.__name__ = "direct_tool"
    
    # Call the spawn_agent function with a direct tool reference
    result = await spawn_agent(
        name="new_agent",
        instructions="You are a test agent",
        tools=[mock_tool]
    )
    
    # Verify it correctly creates the agent
    mock_factory.assert_called_once()
    factory_args = mock_factory.call_args[1]
    assert factory_args["name"] == "new_agent"
    assert factory_args["instructions"] == "You are a test agent"
    assert len(factory_args["tools"]) == 1
    assert factory_args["tools"][0] == mock_tool
    
    # Verify the result is as expected
    assert result["id"] == "test_agent"
    assert result["status"] == "created"
    assert "direct_tool" in result["tools"]


@pytest.mark.asyncio
async def test_spawn_agent_with_handoffs(mock_registry, mock_agent_factory):
    """Test spawn_agent when passed handoffs parameter."""
    mock_factory, mock_agent = mock_agent_factory
    registry_mock = mock_registry
    
    # Create a mock agent that the registry will return
    handoff_agent = MagicMock(spec=Agent)
    handoff_agent.name = "handoff_agent"
    registry_mock.get_agent.return_value = handoff_agent
    
    # Call the spawn_agent function with handoffs
    result = await spawn_agent(
        name="new_agent",
        instructions="You are a test agent",
        handoffs=["handoff_agent"]
    )
    
    # Verify it correctly creates the agent
    mock_factory.assert_called_once()
    factory_args = mock_factory.call_args[1]
    assert factory_args["name"] == "new_agent"
    assert factory_args["instructions"] == "You are a test agent"
    assert len(factory_args["handoffs"]) == 1
    assert factory_args["handoffs"][0] == handoff_agent
    
    # Verify the result is as expected
    assert result["id"] == "test_agent"
    assert result["status"] == "created"
    assert "handoff_agent" in result["handoffs"]


@pytest.mark.asyncio
async def test_spawn_agent_invalid_tool(mock_registry, mock_agent_factory, mock_available_tools):
    """Test that spawn_agent raises an error when passed an invalid tool name."""
    with pytest.raises(ValueError) as excinfo:
        await spawn_agent(
            name="new_agent",
            instructions="You are a test agent",
            tools=["nonexistent_tool"]
        )
    
    assert "Invalid tool name" in str(excinfo.value)


@pytest.mark.asyncio
async def test_spawn_agent_invalid_handoff(mock_registry, mock_agent_factory):
    """Test that spawn_agent raises an error when passed an invalid handoff agent."""
    registry_mock = mock_registry
    registry_mock.get_agent.return_value = None
    
    with pytest.raises(ValueError) as excinfo:
        await spawn_agent(
            name="new_agent",
            instructions="You are a test agent",
            handoffs=["nonexistent_agent"]
        )
    
    assert "Agent not found for handoff" in str(excinfo.value)
