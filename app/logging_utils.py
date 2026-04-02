import logging
from app.config import settings


def setup_logger() -> logging.Logger:
    """Configure and return the application logger."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # Return a named logger so log messages can be traced back to this service.
    return logging.getLogger("llm_process_automation")