import json
from unittest.mock import patch

from app.schemas import ProcessRequest
from app.service import extract_process_with_llm


def test_extract_process_with_llm_mocked_response():
    request = ProcessRequest(
        process_name="Invoice Approval",
        description="An employee submits an invoice. The manager approves it if above threshold.",
    )

    json_payload = {
        "process_name": "Invoice Approval",
        "summary": "Simple invoice approval process.",
        "roles": ["Employee", "Manager"],
        "steps": [
            {"id": 1, "actor": "Employee", "action": "Submit invoice", "condition": None},
            {"id": 2, "actor": "Manager", "action": "Review invoice", "condition": None},
        ],
        "decision_points": [
            {
                "condition": "Amount > 5000",
                "true_branch": "Finance approval",
                "false_branch": "Direct payment",
            }
        ],
    }

    class FakeResponse:
        output_text = json.dumps(json_payload)

    with patch("app.service.client") as mock_client:
        mock_client.responses.create.return_value = FakeResponse()

        result = extract_process_with_llm(request)

    assert result.process_name == "Invoice Approval"
    assert result.roles == ["Employee", "Manager"]
    assert result.steps[0].actor == "Employee"
    assert result.decision_points[0].condition == "Amount > 5000"
