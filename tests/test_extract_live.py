import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set; skipping live extraction test.",
)
def test_extract_process_live():
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