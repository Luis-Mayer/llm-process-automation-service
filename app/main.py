from fastapi import FastAPI, HTTPException, Body

from app.logging_utils import setup_logger
from app.schemas import ProcessRequest, ProcessResponse
from app.service import extract_process_with_llm
from app.storage import save_extraction_result

logger = setup_logger()

app = FastAPI(
    title="LLM Process Automation Service",
    version="0.1.0",
    description="API for extracting structured process information from unstructured text.",
)


@app.get("/health")
def health_check() -> dict:
    logger.info("Health check called")
    return {"status": "ok"}


@app.post("/extract", response_model=ProcessResponse)
def extract_process(request: ProcessRequest) -> ProcessResponse:
    logger.info("Received extraction request for process_name=%s", request.process_name)

    try:
        result = extract_process_with_llm(request)

        artifact_path = save_extraction_result(
            request_data=request.model_dump(),
            response_data=result.model_dump(),
        )

        logger.info("Extraction successful. Saved artifact to %s", artifact_path)
        return result

    except Exception as exc:
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(exc)}")


@app.post("/extract-text", response_model=ProcessResponse)
def extract_process_from_text(description: str = Body(..., media_type="text/plain")) -> ProcessResponse:
    logger.info("Received plain text extraction request")

    try:
        request = ProcessRequest(process_name=None, description=description)
        result = extract_process_with_llm(request)

        artifact_path = save_extraction_result(
            request_data=request.model_dump(),
            response_data=result.model_dump(),
        )

        logger.info("Plain text extraction successful. Saved artifact to %s", artifact_path)
        return result

    except Exception as exc:
        logger.exception("Plain text extraction failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(exc)}")
