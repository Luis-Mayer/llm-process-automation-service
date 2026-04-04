"""
Live extraction tests using real OpenAI API.

This module contains integration tests that make actual API calls to OpenAI.
These tests are skipped by default unless OPENAI_API_KEY is set in the environment.
Use these tests to validate end-to-end functionality with real LLM responses.
"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Create a test client for making HTTP requests to the application
client = TestClient(app)


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set; skipping live extraction test.",
)
def test_extract_process_live():
    """
    Test process extraction with real OpenAI API calls.

    This integration test validates the complete extraction pipeline:
    - API endpoint accepts the request
    - LLM processes the natural language description
    - Structured response is returned and validated
    - All required fields are present in the response

    Note: This test requires a valid OPENAI_API_KEY and will incur API costs.
    """
    payload = {
        "process_name": "Invoice Approval",
        "description": (
            "An employee submits an invoice. The manager reviews it. "
            "If the amount exceeds 5000 EUR, finance approval is required. "
            "After approval, the invoice is paid."
        ),
    }

    response = client.post("/extract", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["process_name"] == "Invoice Approval"
    assert "summary" in data
    assert len(data["steps"]) >= 2
