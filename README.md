# LLM Process Automation Service

A container-ready FastAPI service for extracting structured process information from unstructured business process descriptions using OpenAI models.

## Overview

This project demonstrates how unstructured process descriptions can be transformed into structured JSON outputs using a production-oriented API service. It combines LLM-based extraction with schema validation, logging, and artifact persistence.

## Features

- FastAPI-based REST API
- OpenAI-powered extraction from unstructured text
- Structured JSON output validated with Pydantic
- Health endpoint for service monitoring
- Local logging to file and console
- Automatic storage of request/response artifacts
- Swagger UI for interactive testing
- Lightweight test setup with `pytest`

## Project Structure

```text
llm-process-automation-service/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── prompts.py
│   ├── openai_client.py
│   ├── service.py
│   ├── storage.py
│   └── logging_utils.py
│
├── tests/
│   ├── test_health.py
│   └── test_schema.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Example Use Case

### Input

A free-text business process description such as:

An employee submits an invoice. The manager reviews it. If the amount exceeds 5000 EUR, finance approval is required. After approval, the invoice is paid.

### Output

A structured JSON representation containing:

- process name
- summary
- involved roles
- ordered process steps
- decision points

## Setup

1. Clone the repository

   ```
   git clone https://github.com/Luis-Mayer/llm-process-automation-service.git
   cd llm-process-automation-service
   ```

2. Install dependencies

   ```
   uv sync
   ```

3. Create a `.env` file

   Create a file named `.env` in the project root:

   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o-mini
   LOG_LEVEL=INFO
   ```

4. Run the API locally

   ```
   uv run uvicorn app.main:app --reload
   ```

   The API will be available at:

   - API root: http://127.0.0.1:8000
   - Swagger docs: http://127.0.0.1:8000/docs

### Run with Docker

1. Build the container image:
   ```
   docker build -t llm-process-automation-service .
   ```
2. Run the container:
   ```
   docker run --rm -p 8000:8000 --env-file .env llm-process-automation-service
   ```

   The API will be available at the same endpoints:

   - API root: http://127.0.0.1:8000
   - Swagger docs: http://127.0.0.1:8000/docs

## API Endpoints

### GET /health

Simple health check endpoint.

**Response**
```json
{
  "status": "ok"
}
```

### POST /extract

Extracts structured process information from an unstructured process description.

**Example Request**
```json
{
  "process_name": "Invoice approval",
  "description": "An employee submits an invoice. The manager reviews it. If the amount exceeds 5000 EUR, finance approval is required. After approval, the invoice is paid."
}
```

**Example Response**
```json
{
  "process_name": "Invoice approval",
  "summary": "Invoice approval workflow with conditional finance approval.",
  "roles": [
    "Employee",
    "Manager",
    "Finance"
  ],
  "steps": [
    {
      "id": 1,
      "actor": "Employee",
      "action": "Submit invoice",
      "condition": null
    },
    {
      "id": 2,
      "actor": "Manager",
      "action": "Review invoice",
      "condition": null
    },
    {
      "id": 3,
      "actor": "Finance",
      "action": "Approve invoice",
      "condition": "Amount exceeds 5000 EUR"
    },
    {
      "id": 4,
      "actor": "System",
      "action": "Pay invoice",
      "condition": null
    }
  ],
  "decision_points": [
    {
      "condition": "Amount exceeds 5000 EUR",
      "true_branch": "Finance approval required",
      "false_branch": "Proceed directly to payment"
    }
  ]
}
```

## Testing

Run the test suite with:

```
uv run pytest
```

## Logging and Artifacts

The service automatically creates:

- `logs/app.log` for runtime logs
- `artifacts/` for saved request/response pairs

This supports debugging, reproducibility, and lightweight evaluation of extraction results.

## Future Improvements

Possible next steps:

- Docker-based deployment
- CI pipeline for automated tests
- prompt versioning
- additional schema fields such as inputs, outputs, or risks
- support for BPMN XML generation
- basic evaluation metrics for extraction quality

## Why this project?

This project was built to demonstrate practical AI engineering capabilities at the intersection of:

- LLM-based automation
- API development
- structured data extraction
- reproducible local deployment
- traceability and validation