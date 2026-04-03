from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_extract_process():
    payload = {
        "process_name": "Invoice Approval",
        "description": "An employee submits an invoice. The manager reviews it.",
    }

    response = client.post("/extract", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["process_name"] == "Invoice Approval"
    assert "summary" in data
    assert len(data["steps"]) >= 2
    assert data["steps"][0]["actor"] == "Employee"
    assert data["steps"][1]["actor"] == "Manager"
