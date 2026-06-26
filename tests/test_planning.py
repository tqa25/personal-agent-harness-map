import pytest

from agent_harness.autonomy import AutonomyLevel
from agent_harness.planning import (
    PlanApprovalRequirement,
    PlanApprovalSession,
    PlanApprovalState,
    assess_task_for_plan_approval,
    build_plan_approval_request,
)
from agent_harness.reports import CompletionReport


def test_small_clear_repository_task_can_proceed_without_plan_approval():
    decision = assess_task_for_plan_approval(
        "Fix the typo in README.md",
        autonomy_level=AutonomyLevel.EDIT,
    )

    assert decision.requirement is PlanApprovalRequirement.NOT_REQUIRED
    assert decision.can_proceed
    assert decision.reasons == ()


def test_delivery_action_in_edit_mode_requires_plan_approval():
    decision = assess_task_for_plan_approval(
        "Commit these changes and push the branch",
        autonomy_level=AutonomyLevel.EDIT,
    )

    assert decision.requirement is PlanApprovalRequirement.REQUIRED
    assert not decision.can_proceed
    assert "delivery_action" in decision.reasons


@pytest.mark.parametrize("autonomy_level", [AutonomyLevel.DELIVER, AutonomyLevel.AUTO])
def test_delivery_action_can_proceed_after_mode_change(autonomy_level):
    decision = assess_task_for_plan_approval(
        "Commit these changes and push the branch",
        autonomy_level=autonomy_level,
    )

    assert decision.requirement is PlanApprovalRequirement.NOT_REQUIRED
    assert decision.can_proceed


@pytest.mark.parametrize(
    ("task", "reason"),
    [
        ("Refactor the entire agent harness architecture", "large_task"),
        ("Improve the thing so it works better", "ambiguous_task"),
        ("Delete old generated files from the repository", "risky_task"),
    ],
)
def test_large_ambiguous_or_risky_tasks_require_plan_approval(task, reason):
    decision = assess_task_for_plan_approval(task)

    assert decision.requirement is PlanApprovalRequirement.REQUIRED
    assert reason in decision.reasons


def test_plan_approval_request_contains_short_executable_plan():
    request = build_plan_approval_request(
        "Refactor the planning helpers",
        affected_areas=("src/agent_harness/planning.py", "tests/test_planning.py"),
        verification=("pytest tests/test_planning.py",),
        expected_output="Completion Report with approved plan text",
    )

    assert "Plan Approval Required" in request.render()
    assert "- Intended actions: Refactor the planning helpers" in request.render()
    assert (
        "- Affected areas: src/agent_harness/planning.py, tests/test_planning.py"
        in request.render()
    )
    assert "- Verification: pytest tests/test_planning.py" in request.render()
    assert (
        "- Expected output: Completion Report with approved plan text"
        in request.render()
    )


def test_approved_plan_is_preserved_for_completion_report():
    request = build_plan_approval_request(
        "Refactor the planning helpers",
        affected_areas=("src/agent_harness/planning.py",),
        verification=("pytest tests/test_planning.py",),
        expected_output="Completion Report with approved plan text",
    )
    session = PlanApprovalSession(request)

    session.approve()

    assert session.state is PlanApprovalState.APPROVED
    assert session.approved_plan_text == request.render()

    report = CompletionReport(
        summary="Planning helpers implemented",
        approved_plan=session.approved_plan_text,
    )

    assert request.render() in report.render()


def test_rejected_plan_does_not_preserve_approved_plan_text():
    request = build_plan_approval_request(
        "Delete old generated files",
        affected_areas=("generated/",),
        verification=("pytest",),
        expected_output="No generated files remain",
    )
    session = PlanApprovalSession(request)

    session.reject("Too risky without a file list")

    assert session.state is PlanApprovalState.REJECTED
    assert session.rejection_reason == "Too risky without a file list"
    assert session.approved_plan_text is None


def test_revised_plan_replaces_request_and_clears_prior_decision():
    request = build_plan_approval_request(
        "Delete old generated files",
        affected_areas=("generated/",),
        verification=("pytest",),
        expected_output="No generated files remain",
    )
    revised = build_plan_approval_request(
        "List generated files before deleting any",
        affected_areas=("generated/",),
        verification=("pytest tests/test_planning.py",),
        expected_output="File list and revised deletion recommendation",
    )
    session = PlanApprovalSession(request)
    session.reject("Need a safer first step")

    session.revise(revised)

    assert session.state is PlanApprovalState.REVISED
    assert session.request == revised
    assert session.rejection_reason is None
    assert session.approved_plan_text is None
