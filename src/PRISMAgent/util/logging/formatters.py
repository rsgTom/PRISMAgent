"""Custom formatters for logging."""

import inspect
import json
import logging
from typing import Any, Dict

from .context import _get_context


class ContextFilter(logging.Filter):
    """Filter that adds context information to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to the log record."""
        context = _get_context()
        for key, value in context.items():
            setattr(record, key, value)
        
        # Add request_id if not present
        if not hasattr(record, "request_id") and context.get("request_id"):
            record.request_id = context.get("request_id")
        
        # Add caller information
        if not hasattr(record, "caller"):
            frame = inspect.currentframe()
            # Go back 2 frames to get the caller of the logging function
            if frame:
                try:
                    frame = frame.f_back
                    if frame:
                        frame = frame.f_back
                        if frame:
                            caller = f"{frame.f_globals['__name__']}:{frame.f_lineno}"
                            record.caller = caller
                except (AttributeError, KeyError):
                    record.caller = "unknown"
            else:
                record.caller = "unknown"
        
        return True


class JsonFormatter(logging.Formatter):
    """Formatter that outputs log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add context data if present
        context = _get_context()
        if context:
            log_data["context"] = dict(context)
        
        # Add any other attributes from the record
        for key, value in record.__dict__.items():
            if key not in ("args", "asctime", "created", "exc_info", "exc_text", 
                          "filename", "funcName", "id", "levelname", "levelno",
                          "lineno", "module", "msecs", "message", "msg", 
                          "name", "pathname", "process", "processName", 
                          "relativeCreated", "stack_info", "thread", "threadName"):
                log_data[key] = value
        
        return json.dumps(log_data) 