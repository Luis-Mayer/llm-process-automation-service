"""
Health endpoint tests.

This module contains tests for the application's health check endpoint,
which is used for monitoring service availability and basic functionality.
"""

from fastapi.testclient import TestClient

from app.main import app

# Create a test client instance for making HTTP requests to the FastAPI application
# This client simulates real HTTP calls without starting a server
client = TestClient(app)


def test_health_check():
    """
    Test the health check endpoint.

    This test verifies that:
    - The /health endpoint returns HTTP 200
    - The response contains the expected status message
    - The service is responsive and basic functionality works
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
