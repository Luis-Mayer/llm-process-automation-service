from typing import List, Optional
from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    """Input payload for submitting a natural-language process description."""

    process_name: Optional[str] = Field(
        default=None,
        description="Optional name of the process."
    )
    description: str = Field(
        ...,
        min_length=20,
        description="Unstructured process description in natural language."
    )


class ProcessStep(BaseModel):
    """Represents a single ordered step in the extracted process."""

    id: int = Field(..., description="Sequential step identifier.")
    actor: str = Field(..., description="Role or system performing the step.")
    action: str = Field(..., description="Action performed in this step.")
    condition: Optional[str] = Field(
        default=None,
        description="Optional condition associated with this step."
    )


class DecisionPoint(BaseModel):
    """Represents a binary decision point derived from the process description."""

    condition: str = Field(..., description="Decision condition.")
    true_branch: str = Field(..., description="Outcome if condition is true.")
    false_branch: str = Field(..., description="Outcome if condition is false.")


class ProcessResponse(BaseModel):
    """Structured response returned by the extraction endpoint."""

    process_name: str = Field(..., description="Normalized process name.")
    summary: str = Field(..., description="Short summary of the process.")
    roles: List[str] = Field(..., description="List of involved roles or systems.")
    steps: List[ProcessStep] = Field(..., description="Ordered process steps.")
    decision_points: List[DecisionPoint] = Field(
        default_factory=list,
        description="Extracted decision points."
    )