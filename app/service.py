from app.config import settings
from app.openai_client import client
from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas import ProcessRequest, ProcessResponse

# JSON schema used to enforce a structured LLM response format.
# This ensures the LLM returns a consistent process representation 
# that can be validated against the Pydantic response model.
PROCESS_RESPONSE_SCHEMA = {
    "name": "process_extraction",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "process_name": {"type": "string"},
            "summary": {"type": "string"},
            "roles": {"type": "array", "items": {"type": "string"}},
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "actor": {"type": "string"},
                        "action": {"type": "string"},
                        "condition": {"type": ["string", "null"]},
                    },
                    "required": ["id", "actor", "action", "condition"],
                    "additionalProperties": False,
                },
            },
            "decision_points": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "condition": {"type": "string"},
                        "true_branch": {"type": "string"},
                        "false_branch": {"type": "string"},
                    },
                    "required": ["condition", "true_branch", "false_branch"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["process_name", "summary", "roles", "steps", "decision_points"],
        "additionalProperties": False,
    },
}


def extract_process_with_llm(request: ProcessRequest) -> ProcessResponse:
    """Generate a structured process representation from 
    a natural-language description using the OpenAI API."""

    # Send the system instruction and the user-specific process description 
    # to the model, while enforcing a strict JSON schema for the response.
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_prompt(
                    process_name=request.process_name, description=request.description
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": PROCESS_RESPONSE_SCHEMA["name"],
                "strict": PROCESS_RESPONSE_SCHEMA["strict"],
                "schema": PROCESS_RESPONSE_SCHEMA["schema"],
            }
        },
    )

    # Validate the structured model output against the Pydantic response schema 
    # before returning it to the API layer.
    output_text = response.output_text
    return ProcessResponse.model_validate_json(output_text)
