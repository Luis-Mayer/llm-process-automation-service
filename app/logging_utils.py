import logging
from pathlib import Path

from app.config import settings


def setup_logger() -> logging.Logger:
    # Create a local directory for log files if it does not exist yet
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create or retrieve the application logger
    logger = logging.getLogger("llm_process_automation")

    # Set the log level from the config, defaulting to INFO if invalid
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Avoid adding duplicate handlers when the app reloads
    if not logger.handlers:
        # Define a shared log message format
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

        # Log messages to the console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Log messages to a file inside the logs directory
        file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        file_handler.setFormatter(formatter)

        # Attach both handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
