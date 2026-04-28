"""
agent_audit.logging_config — Logging Configuration
===================================================

Centralized logging configuration for the agent_audit library.

Usage:
    from agent_audit.logging_config import setup_logging
    
    # Basic setup (INFO level)
    setup_logging()
    
    # Debug mode (DEBUG level)
    setup_logging(level="DEBUG")
    
    # Custom format
    setup_logging(level="INFO", format="%(message)s")
"""

import logging
import sys
from typing import Literal


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
    format: str | None = None,
    include_timestamp: bool = True,
) -> None:
    """
    Configure logging for the agent_audit library.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
        format: Custom format string. If None, uses default format.
        include_timestamp: Whether to include timestamps in log messages.
    
    Example:
        >>> setup_logging(level="DEBUG")
        >>> # Now all agent_audit logs will be visible at DEBUG level
    """
    # Default format
    if format is None:
        if include_timestamp:
            format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        else:
            format = "[%(levelname)s] %(name)s: %(message)s"
    
    # Configure root logger for agent_audit
    logger = logging.getLogger("agent_audit")
    logger.setLevel(getattr(logging, level))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Add console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level))
    
    # Set format
    formatter = logging.Formatter(format, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(f"Logging configured at {level} level")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (typically __name__).
    
    Returns:
        Configured logger instance.
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    return logging.getLogger(name)


def disable_logging() -> None:
    """Disable all agent_audit logging."""
    logger = logging.getLogger("agent_audit")
    logger.setLevel(logging.CRITICAL + 1)
    logger.info("Logging disabled")


def enable_debug_mode() -> None:
    """Quick helper to enable debug mode."""
    setup_logging(level="DEBUG")
