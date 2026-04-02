from openai import OpenAI
from app.config import settings

# Initialize a reusable OpenAI client with credentials loaded from the application configuration
client = OpenAI(api_key=settings.openai_api_key)