from fastapi.testclient import TestClient

from app.main import app
from app.schemas import DecisionPoint, ProcessResponse, ProcessStep

client = TestClient(app)


def test_extract_process(monkeypatch):
    def mock_extract_process_with_llm(request):
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
        )

    monkeypatch.setattr("app.main.extract_process_with_llm", mock_extract_process_with_llm)

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
    assert data["process_name"] == "Invoice Approval"
    assert "summary" in data
    assert len(data["steps"]) >= 2
    assert data["steps"][0]["actor"] == "Employee"
    assert data["steps"][1]["actor"] == "Manager"
