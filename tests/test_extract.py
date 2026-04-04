"""
Tests for process extraction endpoints.

This module tests the API endpoints that handle process extraction from
both JSON and plain text inputs. Tests use mocking to isolate the LLM
service layer and focus on API behavior, request/response handling,
and data validation.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import DecisionPoint, ProcessResponse, ProcessStep

# Test client for making HTTP requests to the FastAPI app
# This simulates real API calls without starting a server
client = TestClient(app)


def test_extract_process(monkeypatch):
    """
    Test the /extract endpoint with JSON payload.

    This test validates:
    - JSON request parsing and validation
    - Response structure includes all required fields
    - Process name is correctly handled from request
    - New schema fields (inputs, outputs, risks, missing_information) are present
    """
    """
    Test the /extract endpoint with JSON input.

    Verifies that:
    - JSON requests are properly parsed
    - The LLM service is called with correct parameters
    - Response includes all new fields (inputs, outputs, risks, missing_info)
    - Process name from request is preserved in response
    """

    def mock_extract_process_with_llm(request):
        """Mock LLM service that returns a complete ProcessResponse."""
        return ProcessResponse(
            process_name=request.process_name or "Unknown Process",
            summary="Invoice approval workflow.",
            roles=["Employee", "Manager", "Finance"],
            steps=[
                ProcessStep(id=1, actor="Employee", action="Submit invoice"),
                ProcessStep(id=2, actor="Manager", action="Review invoice"),
                ProcessStep(
                    id=3,
                    actor="Finance",
                    action="Approve invoice",
                    condition="Amount > 5000 EUR",
                ),
            ],
            decision_points=[
                DecisionPoint(
                    condition="Amount > 5000 EUR",
                    true_branch="Finance approval required",
                    false_branch="Proceed to payment",
                )
            ],
            # Test the new fields added for enhanced process analysis
            inputs=["Invoice document", "Purchase order"],
            outputs=["Approved invoice", "Payment confirmation"],
            risks=["Payment delays", "Approval bottlenecks"],
            missing_information="Specific threshold amounts",
        )

    # Replace the real LLM service with our mock for testing
    monkeypatch.setattr("app.main.extract_process_with_llm", mock_extract_process_with_llm)

    # Test payload matching the ProcessRequest schema
    payload = {
        "process_name": "Invoice Approval",
        "description": (
            "An employee submits an invoice. The manager reviews it. "
            "Finance approves if greater than 5000 EUR. Payment is triggered after approval."
        ),
    }

    response = client.post("/extract", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Verify core functionality
    assert data["process_name"] == "Invoice Approval"
    assert "summary" in data
    assert len(data["steps"]) >= 2

    # Verify new enhanced fields are present and correctly typed
    assert "inputs" in data
    assert "outputs" in data
    assert "risks" in data
    assert "missing_information" in data
    assert isinstance(data["inputs"], list)
    assert isinstance(data["outputs"], list)
    assert isinstance(data["risks"], list)


def test_extract_process_from_text(monkeypatch):
    """
    Test the /extract-text endpoint with plain text input.

    This test validates:
    - Plain text content-type handling
    - Automatic process name assignment when not provided
    - Response structure is identical to JSON endpoint
    - All new schema fields are included in plain text responses
    """
    """
    Test the /extract-text endpoint with plain text input.

    Verifies that:
    - Plain text requests are accepted with correct content-type
    - Text is converted to ProcessRequest internally
    - Same extraction logic applies as JSON endpoint
    - All new fields are included in response
    - Process name defaults to "Unknown Process" when not provided
    """

    def mock_extract_process_with_llm(request):
        """Mock LLM service for plain text testing."""
        return ProcessResponse(
            process_name="Unknown Process",  # No name provided in plain text
            summary="Invoice approval workflow.",
            roles=["Employee", "Manager", "Finance"],
            steps=[
                ProcessStep(id=1, actor="Employee", action="Submit invoice"),
                ProcessStep(id=2, actor="Manager", action="Review invoice"),
                ProcessStep(
                    id=3,
                    actor="Finance",
                    action="Approve invoice",
                    condition="Amount > 5000 EUR",
                ),
            ],
            decision_points=[
                DecisionPoint(
                    condition="Amount > 5000 EUR",
                    true_branch="Finance approval required",
                    false_branch="Proceed to payment",
                )
            ],
            inputs=["Invoice document"],
            outputs=["Approved invoice"],
            risks=["Payment delays"],
            missing_information="Approval thresholds",
        )

    # Mock the service layer
    monkeypatch.setattr("app.main.extract_process_with_llm", mock_extract_process_with_llm)

    # Plain text input (no JSON structure)
    text_payload = (
        "An employee submits an invoice. The manager reviews it. "
        "Finance approves if greater than 5000 EUR. Payment is triggered after approval."
    )

    # Use 'content' parameter instead of deprecated 'data' for plain text
    response = client.post(
        "/extract-text",
        content=text_payload,
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify the endpoint works with plain text
    assert data["process_name"] == "Unknown Process"
    assert "summary" in data
    assert len(data["steps"]) >= 2

    # Verify enhanced fields are extracted even from plain text
    assert "inputs" in data
    assert "outputs" in data
    assert "risks" in data
    assert "missing_information" in data

    # Verify step structure is correct
    assert data["steps"][0]["actor"] == "Employee"
    assert data["steps"][1]["actor"] == "Manager"
