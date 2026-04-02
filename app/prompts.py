SYSTEM_PROMPT = """
You are an expert process analyst.

Your task is to extract structured process information 
from unstructured business process descriptions.

Return only information that is supported by the input text.
Do not invent roles, steps, or decision points.
Keep the output concise, structured, and faithful to the source text.
"""


def build_user_prompt(process_name: str | None, description: str) -> str:
    return f"""
Process name: {process_name or "Unknown"}

Process description:
{description}

Extract the process into a structured representation with:
- process_name
- summary
- roles
- steps
- decision_points
"""
