from fastapi import FastAPI, HTTPException
from app.schemas import ProcessRequest, ProcessResponse
from app.logging_utils import setup_logger
from app.service import extract_process_with_llm

# Initialize the application logger
logger = setup_logger()

# Create the FastAPI application
app = FastAPI(
    title="LLM Process Automation Service",
    version="0.1.0",
    description="API for extracting structured process information from unstructured text.",
)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint used to verify that the service is running."""
    logger.info("Health check called")
    return {"status": "ok"}


@app.post("/extract", response_model=ProcessResponse)
def extract_process(request: ProcessRequest) -> ProcessResponse:
    """Extract a structured process representation from a natural-language input."""
    logger.info("Received extraction request for process_name=%s", request.process_name)

    try:
        # Delegate the extraction logic to the LLM-based service layer
        return extract_process_with_llm(request)
    except Exception as exc:
        # Log the full exception for debugging and return a generic API error response
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(exc)}")