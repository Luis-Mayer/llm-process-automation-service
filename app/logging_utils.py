"""
Logging configuration and setup.

This module provides centralized logging configuration for the application.
It sets up both console and file logging with consistent formatting and
appropriate log levels. The logger is designed to be thread-safe and
handles log rotation implicitly through Python's logging module.
"""

import logging
from pathlib import Path

from app.config import settings


def setup_logger() -> logging.Logger:
    """
    Configure and return the application logger.

    This function creates a logger with the following characteristics:
    - Logs to both console and file
    - Uses configurable log levels from settings
    - Prevents duplicate handlers on reload (important for development)
    - Creates log directories automatically
    - Uses structured formatting for better readability

    Returns:
        logging.Logger: Configured logger instance for the application
    """
    # Ensure the logs directory exists before creating file handler
    # This prevents FileNotFoundError when the app starts
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Get or create the application logger with a unique name
    # Using a specific name prevents conflicts with other loggers
    logger = logging.getLogger("llm_process_automation")

    # Set log level from configuration, with fallback to INFO
    # This allows runtime configuration of verbosity
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Prevent duplicate handlers when the app reloads during development
    # This is common with FastAPI's auto-reload feature
    if not logger.handlers:
        # Define a consistent log format across all outputs
        # Includes timestamp, level, logger name, and message
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

        # Console handler for development and debugging
        # Outputs are color-coded by most terminals
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handler for persistent logging and production monitoring
        file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        file_handler.setFormatter(formatter)

        # Attach both handlers to enable simultaneous console and file logging
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
