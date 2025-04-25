#!/usr/bin/env python
"""
Logging Example
--------------

This example demonstrates the PRISMAgent logging system.
"""

import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the PRISMAgent package
from PRISMAgent.util import (
    clear_request_context,
    get_logger,
    init_request_context,
    log_context,
    with_log_context,
)

# Create a logger
logger = get_logger(__name__)

# Basic logging
logger.info("This is an info message")
logger.debug("This is a debug message that may not show depending on log level")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Using context
with log_context(user_id="example_user", action="demo"):
    logger.info("This log has context information")
    
    # Nested context
    with log_context(sub_action="nested"):
        logger.info("This log has additional nested context")

# Using context decorator
@with_log_context(component="example")  # type: ignore
def example_function(arg1: str) -> str:
    logger.info("Calling example function", arg1=arg1)
    return arg1

example_function("test")

# Using request context
request_id = init_request_context(user_agent="Example/1.0", user_ip="127.0.0.1")
logger.info("This log includes request context", request_id=request_id)
clear_request_context()

# Demonstrate passing additional context in log calls
logger.info("Processing item", item_id="12345", status="complete")

print("\nLogging example complete!")
print(f"Check the logs directory for log files: {Path('logs').absolute()}") 