"""Unit tests for PRISMAgent tool_factory."""

import inspect
from typing import Dict, List, Optional

import pytest

from PRISMAgent.tools.factory import tool_factory, list_available_tools


def test_tool_factory_basic():
    """Test basic functionality of tool_factory."""
    
    def sample_func(param1: str, param2: int = 42) -> Dict:
        """Sample function for testing."""
        return {"param1": param1, "param2": param2}
    
    # Apply tool_factory
    wrapped = tool_factory(sample_func)
    
    # Check that it's properly decorated
    assert hasattr(wrapped, "__agents_tool__")
    assert wrapped.__agents_tool__ is True
    
    # Check that PRISMAgent metadata is added
    assert hasattr(wrapped, "__prism_tool__")
    assert wrapped.__prism_tool__ is True
    assert wrapped.__prism_name__ == "sample_func"
    assert "Sample function for testing" in wrapped.__prism_description__
    
    # Check parameter info
    assert "param1" in wrapped.__prism_params__
    assert wrapped.__prism_params__["param1"]["required"] is True
    assert "param2" in wrapped.__prism_params__
    assert wrapped.__prism_params__["param2"]["required"] is False
    assert wrapped.__prism_params__["param2"]["default"] == 42
    
    # Check that function still works
    result = wrapped("test", 10)
    assert result == {"param1": "test", "param2": 10}
    
    # Check with default parameter
    result = wrapped("test")
    assert result == {"param1": "test", "param2": 42}


def test_tool_factory_with_custom_name_description():
    """Test tool_factory with custom name and description."""
    
    def another_func(x: int) -> int:
        return x * 2
    
    custom_name = "custom_tool"
    custom_desc = "A special tool for testing"
    
    wrapped = tool_factory(
        another_func, 
        name=custom_name, 
        description=custom_desc
    )
    
    assert wrapped.__prism_name__ == custom_name
    assert wrapped.__prism_description__ == custom_desc
    
    # Check that function works
    assert wrapped(5) == 10


def test_list_available_tools(monkeypatch):
    """Test list_available_tools function.
    
    This test uses monkeypatch to simulate tools modules.
    """
    # Mock the module discovery
    def mock_iter_modules(paths):
        # Return some fake modules
        return [
            (None, "mock_tool1", None),
            (None, "mock_tool2", None),
            (None, "__init__", None),
            (None, "factory", None),
        ]
    
    # Mock the import_module function
    def mock_import_module(name):
        class MockModule:
            def __dir__(self):
                if "mock_tool1" in name:
                    return ["tool_a", "tool_b", "not_a_tool"]
                else:
                    return ["tool_c"]
                
            def __getattr__(self, attr):
                if attr in ["tool_a", "tool_b", "tool_c"]:
                    # Create a callable with the __agents_tool__ attribute
                    def mock_tool(*args, **kwargs):
                        pass
                    mock_tool.__agents_tool__ = True
                    return mock_tool
                return None
        
        return MockModule()
    
    # Apply the monkeypatches
    import importlib
    from pkgutil import iter_modules
    monkeypatch.setattr(importlib, "import_module", mock_import_module)
    monkeypatch.setattr("pkgutil.iter_modules", mock_iter_modules)
    
    # Run the function
    tools = list_available_tools()
    
    # Check the results
    assert set(tools) == {"tool_a", "tool_b", "tool_c"}
