"""
Tests for the spawn tool.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from PRISMAgent.tools.spawn import spawn_agent


@pytest.mark.asyncio
async def test_spawn_agent_with_no_tools_or_handoffs():
    """Test spawn_agent with no tools or handoffs."""
    with patch('PRISMAgent.tools.spawn.list_available_tools', return_value=[]), \
         patch('PRISMAgent.tools.spawn.agent_factory') as mock_agent_factory:
        
        mock_agent = MagicMock()
        mock_agent.name = "test_agent"
        mock_agent_factory.return_value = mock_agent
        
        result = await spawn_agent("test_agent", "Test instructions")
        
        mock_agent_factory.assert_called_once_with(
            name="test_agent",
            instructions="Test instructions",
            tools=None,
            handoffs=None
        )
        
        assert result["id"] == "test_agent"
        assert result["status"] == "created"
        assert result["tools"] == []
        assert result["handoffs"] == []


@pytest.mark.asyncio
async def test_spawn_agent_with_handoffs():
    """Test spawn_agent with handoffs."""
    with patch('PRISMAgent.tools.spawn.list_available_tools', return_value=[]), \
         patch('PRISMAgent.tools.spawn.agent_factory') as mock_agent_factory, \
         patch('PRISMAgent.tools.spawn.registry_factory') as mock_registry_factory:
        
        # Mock registry
        mock_registry = AsyncMock()
        mock_registry_factory.return_value = mock_registry
        
        # Mock agent
        mock_handoff_agent = MagicMock()
        mock_handoff_agent.name = "handoff_agent"
        mock_registry.get_agent.return_value = mock_handoff_agent
        
        # Mock main agent
        mock_agent = MagicMock()
        mock_agent.name = "test_agent"
        mock_agent_factory.return_value = mock_agent
        
        result = await spawn_agent(
            "test_agent", 
            "Test instructions", 
            handoffs=["handoff_agent"]
        )
        
        mock_registry.get_agent.assert_called_once_with("handoff_agent")
        mock_agent_factory.assert_called_once_with(
            name="test_agent",
            instructions="Test instructions",
            tools=None,
            handoffs=[mock_handoff_agent]
        )
        
        assert result["id"] == "test_agent"
        assert result["status"] == "created"
        assert result["tools"] == []
        assert result["handoffs"] == ["handoff_agent"]


@pytest.mark.asyncio
async def test_spawn_agent_with_missing_handoff():
    """Test spawn_agent with a missing handoff agent."""
    with patch('PRISMAgent.tools.spawn.list_available_tools', return_value=[]), \
         patch('PRISMAgent.tools.spawn.registry_factory') as mock_registry_factory:
        
        # Mock registry
        mock_registry = AsyncMock()
        mock_registry_factory.return_value = mock_registry
        mock_registry.get_agent.return_value = None
        
        with pytest.raises(ValueError, match="Agent not found for handoff: missing_agent"):
            await spawn_agent(
                "test_agent", 
                "Test instructions", 
                handoffs=["missing_agent"]
            )
        
        mock_registry.get_agent.assert_called_once_with("missing_agent")


@pytest.mark.asyncio
async def test_spawn_agent_with_callable_tools():
    """Test spawn_agent with callable tools."""
    def dummy_tool():
        return "I'm a tool"
    
    with patch('PRISMAgent.tools.spawn.list_available_tools', return_value=[]), \
         patch('PRISMAgent.tools.spawn.agent_factory') as mock_agent_factory:
        
        mock_agent = MagicMock()
        mock_agent.name = "test_agent"
        mock_agent_factory.return_value = mock_agent
        
        result = await spawn_agent(
            "test_agent", 
            "Test instructions", 
            tools=[dummy_tool]
        )
        
        mock_agent_factory.assert_called_once_with(
            name="test_agent",
            instructions="Test instructions",
            tools=[dummy_tool],
            handoffs=None
        )
        
        assert result["id"] == "test_agent"
        assert result["status"] == "created"
        assert result["tools"] == ["dummy_tool"]
        assert result["handoffs"] == []


@pytest.mark.asyncio
async def test_spawn_agent_with_string_tools():
    """Test spawn_agent with string tool names."""
    with patch('PRISMAgent.tools.spawn.list_available_tools', return_value=["existing_tool"]), \
         patch('PRISMAgent.tools.spawn.import_module') as mock_import_module, \
         patch('PRISMAgent.tools.spawn.agent_factory') as mock_agent_factory:
        
        # Mock module
        mock_module = MagicMock()
        mock_tool = MagicMock()
        mock_tool.__name__ = "existing_tool"
        setattr(mock_module, "existing_tool", mock_tool)
        mock_import_module.return_value = mock_module
        
        # Mock agent
        mock_agent = MagicMock()
        mock_agent.name = "test_agent"
        mock_agent_factory.return_value = mock_agent
        
        result = await spawn_agent(
            "test_agent", 
            "Test instructions", 
            tools=["existing_tool"]
        )
        
        mock_import_module.assert_called_once_with("PRISMAgent.tools.existing_tool")
        mock_agent_factory.assert_called_once_with(
            name="test_agent",
            instructions="Test instructions",
            tools=[mock_tool],
            handoffs=None
        )
        
        assert result["id"] == "test_agent"
        assert result["status"] == "created"
        assert result["tools"] == ["existing_tool"]
        assert result["handoffs"] == []


@pytest.mark.asyncio
async def test_spawn_agent_with_invalid_tool_name():
    """Test spawn_agent with an invalid tool name."""
    with patch('PRISMAgent.tools.spawn.list_available_tools', return_value=[]):
        with pytest.raises(ValueError, match="Invalid tool name: invalid_tool"):
            await spawn_agent(
                "test_agent", 
                "Test instructions", 
                tools=["invalid_tool"]
            )


@pytest.mark.asyncio
async def test_spawn_agent_with_import_error():
    """Test spawn_agent with an import error."""
    with patch('PRISMAgent.tools.spawn.list_available_tools', return_value=["problematic_tool"]), \
         patch('PRISMAgent.tools.spawn.import_module', side_effect=ImportError("Module not found")):
        
        with pytest.raises(ValueError, match="Could not load tool module for: problematic_tool"):
            await spawn_agent(
                "test_agent", 
                "Test instructions", 
                tools=["problematic_tool"]
            )
