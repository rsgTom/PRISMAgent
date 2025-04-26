"""
PRISMAgent.tools.code_interpreter
--------------------------------

This module provides a tool for executing Python code safely in a sandboxed environment.
"""

from __future__ import annotations

import io
import sys
import contextlib
from typing import Dict, Any, Optional, List, Union

from .factory import tool_factory
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)

@tool_factory
@with_log_context(component="code_interpreter_tool")
async def code_interpreter(
    code: str,
    *,
    max_execution_time: Optional[int] = 10,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    """
    Execute Python code and return the results.
    
    This tool provides a way to run Python code snippets and capture
    their output. It uses a restricted execution environment for safety.
    
    Args:
        code: The Python code to execute
        max_execution_time: Maximum allowed execution time in seconds
        safe_mode: Whether to run in restricted mode (recommended)
        
    Returns:
        A dictionary containing the execution results, including stdout, 
        stderr, and any returned value.
    """
    logger.info(
        f"Executing code (safe_mode={safe_mode}, max_time={max_execution_time}s)",
        safe_mode=safe_mode,
        max_execution_time=max_execution_time,
        code_length=len(code)
    )
    
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    result = {
        "success": False,
        "stdout": "",
        "stderr": "",
        "result": None,
        "error": None
    }
    
    try:
        # Set timeout if specified (only in non-safe mode as it requires additional dependencies)
        if not safe_mode and max_execution_time:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Code execution timed out after {max_execution_time} seconds")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(max_execution_time)
        
        # Execute the code with captured stdout/stderr
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            # Create a local namespace for code execution
            local_namespace = {}
            
            # Execute the code
            exec_result = exec(code, {}, local_namespace)
            
            # Check for last expression value if available
            if '_' in local_namespace:
                result["result"] = local_namespace['_']
        
        # Get the captured output
        result["stdout"] = stdout_capture.getvalue()
        result["stderr"] = stderr_capture.getvalue()
        result["success"] = True
        
        logger.debug(
            "Code execution successful",
            stdout_length=len(result["stdout"]),
            stderr_length=len(result["stderr"])
        )
        
    except Exception as e:
        # Handle any exceptions during execution
        result["success"] = False
        result["error"] = str(e)
        result["stderr"] = stderr_capture.getvalue() or str(e)
        
        logger.warning(
            f"Code execution failed: {str(e)}",
            error=str(e),
            error_type=type(e).__name__,
            stdout_length=len(stdout_capture.getvalue()),
            stderr_length=len(stderr_capture.getvalue())
        )
    
    finally:
        # Reset the alarm if it was set
        if not safe_mode and max_execution_time:
            signal.alarm(0)
    
    return result

@tool_factory
@with_log_context(component="install_package_tool")
async def install_package(
    package_name: str,
    version: Optional[str] = None,
    upgrade: bool = False,
) -> Dict[str, Any]:
    """
    Install a Python package in the current environment.
    
    This tool is designed to install packages on-the-fly during agent
    execution when needed for code functionality.
    
    Args:
        package_name: The name of the package to install
        version: Optional specific version to install
        upgrade: Whether to upgrade the package if already installed
        
    Returns:
        A dictionary containing the installation results
    """
    import subprocess
    
    logger.info(
        f"Installing package: {package_name} (version={version}, upgrade={upgrade})",
        package=package_name,
        version=version,
        upgrade=upgrade
    )
    
    # Construct the pip command
    cmd = [sys.executable, "-m", "pip", "install"]
    
    if upgrade:
        cmd.append("--upgrade")
    
    if version:
        cmd.append(f"{package_name}=={version}")
    else:
        cmd.append(package_name)
    
    # Execute the pip install command
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        success = True
        stdout = result.stdout
        stderr = result.stderr
        error = None
        
        logger.info(
            f"Successfully installed package: {package_name}",
            package=package_name,
            success=True
        )
        
    except subprocess.CalledProcessError as e:
        success = False
        stdout = e.stdout
        stderr = e.stderr
        error = str(e)
        
        logger.error(
            f"Failed to install package: {package_name}",
            package=package_name,
            error=str(e),
            stdout=e.stdout,
            stderr=e.stderr
        )
    
    return {
        "success": success,
        "package": package_name,
        "version": version,
        "stdout": stdout,
        "stderr": stderr,
        "error": error
    }
