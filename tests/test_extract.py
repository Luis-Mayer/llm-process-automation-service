from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_extract_process():
    payload = {
        "process_name": "Invoice Approval",
        "description": "An employee submits an invoice. The manager reviews it. "
        "Finance approves if greater than 5000 EUR. Payment is triggered after approval.",
    }

    response = client.post("/extract", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["process_name"] == "Invoice Approval"
    assert isinstance(data.get("summary"), str) and len(data["summary"]) > 0
    assert isinstance(data.get("roles"), list) and "Employee" in data["roles"]
    assert len(data["steps"]) >= 2
    assert data["steps"][0]["actor"] == "Employee"
    assert data["steps"][1]["actor"] == "Manager"
    assert isinstance(data.get("decision_points"), list)


def test_extract_process_invalid_description_too_short():
    payload = {
        "process_name": "Invoice Approval",
        "description": "Short text",
    }

    response = client.post("/extract", json=payload)

    assert response.status_code == 422
    assert "description" in response.json()["detail"][0]["loc"]
