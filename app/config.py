import os

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from a local .env file 
# so configuration can be managed outside the source 
# code.
load_dotenv()


class Settings(BaseModel):
    """Application configuration loaded from environment variables."""

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


# Create a single settings instance that can be imported across the app.
settings = Settings()
