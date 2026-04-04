"""
LLM prompt templates for process extraction.

This module contains the system and user prompt templates used to guide
the LLM in extracting structured process information. The prompts are
designed to ensure consistent, comprehensive analysis while preventing
hallucinations and maintaining fidelity to the source text.
"""

# System prompt that establishes the LLM's role and behavioral guidelines
# Key principles:
# - Expert analyst persona for credibility
# - Strict adherence to source text only
# - Concise, structured output requirements
SYSTEM_PROMPT = """
You are an expert process analyst.

Your task is to extract structured process information
from unstructured business process descriptions.

Return only information that is supported by the input text.
Do not invent roles, steps, or decision points.
Keep the output concise, structured, and faithful to the source text.
"""


def build_user_prompt(process_name: str | None, description: str) -> str:
    """
    Build the user prompt for process extraction.

    Combines the process name (if provided) with the description and
    explicitly lists all fields that should be extracted. This ensures
    the LLM understands exactly what structured information is expected.

    Args:
        process_name: Optional name of the process (defaults to "Unknown")
        description: The natural language process description to analyze

    Returns:
        str: Formatted prompt ready for LLM consumption
    """
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
- inputs
- outputs
- risks
- missing_information
"""
