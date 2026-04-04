"""
Application configuration management.

This module handles loading and validation of application settings from environment
variables. It uses Pydantic for type validation and provides a centralized settings
object that can be imported throughout the application.

Environment variables are loaded from a .env file in development, and from the
system environment in production deployments.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from a local .env file for development
# This allows sensitive configuration to be kept out of version control
# In production, environment variables should be set by the deployment platform
load_dotenv()


class Settings(BaseModel):
    """
    Application configuration model.

    All configuration values are validated and converted to appropriate types.
    Default values are provided for optional settings.
    """

    # OpenAI API credentials - required for LLM functionality
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Model selection - defaults to a cost-effective model for development
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Logging verbosity - controls both file and console output levels
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


# Create a singleton settings instance that can be imported across the application
# This ensures consistent configuration access and allows for runtime config changes
settings = Settings()
