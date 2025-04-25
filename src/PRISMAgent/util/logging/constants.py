"""Constants for the logging system."""

import enum
import logging


class LogLevel(str, enum.Enum):
    """Log level enumeration with string values for configuration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def to_int(self) -> int:
        """Convert the log level string to its numeric value in the logging module."""
        return int(getattr(logging, self.value))


# Default format strings for different use cases
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
)
JSON_FORMAT = "json"  # Special marker for JSON formatting

# Mapping from string log levels to numeric values
LOG_LEVEL_MAP = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARNING: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.CRITICAL: logging.CRITICAL,
} 