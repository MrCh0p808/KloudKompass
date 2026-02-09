# bashcloud/utils/logger.py
# --------------------------
# Centralized logging so debug mode can be toggled from the CLI.
# By default we only show warnings and errors. Debug mode shows everything.

import logging
import sys
from typing import Optional


# Module-level state for debug mode
_debug_mode = False

# Creates a named logger so all bashcloud modules use the same one
_logger = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get the BashCloud logger.
    
    a single logger for the whole package ensures all log messages
    are consistently formatted and respect the debug mode setting.
    
    Args:
        name: Optional sublogger name, e.g. "bashcloud.aws.cost"
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = logging.getLogger("bashcloud")
        _configure_logger(_logger)
    
    if name:
        return logging.getLogger(name)
    
    return _logger


def _configure_logger(logger: logging.Logger) -> None:
    """
    Set up the logger with our preferred format.
    
    Uses a simple format that shows level and message. In debug mode
    it also shows the module name for tracing.
    """
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    
    # Set format based on debug mode
    if _debug_mode:
        formatter = logging.Formatter(
            "[%(levelname)s] %(name)s: %(message)s"
        )
        logger.setLevel(logging.DEBUG)
    else:
        formatter = logging.Formatter(
            "[%(levelname)s] %(message)s"
        )
        logger.setLevel(logging.WARNING)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def set_debug_mode(enabled: bool) -> None:
    """
    Toggle debug mode for the logger.
    
    Called from CLI when --debug flag is passed. It reconfigures
    the logger to show debug level messages.
    """
    global _debug_mode, _logger
    
    _debug_mode = enabled
    
    if _logger is not None:
        _configure_logger(_logger)
    else:
        _logger = get_logger()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return _debug_mode


def debug(message: str, *args, **kwargs) -> None:
    """Log a debug message."""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    """Log an info message."""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs) -> None:
    """Log a warning message."""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs) -> None:
    """Log an error message."""
    get_logger().error(message, *args, **kwargs)
