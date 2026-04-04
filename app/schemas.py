"""
Pydantic data models for process automation API.

This module defines the request/response schemas using Pydantic BaseModel.
These models provide:
- Type validation and serialization
- Automatic API documentation generation
- JSON schema generation for LLM structured outputs
- Data integrity and consistency across the application
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    """
    Input payload for submitting a natural-language process description.

    This model validates incoming API requests and ensures the description
    meets minimum length requirements for meaningful processing.
    """

    process_name: Optional[str] = Field(default=None, description="Optional name of the process.")
    description: str = Field(
        ..., min_length=20, description="Unstructured process description in natural language."
    )


class ProcessStep(BaseModel):
    """
    Represents a single ordered step in the extracted process.

    Each step has a unique ID for ordering, identifies the actor/role
    performing the action, and may include conditional logic.
    """

    id: int = Field(..., description="Sequential step identifier.")
    actor: str = Field(..., description="Role or system performing the step.")
    action: str = Field(..., description="Action performed in this step.")
    condition: Optional[str] = Field(
        default=None, description="Optional condition associated with this step."
    )


class DecisionPoint(BaseModel):
    """
    Represents a binary decision point derived from the process description.

    Decision points capture conditional logic where the process flow
    branches based on specific conditions.
    """

    condition: str = Field(..., description="Decision condition.")
    true_branch: str = Field(..., description="Outcome if condition is true.")
    false_branch: str = Field(..., description="Outcome if condition is false.")


class ProcessResponse(BaseModel):
    """
    Structured response returned by the extraction endpoint.

    This comprehensive model captures all aspects of a business process:
    - Basic metadata (name, summary, roles)
    - Process flow (steps, decision points)
    - Resource requirements (inputs, outputs)
    - Risk assessment and gaps (risks, missing information)

    All fields are included in the LLM response schema to ensure
    complete process analysis in every extraction.
    """

    process_name: str = Field(..., description="Normalized process name.")
    summary: str = Field(..., description="Short summary of the process.")
    roles: List[str] = Field(..., description="List of involved roles or systems.")
    steps: List[ProcessStep] = Field(..., description="Ordered process steps.")
    decision_points: List[DecisionPoint] = Field(
        default_factory=list, description="Extracted decision points."
    )
    inputs: List[str] = Field(
        default_factory=list, description="List of inputs required for the process."
    )
    outputs: List[str] = Field(
        default_factory=list, description="List of outputs produced by the process."
    )
    risks: List[str] = Field(
        default_factory=list, description="Potential risks or issues in the process."
    )
    missing_information: Optional[str] = Field(
        default=None, description="Any information that is missing or unclear from the description."
    )
