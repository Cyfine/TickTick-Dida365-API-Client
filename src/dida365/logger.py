"""Simple logging configuration for debug output."""
import logging
import sys
from typing import Optional


# Create logger
logger = logging.getLogger("dida365")


def setup_logging(
    level: str = "INFO",
    log_format: str = "%(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    log_file: Optional[str] = None,
) -> None:
    """Configure logging for the package.
    
    Args:
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format string for log messages
        date_format: Format string for timestamps
        log_file: Optional file path to write logs to
    """
    # Remove any existing handlers
    logger.handlers.clear()
    
    # Set log level
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatters
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to setup file logging to {log_file}: {e}")


# Set default logging configuration
setup_logging() 