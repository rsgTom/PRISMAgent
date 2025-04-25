"""Formatter classes for the logging system."""

import json
import logging
import datetime
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Formatter that outputs JSON formatted logs.
    
    Useful for structured logging that can be easily parsed by log aggregation tools.
    """
    
    def __init__(self, include_context: bool = True):
        """Initialize the JSON formatter.
        
        Args:
            include_context: Whether to include context data in the logs
        """
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as JSON.
        
        Args:
            record: The log record to format
            
        Returns:
            A JSON string representation of the log record
        """
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "path": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add context data if available and enabled
        if self.include_context and hasattr(record, "context") and record.context:
            log_data["context"] = record.context
            
        # Add any extra attributes set with extra={} when logging
        for key, value in record.__dict__.items():
            if key not in {
                "args", "asctime", "created", "exc_info", "exc_text", 
                "filename", "funcName", "id", "levelname", "levelno", 
                "lineno", "module", "msecs", "message", "msg", "name", 
                "pathname", "process", "processName", "relativeCreated", 
                "stack_info", "thread", "threadName", "context"
            }:
                log_data[key] = value
        
        return json.dumps(log_data)
    
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        """Format the time of the record creation.
        
        Args:
            record: The log record
            datefmt: The date format string (unused in this implementation)
            
        Returns:
            ISO 8601 formatted timestamp
        """
        return datetime.datetime.fromtimestamp(
            record.created, datetime.timezone.utc
        ).isoformat()


class ContextAwareFormatter(logging.Formatter):
    """Standard formatter that can include context data in the log message."""
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, 
                 include_context: bool = True):
        """Initialize the context-aware formatter.
        
        Args:
            fmt: The format string
            datefmt: The date format string
            include_context: Whether to include context data in the logs
        """
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the record with optional context data.
        
        Args:
            record: The log record to format
            
        Returns:
            The formatted log message with optional context data
        """
        formatted = super().format(record)
        
        # Add context data if available and enabled
        if self.include_context and hasattr(record, "context") and record.context:
            context_str = " | Context: " + ", ".join(
                f"{k}={v}" for k, v in record.context.items()
            )
            formatted += context_str
            
        return formatted


def get_formatter(format_spec: str, include_context: bool = True) -> logging.Formatter:
    """Get a formatter based on the format specification.
    
    Args:
        format_spec: The format specification, either a format string or "json"
        include_context: Whether to include context data in the logs
        
    Returns:
        An appropriate formatter for the given format specification
    """
    if format_spec.lower() == "json":
        return JsonFormatter(include_context=include_context)
    elif format_spec.lower() == "default":
        # Use a standard format string
        return ContextAwareFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            include_context=include_context
        )
    else:
        return ContextAwareFormatter(fmt=format_spec, include_context=include_context) 