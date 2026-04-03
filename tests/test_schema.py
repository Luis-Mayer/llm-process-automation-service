from app.schemas import DecisionPoint, ProcessRequest, ProcessResponse, ProcessStep


def test_process_request_valid():
    req = ProcessRequest(
        process_name="Invoice Approval",
        description="An employee submits an invoice. "
        "The manager reviews it. "
        "If the amount exceeds 5000 EUR, finance approval is required.",
    )
    assert req.process_name == "Invoice Approval"
    assert "employee submits" in req.description.lower()


def test_process_response_valid():
    response = ProcessResponse(
        process_name="Invoice Approval",
        summary="Invoice approval workflow with optional finance review.",
        roles=["Employee", "Manager", "Finance"],
        steps=[
            ProcessStep(id=1, actor="Employee", action="Submit invoice"),
            ProcessStep(id=2, actor="Manager", action="Review invoice"),
        ],
        decision_points=[
            DecisionPoint(
                condition="Amount > 5000 EUR",
                true_branch="Finance approval required",
                false_branch="Proceed to payment",
            )
        ],
    )

    assert response.process_name == "Invoice Approval"
    assert len(response.steps) == 2
    assert response.steps[0].condition is None
    assert response.steps[1].actor == "Manager"
    assert response.decision_points[0].condition == "Amount > 5000 EUR"


def test_process_response_missing_required_field_raises():
    try:
        ProcessResponse(
            process_name="Invoice Approval",
            summary="Invoice approval workflow",
            roles=["Employee", "Manager"],
            steps=[
                ProcessStep(id=1, actor="Employee", action="Submit invoice"),
            ],
            # data is missing decision_points, should raise
        )
        assert False, "Expected validation error for missing decision_points"
    except Exception as exc:
        assert "decision_points" in str(exc)

