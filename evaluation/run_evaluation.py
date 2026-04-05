"""
Evaluation framework for process extraction quality.

This module implements a lightweight evaluation pipeline for the LLM-based
process extraction service. It compares API outputs against a small golden
dataset of expected process characteristics and computes simple quality metrics.

Current evaluation dimensions:
- Role coverage: How many expected roles were extracted
- Step count validation: Whether a minimum number of steps was returned
- Output coverage: How many expected outputs were captured
- Risk coverage: How many expected risks were identified

The results are stored as JSON so model or prompt changes can be compared
across multiple evaluation runs over time.
"""

import json
import re
from pathlib import Path
from typing import Any

import requests

# Plain-text API endpoint used for evaluation calls.
API_URL = "http://127.0.0.1:8000/extract-text"

# Golden dataset containing test inputs and expected characteristics.
GOLDEN_SET_PATH = Path("evaluation/golden_set.json")

# Output file for evaluation results.
RESULTS_PATH = Path("evaluation/results.json")


def normalize_text(value: str) -> str:
    """
    Normalize a single text value for comparison.

    Lowercasing and trimming whitespace makes comparisons more robust to
    formatting differences in model outputs.

    Args:
        value: Raw string value

    Returns:
        Normalized string
    """
    return value.strip().lower()


def normalize_list(values: list[str]) -> list[str]:
    """
    Normalize a list of strings for comparison.

    Args:
        values: List of raw string values

    Returns:
        List of normalized strings
    """
    return [normalize_text(value) for value in values]


def tokenize(value: str) -> set[str]:
    """
    Convert a string into a set of normalized word tokens.

    This supports more flexible matching for semantically similar phrases such as
    'budget approval' and 'approved budget'.

    Args:
        value: Raw input string

    Returns:
        Set of lowercase tokens
    """
    normalized = normalize_text(value)
    return set(re.findall(r"\b[a-z0-9]+\b", normalized))


def token_overlap_score(expected_item: str, actual_item: str) -> float:
    """
    Compute token overlap relative to the expected item.

    A score of 1.0 means that all expected tokens appear in the actual item.
    This is useful when wording differs but key terms are still preserved.

    Args:
        expected_item: Expected phrase from the golden dataset
        actual_item: Phrase returned by the extraction API

    Returns:
        Overlap score between 0.0 and 1.0
    """
    expected_tokens = tokenize(expected_item)
    actual_tokens = tokenize(actual_item)

    if not expected_tokens:
        return 1.0

    overlap = expected_tokens.intersection(actual_tokens)
    return len(overlap) / len(expected_tokens)


def items_match(expected_item: str, actual_item: str, threshold: float = 0.5) -> bool:
    """
    Determine whether two textual items should be treated as a match.

    Matching is considered successful if either:
    - one string is a substring of the other, or
    - token overlap reaches the specified threshold

    Args:
        expected_item: Expected value from the golden dataset
        actual_item: Value extracted by the API
        threshold: Minimum token overlap required for a match

    Returns:
        True if the two items are considered a match, otherwise False
    """
    expected_norm = normalize_text(expected_item)
    actual_norm = normalize_text(actual_item)

    # Fast path for exact or substring-style matches.
    if expected_norm in actual_norm or actual_norm in expected_norm:
        return True

    # Fallback to token-based matching for wording variations.
    return token_overlap_score(expected_item, actual_item) >= threshold


def compute_role_coverage(expected_roles: list[str], actual_roles: list[str]) -> float:
    """
    Calculate the percentage of expected roles that were extracted.

    Uses flexible matching so roles such as 'manager' and 'direct manager'
    can still be considered a match.

    Args:
        expected_roles: Roles defined in the golden dataset
        actual_roles: Roles extracted by the API

    Returns:
        Coverage ratio between 0.0 and 1.0
    """
    expected = normalize_list(expected_roles)
    actual = normalize_list(actual_roles)

    if not expected:
        return 1.0

    matches = 0
    for expected_role in expected:
        if any(items_match(expected_role, actual_role, threshold=0.5) for actual_role in actual):
            matches += 1

    return matches / len(expected)


def contains_expected_items(expected_items: list[str], actual_items: list[str]) -> float:
    """
    Calculate coverage of expected items using flexible matching.

    This is used for outputs, risks, and other list-based comparisons where
    wording can vary slightly between the expected benchmark and model output.

    Args:
        expected_items: Expected items from the golden dataset
        actual_items: Items extracted by the API

    Returns:
        Coverage ratio between 0.0 and 1.0
    """
    expected = normalize_list(expected_items)
    actual = normalize_list(actual_items)

    if not expected:
        return 1.0

    matches = 0
    for expected_item in expected:
        if any(items_match(expected_item, actual_item, threshold=0.5) for actual_item in actual):
            matches += 1

    return matches / len(expected)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate a single golden-set case against the extraction API.

    The function sends the input text to the plain-text extraction endpoint,
    collects the structured response, computes evaluation metrics, and returns
    both the metrics and the actual model output for inspection.

    Args:
        case: One golden-set test case containing input_text and expected values

    Returns:
        Evaluation result dictionary with metrics and API output
    """
    input_text = case["input_text"]
    expected = case["expected"]

    # Send the test case to the API. A generous timeout is used because the
    # endpoint depends on LLM inference and can take a few seconds to respond.
    response = requests.post(
        API_URL,
        data=input_text,
        headers={"Content-Type": "text/plain"},
        timeout=60,
    )

    result: dict[str, Any] = {
        "id": case["id"],
        "status_code": response.status_code,
    }

    # If the API call fails, return the error information directly so the case
    # can be inspected without breaking the full evaluation run.
    if response.status_code != 200:
        result["passed"] = False
        result["error"] = response.text
        return result

    actual = response.json()

    # Extract only the response fields that are currently part of the
    # lightweight benchmark setup.
    actual_roles = actual.get("roles", [])
    actual_steps = actual.get("steps", [])
    actual_outputs = actual.get("outputs", [])
    actual_risks = actual.get("risks", [])

    # Compute metric values.
    role_coverage = compute_role_coverage(expected.get("roles", []), actual_roles)
    min_steps_passed = len(actual_steps) >= expected.get("min_steps", 0)
    output_coverage = contains_expected_items(expected.get("outputs", []), actual_outputs)
    risk_coverage = contains_expected_items(expected.get("risks", []), actual_risks)

    # Convert the step threshold check into a numeric score so it can be
    # included in the overall score calculation.
    step_score = 1.0 if min_steps_passed else 0.0

    # Aggregate all evaluation dimensions into one overall score.
    overall_score = (role_coverage + step_score + output_coverage + risk_coverage) / 4

    # A case is considered passed if the overall score reaches the threshold.
    passed = overall_score >= 0.8

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

    This function loads the golden dataset, evaluates each case against the API,
    stores the results as JSON, and prints a compact summary to the console.
    """
    with GOLDEN_SET_PATH.open("r", encoding="utf-8") as f:
        golden_set = json.load(f)

    results = [evaluate_case(case) for case in golden_set]

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total = len(results)
    passed = sum(result["passed"] for result in results)
    print(f"Evaluation finished: {passed}/{total} cases passed")

    average_score = (
        sum(result["metrics"]["overall_score"] for result in results if "metrics" in result) / total
    )
    print(f"Average overall score: {average_score:.2f} ({average_score * 100:.1f}%)")

    for result in results:
        print(f"- {result['id']}: passed={result['passed']}, status_code={result['status_code']}")


if __name__ == "__main__":
    main()
