import json
from pathlib import Path
from datetime import datetime
from typing import Any


def save_extraction_result(request_data: dict[str, Any], response_data: dict[str, Any]) -> str:
    # Create a directory for saved extraction artifacts if it does not exist yet
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)

    # Create a unique timestamp-based filename for each extraction result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = output_dir / f"extraction_{timestamp}.json"

    # Combine request and response data into one structured payload
    payload = {
        "timestamp": timestamp,
        "request": request_data,
        "response": response_data,
    }

    # Save the payload as a formatted JSON file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    # Return the saved file path for logging or later use
    return str(file_path)