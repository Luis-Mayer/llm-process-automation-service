"""
OpenAI client configuration and initialization.

This module provides a centralized OpenAI client instance that can be imported
and used throughout the application. It ensures consistent API key management
and client configuration across all LLM interactions.
"""

from openai import OpenAI

from app.config import settings

# Initialize a reusable OpenAI client with credentials loaded from the application configuration
# This client is thread-safe and can be used concurrently across multiple requests
client = OpenAI(api_key=settings.openai_api_key)
