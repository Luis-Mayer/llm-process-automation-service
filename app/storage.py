"""
Artifact storage utilities.

This module handles saving extraction results to disk for debugging,
auditing, and offline analysis. Each extraction creates a timestamped
JSON file containing both the original request and the LLM response.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def save_extraction_result(request_data: dict[str, Any], response_data: dict[str, Any]) -> str:
    """
    Save a complete extraction result to disk.

    This function creates a timestamped JSON file containing:
    - The original request data (process name, description)
    - The LLM response data (extracted process structure)
    - Metadata like timestamp for traceability

    The files are stored in the 'artifacts/' directory.

    Args:
        request_data: The original ProcessRequest as a dictionary
        response_data: The ProcessResponse as a dictionary

    Returns:
        str: Path to the saved artifact file
    """
    # Create artifacts directory if it doesn't exist
    # This ensures the app can run without manual setup
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)

    # Generate unique filename using high-precision timestamp
    # Format: YYYYMMDD_HHMMSS_microseconds
    # This ensures uniqueness even with rapid successive calls
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = output_dir / f"extraction_{timestamp}.json"

    # Structure the complete artifact with metadata
    # This provides full context for later analysis
    payload = {
        "timestamp": timestamp,
        "request": request_data,
        "response": response_data,
    }

    # Write formatted JSON with proper encoding
    # indent=2 for readability, ensure_ascii=False for Unicode support
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    # Return file path for logging and potential further processing
    return str(file_path)
