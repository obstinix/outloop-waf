"""
Logging Utilities

Centralized logging configuration for the WAF application.
Provides structured logging with configurable levels and formats.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class WAFFormatter(logging.Formatter):
    """Custom formatter for WAF log messages."""
    
    FORMATS = {
        logging.DEBUG: "\033[36m%(levelname)s\033[0m | %(name)s | %(message)s",
        logging.INFO: "\033[32m%(levelname)s\033[0m | %(name)s | %(message)s",
        logging.WARNING: "\033[33m%(levelname)s\033[0m | %(name)s | %(message)s",
        logging.ERROR: "\033[31m%(levelname)s\033[0m | %(name)s | %(message)s",
        logging.CRITICAL: "\033[1;31m%(levelname)s\033[0m | %(name)s | %(message)s",
    }
    
    def format(self, record):
        """Format log record with color coding."""
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class StructuredFormatter(logging.Formatter):
    """JSON-structured formatter for production environments."""
    
    def format(self, record):
        """Format log record as JSON structure."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Simple JSON-like format without external dependencies
        parts = [f'"{k}": "{v}"' for k, v in log_data.items()]
        return "{" + ", ".join(parts) + "}"


_loggers: dict = {}
_configured: bool = False


def configure_logging(
    level: int = logging.INFO,
    structured: bool = False
) -> None:
    """
    Configure global logging settings.
    
    Args:
        level: Logging level (default: INFO)
        structured: Use JSON structured format (default: False)
    """
    global _configured
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Set formatter
    if structured:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(WAFFormatter())
    
    root_logger.addHandler(console_handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    global _configured
    
    if not _configured:
        configure_logging()
    
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    
    return _loggers[name]
