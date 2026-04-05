"""
Evaluation framework for process extraction quality.

This module implements an evaluation pipeline that tests the LLM-based process
extraction service against a golden dataset of known good inputs and outputs.
It provides metrics for:
- Role coverage: How many expected roles were extracted
- Step count validation: Minimum number of steps required
- Output coverage: How many expected outputs were captured
- Risk identification: How many expected risks were detected

The evaluation results are saved for analysis and can be used to track
extraction quality over time and after model/prompt changes.
"""

import json
from pathlib import Path
from typing import Any

import requests

# API endpoint for plain text extraction
API_URL = "http://127.0.0.1:8000/extract-text"

# Path to the golden dataset containing test cases with expected outputs
GOLDEN_SET_PATH = Path("evaluation/golden_set.json")

# Path where evaluation results will be saved for analysis and metrics
RESULTS_PATH = Path("evaluation/results.json")


def normalize_list(values: list[str]) -> list[str]:
    """
    Normalize strings for comparison.

    Converts values to lowercase and strips whitespace to ensure
    consistent matching regardless of capitalization or formatting.
    This is important for fuzzy matching of extracted values.

    Args:
        values: List of strings to normalize

    Returns:
        List of normalized strings
    """
    return [value.strip().lower() for value in values]


def compute_role_coverage(expected_roles: list[str], actual_roles: list[str]) -> float:
    """
    Calculate the percentage of expected roles that were extracted.

    This metric shows how well the LLM identifies all actors and systems
    involved in the process. A coverage of 0.8 (80%) is considered acceptable.

    Args:
        expected_roles: Roles from the golden dataset
        actual_roles: Roles extracted by the LLM

    Returns:
        Coverage ratio between 0.0 and 1.0
    """
    expected = set(normalize_list(expected_roles))
    actual = set(normalize_list(actual_roles))

    # Handle edge case: if no roles expected, consider perfect coverage
    if not expected:
        return 1.0

    # Calculate intersection - how many expected roles were found
    matched = expected.intersection(actual)
    return len(matched) / len(expected)


def contains_expected_items(expected_items: list[str], actual_items: list[str]) -> float:
    """
    Calculate coverage of expected items in actual items using partial matching.

    This function handles fuzzy matching where expected items might be
    substrings of actual items (e.g., "Payment" in "Payment processing").
    Used for outputs, risks, and other list-based comparisons.

    Args:
        expected_items: Expected items from golden dataset
        actual_items: Items extracted by the LLM

    Returns:
        Coverage ratio between 0.0 and 1.0
    """
    expected = normalize_list(expected_items)
    actual = normalize_list(actual_items)

    # Handle edge case: if no items expected, consider perfect coverage
    if not expected:
        return 1.0

    # Count matches using bidirectional substring matching
    matches = 0
    for expected_item in expected:
        # Item is considered matched if it's a substring or contains a substring
        # This handles variations like "approval" vs "invoice approval"
        if any(
            expected_item in actual_item or actual_item in expected_item for actual_item in actual
        ):
            matches += 1

    return matches / len(expected)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate a single test case against the extraction API.

    This function:
    1. Sends the test input to the extraction endpoint
    2. Receives and parses the JSON response
    3. Compares extracted values against expected values
    4. Calculates multiple quality metrics
    5. Determines if the case passed based on thresholds

    Args:
        case: Test case dictionary containing input_text and expected values

    Returns:
        Evaluation result with metrics, status, and actual output
    """
    input_text = case["input_text"]
    expected = case["expected"]

    # Make API request with plain text input
    # Using 60 second timeout for LLM processing time
    response = requests.post(
        API_URL,
        data=input_text,
        headers={"Content-Type": "text/plain"},
        timeout=60,
    )

    # Initialize result with basic information
    result: dict[str, Any] = {
        "id": case["id"],
        "status_code": response.status_code,
    }

    # Handle API errors
    if response.status_code != 200:
        result["passed"] = False
        result["error"] = response.text
        return result

    # Parse the successful response
    actual = response.json()

    # Extract the metrics we're evaluating
    actual_roles = actual.get("roles", [])
    actual_steps = actual.get("steps", [])
    actual_outputs = actual.get("outputs", [])
    actual_risks = actual.get("risks", [])

    # Calculate individual metrics
    role_coverage = compute_role_coverage(expected.get("roles", []), actual_roles)
    min_steps_passed = len(actual_steps) >= expected.get("min_steps", 0)
    output_coverage = contains_expected_items(expected.get("outputs", []), actual_outputs)
    risk_coverage = contains_expected_items(expected.get("risks", []), actual_risks)

    # Convert the boolean step check into a numeric score
    step_score = 1.0 if min_steps_passed else 0.0

    # Compute an overall score across all evaluation dimensions
    overall_score = (
        role_coverage
        + step_score
        + output_coverage
        + risk_coverage
    ) / 4

    # Determine overall pass/fail using threshold-based logic
    passed = overall_score >= 0.8

    # Add detailed metrics to result
    result.update(
        {
            "passed": passed,
            "metrics": {
                "role_coverage": role_coverage,
                "step_count": len(actual_steps),
                "min_steps_expected": expected.get("min_steps", 0),
                "min_steps_passed": min_steps_passed,
                "step_score": step_score,
                "output_coverage": output_coverage,
                "risk_coverage": risk_coverage,
                "overall_score": overall_score,
            },
            "actual_output": actual,
        }
    )

    return result


def main() -> None:
    """
    Run the complete evaluation pipeline.

    This function:
    1. Loads the golden dataset with test cases
    2. Evaluates each test case against the API
    3. Saves results to a JSON file for analysis
    4. Prints a summary of pass/fail results
    """
    # Load golden dataset containing expected test cases and outputs
    with GOLDEN_SET_PATH.open("r", encoding="utf-8") as f:
        golden_set = json.load(f)

    # Run evaluation for each test case
    results = [evaluate_case(case) for case in golden_set]

    # Save results to file for further analysis and tracking
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary statistics
    total = len(results)
    passed = sum(result["passed"] for result in results)
    print(f"Evaluation finished: {passed}/{total} cases passed")
    average_score = sum(
        result["metrics"]["overall_score"]
        for result in results
        if "metrics" in result
    ) / total

    print(f"Average overall score: {average_score:.2f}")

    # Print detailed results for each test case
    for result in results:
        print(f"- {result['id']}: passed={result['passed']}, status_code={result['status_code']}")


if __name__ == "__main__":
    main()
