"""
Tests for PRISMAgent.util.error_handling module.

This test suite covers the error handling utilities and decorators.
"""

import pytest
from unittest.mock import MagicMock, patch

from PRISMAgent.util.exceptions import (
    PRISMAgentError,
    ValidationError,
    ConfigurationError,
    ExecutionError,
    ToolError
)
from PRISMAgent.util.error_handling import (
    handle_exceptions,
    error_context,
    validate_or_raise,
    format_exception_with_context
)


class TestHandleExceptionsDecorator:
    """Test the handle_exceptions decorator."""
    
    def test_successful_execution(self):
        """Test that the decorator passes through successful execution."""
        @handle_exceptions()
        def successful_function():
            return "success"
        
        assert successful_function() == "success"
    
    def test_passing_arguments(self):
        """Test that the decorator properly passes arguments."""
        @handle_exceptions()
        def function_with_args(a, b, *, c=None):
            return a + b + (c or 0)
        
        assert function_with_args(1, 2) == 3
        assert function_with_args(1, 2, c=3) == 6
    
    def test_reraise_prismagent_error(self):
        """Test that PRISMAgentError exceptions are re-raised directly."""
        @handle_exceptions()
        def function_raising_prismagent_error():
            raise PRISMAgentError("Test error")
        
        with pytest.raises(PRISMAgentError) as excinfo:
            function_raising_prismagent_error()
        
        assert "Test error" in str(excinfo.value)
        assert not hasattr(excinfo.value, "function")  # Should not add metadata
    
    def test_convert_standard_exceptions(self):
        """Test that standard exceptions are converted to PRISMAgentError."""
        @handle_exceptions()
        def function_raising_value_error():
            raise ValueError("Invalid value")
        
        with pytest.raises(PRISMAgentError) as excinfo:
            function_raising_value_error()
        
        assert "Invalid value" in str(excinfo.value)
        assert "function_raising_value_error" in excinfo.value.details["function"]
    
    def test_error_mapping(self):
        """Test that exceptions are mapped to the specified error classes."""
        error_map = {
            ValueError: ValidationError,
            FileNotFoundError: ConfigurationError,
            RuntimeError: ExecutionError
        }
        
        @handle_exceptions(error_map=error_map)
        def function_raising_mapped_errors(error_type):
            if error_type == "value":
                raise ValueError("Invalid value")
            elif error_type == "file":
                raise FileNotFoundError("File not found")
            elif error_type == "runtime":
                raise RuntimeError("Runtime error")
            else:
                raise KeyError("Unknown key")  # Not in the map
        
        # Test ValueError → ValidationError
        with pytest.raises(ValidationError) as excinfo:
            function_raising_mapped_errors("value")
        
        # Test FileNotFoundError → ConfigurationError
        with pytest.raises(ConfigurationError) as excinfo:
            function_raising_mapped_errors("file")
        
        # Test RuntimeError → ExecutionError
        with pytest.raises(ExecutionError) as excinfo:
            function_raising_mapped_errors("runtime")
        
        # Test unmapped exception → default error class
        with pytest.raises(PRISMAgentError) as excinfo:
            function_raising_mapped_errors("other")
    
    def test_custom_default_error_class(self):
        """Test using a custom default error class."""
        @handle_exceptions(default_error_class=ToolError)
        def function_raising_unmapped_error():
            raise KeyError("Unknown key")
        
        with pytest.raises(ToolError) as excinfo:
            function_raising_unmapped_error()
    
    @patch("PRISMAgent.util.error_handling.logger")
    def test_logging(self, mock_logger):
        """Test that exceptions are logged correctly."""
        @handle_exceptions(log_level="error", include_traceback=True)
        def function_that_logs():
            raise ValueError("This should be logged")
        
        with pytest.raises(PRISMAgentError):
            function_that_logs()
        
        # Check that logger.error was called
        mock_logger.error.assert_called_once()
        
        # Check log message contains function name and error
        log_call_args = mock_logger.error.call_args[0]
        assert "function_that_logs" in log_call_args[0]
        assert "This should be logged" in log_call_args[0]
        
        # Check exc_info is True for traceback inclusion
        log_call_kwargs = mock_logger.error.call_args[1]
        assert log_call_kwargs["exc_info"] is True


class TestErrorContext:
    """Test the error_context context manager."""
    
    def test_successful_execution(self):
        """Test that successful code executes normally."""
        with error_context("Context message"):
            result = "success"
        
        assert result == "success"
    
    def test_reraise_prismagent_error_with_context(self):
        """Test that PRISMAgentError exceptions are enhanced with context."""
        with pytest.raises(PRISMAgentError) as excinfo:
            with error_context("During configuration"):
                raise PRISMAgentError("Test error")
        
        assert "During configuration: Test error" in str(excinfo.value)
    
    def test_convert_standard_exceptions_with_context(self):
        """Test that standard exceptions are converted with context."""
        with pytest.raises(PRISMAgentError) as excinfo:
            with error_context("While loading file"):
                raise FileNotFoundError("config.yaml")
        
        assert "While loading file" in str(excinfo.value)
        assert "config.yaml" in str(excinfo.value)
    
    def test_error_mapping_with_context(self):
        """Test that exceptions are mapped with context information."""
        error_map = {
            ValueError: ValidationError,
            FileNotFoundError: ConfigurationError
        }
        
        with pytest.raises(ValidationError) as excinfo:
            with error_context(
                "Validating input", 
                error_map=error_map,
                context_details={"field": "username"}
            ):
                raise ValueError("Must be alphanumeric")
        
        assert "Validating input" in str(excinfo.value)
        assert "Must be alphanumeric" in str(excinfo.value)
        assert "field" in excinfo.value.details


class TestValidateOrRaise:
    """Test the validate_or_raise utility function."""
    
    def test_valid_condition(self):
        """Test that validate_or_raise doesn't raise for true conditions."""
        # This should not raise
        validate_or_raise(True, "This error should not appear")
    
    def test_invalid_condition(self):
        """Test that validate_or_raise raises ValidationError for false conditions."""
        with pytest.raises(ValidationError) as excinfo:
            validate_or_raise(False, "Validation failed", "test_field")
        
        assert "Validation error for field 'test_field'" in str(excinfo.value)
        assert "Validation failed" in str(excinfo.value)
    
    def test_custom_error_class(self):
        """Test using a custom error class."""
        with pytest.raises(ConfigurationError) as excinfo:
            validate_or_raise(
                False, 
                "Configuration invalid", 
                error_class=ConfigurationError
            )
        
        assert isinstance(excinfo.value, ConfigurationError)
        assert "Configuration invalid" in str(excinfo.value)
    
    def test_with_details(self):
        """Test providing additional details."""
        with pytest.raises(ValidationError) as excinfo:
            validate_or_raise(
                False, 
                "Value out of range", 
                "amount",
                details={"min": 0, "max": 100, "actual": 150}
            )
        
        assert "actual" in excinfo.value.details
        assert excinfo.value.details["actual"] == 150


class TestFormatExceptionWithContext:
    """Test the format_exception_with_context utility function."""
    
    def test_format_exception(self):
        """Test formatting an exception with context."""
        try:
            # Cause an exception
            1 / 0
        except Exception:
            # Format the exception with context
            result = format_exception_with_context(
                context={"operation": "division", "value": 0}
            )
            
            # Check result
            assert "ZeroDivisionError" in result
            assert "Context:" in result
            assert "operation: division" in result
            assert "value: 0" in result
