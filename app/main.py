"""
FastAPI application for LLM-powered process automation.

This module defines the REST API endpoints for extracting structured process
information from natural language descriptions using OpenAI's LLM models.
"""

from fastapi import Body, FastAPI, HTTPException

from app.logging_utils import setup_logger
from app.schemas import ProcessRequest, ProcessResponse
from app.service import extract_process_with_llm
from app.storage import save_extraction_result

# Initialize structured logging for the application
# Logs are written to both console and file for debugging and monitoring
logger = setup_logger()

# Create FastAPI application instance with metadata
app = FastAPI(
    title="LLM Process Automation Service",
    version="0.1.0",
    description="API for extracting structured process information from unstructured text.",
)


@app.get("/health")
def health_check() -> dict:
    """
    Health check endpoint for monitoring service availability.

    Returns:
        dict: Status response with "ok" status
    """
    logger.info("Health check called")
    return {"status": "ok"}


@app.post("/extract", response_model=ProcessResponse)
def extract_process(request: ProcessRequest) -> ProcessResponse:
    """
    Extract structured process information from a JSON request.

    This endpoint accepts a structured request with optional process name
    and required description, then uses LLM to extract comprehensive process
    information including steps, roles, inputs, outputs, risks, and gaps.

    Args:
        request: ProcessRequest containing process_name and description

    Returns:
        ProcessResponse: Structured process representation with all extracted fields

    Raises:
        HTTPException: 500 error if LLM extraction fails
    """
    logger.info("Received extraction request for process_name=%s", request.process_name)

    try:
        # Call the core LLM extraction service
        result = extract_process_with_llm(request)

        # Persist the request/response pair for debugging and evaluation
        # This creates audit trails and enables offline analysis
        artifact_path = save_extraction_result(
            request_data=request.model_dump(),
            response_data=result.model_dump(),
        )

        logger.info("Extraction successful. Saved artifact to %s", artifact_path)
        return result

    except Exception as exc:
        # Log full exception details for debugging while returning user-friendly error
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(exc)}")


@app.post("/extract-text", response_model=ProcessResponse)
def extract_process_from_text(
    description: str = Body(..., media_type="text/plain"),
) -> ProcessResponse:
    """
    Extract structured process information from plain text input.

    Alternative endpoint that accepts raw text instead of JSON. Internally
    converts the text to a ProcessRequest and uses the same extraction logic.

    Args:
        description: Plain text process description (minimum 20 characters)

    Returns:
        ProcessResponse: Structured process representation

    Raises:
        HTTPException: 500 error if extraction fails
    """
    logger.info("Received plain text extraction request")

    try:
        # Convert plain text to structured request format
        # Process name is set to None, letting the LLM infer it from text
        request = ProcessRequest(process_name=None, description=description)
        result = extract_process_with_llm(request)

        # Save artifacts for consistency with JSON endpoint
        artifact_path = save_extraction_result(
            request_data=request.model_dump(),
            response_data=result.model_dump(),
        )

        logger.info("Plain text extraction successful. Saved artifact to %s", artifact_path)
        return result

    except Exception as exc:
        logger.exception("Plain text extraction failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(exc)}")
