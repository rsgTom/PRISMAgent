"""
Unit tests for the PRISMAgent logging system.
"""

import io
import logging
import os
import sys
import unittest
from unittest.mock import patch

import pytest

from PRISMAgent.util.logging import (
    Logger,
    LoggingConfig,
    LogHandlerConfig,
    LogLevel,
    get_logger,
    log_context,
    with_log_context,
    init_request_context,
    clear_request_context,
    configure_root_logger,
)


class TestLogging(unittest.TestCase):
    """Tests for the logging system."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset root logger
        root_logger = logging.getLogger()
        root_logger.handlers = []
        
        # Capture logs
        self.log_output = io.StringIO()
        handler = logging.StreamHandler(self.log_output)
        handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)
    
    def test_get_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test")
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, "test")
    
    def test_logger_levels(self):
        """Test that logger levels work correctly."""
        logger = get_logger("test_levels")
        
        # Test all log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        log_content = self.log_output.getvalue()
        self.assertIn("DEBUG:test_levels:Debug message", log_content)
        self.assertIn("INFO:test_levels:Info message", log_content)
        self.assertIn("WARNING:test_levels:Warning message", log_content)
        self.assertIn("ERROR:test_levels:Error message", log_content)
        self.assertIn("CRITICAL:test_levels:Critical message", log_content)
    
    def test_context_logging(self):
        """Test context-based logging."""
        logger = get_logger("test_context")
        
        # Use log_context context manager
        with log_context(user_id="123", action="login"):
            logger.info("User logged in")
        
        # Check that context was included in the log
        log_content = self.log_output.getvalue()
        self.assertIn("INFO:test_context:User logged in", log_content)
    
    def test_log_context_decorator(self):
        """Test logging context decorator."""
        logger = get_logger("test_decorator")
        
        @with_log_context(component="auth")
        def test_function():
            logger.info("Function called")
        
        test_function()
        
        log_content = self.log_output.getvalue()
        self.assertIn("INFO:test_decorator:Function called", log_content)
    
    def test_request_context(self):
        """Test request context functionality."""
        logger = get_logger("test_request")
        
        # Initialize request context
        request_id = init_request_context(session_id="abc123")
        logger.info("Processing request")
        
        # Check that request_id was generated and used
        log_content = self.log_output.getvalue()
        self.assertIn("INFO:test_request:Processing request", log_content)
        
        # Clear request context
        clear_request_context()
    
    def test_custom_config(self):
        """Test custom logging configuration."""
        # Create custom config
        config = LoggingConfig(
            level=LogLevel.DEBUG,
            handlers=[
                LogHandlerConfig(
                    type="console",
                    level=LogLevel.DEBUG,
                    format="default"
                )
            ]
        )
        
        # Configure root logger with custom config
        configure_root_logger(config)
        
        # Test logging
        logger = get_logger("test_custom_config", config)
        logger.debug("Custom debug message")
        
        log_content = self.log_output.getvalue()
        self.assertIn("DEBUG:test_custom_config:Custom debug message", log_content)


if __name__ == "__main__":
    unittest.main()
