from fastapi import FastAPI, HTTPException

from app.logging_utils import setup_logger
from app.schemas import ProcessRequest, ProcessResponse
from app.service import extract_process_with_llm
from app.storage import save_extraction_result

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
    # Simple health endpoint to verify that the service is running
    logger.info("Health check called")
    return {"status": "ok"}


@app.post("/extract", response_model=ProcessResponse)
def extract_process(request: ProcessRequest) -> ProcessResponse:
    # Log basic request context for traceability
    logger.info("Received extraction request for process_name=%s", request.process_name)

    try:
        # Run the LLM-based extraction pipeline
        result = extract_process_with_llm(request)

        # Persist request and response data locally for debugging and evaluation
        artifact_path = save_extraction_result(
            request_data=request.model_dump(),
            response_data=result.model_dump(),
        )

        # Log the successful extraction and storage location
        logger.info("Extraction successful. Saved artifact to %s", artifact_path)
        return result

    except Exception as exc:
        # Log the full exception traceback and return an HTTP 500 error
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(exc)}")
