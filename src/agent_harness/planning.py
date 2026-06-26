from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from agent_harness.autonomy import AutonomyLevel


DELIVERY_ACTION_TERMS = (
    "commit",
    "push",
    "pull request",
    "pr",
    "deploy",
    "publish",
    "release",
)

LARGE_TASK_TERMS = (
    "architecture",
    "entire",
    "whole",
    "refactor",
    "redesign",
    "rewrite",
    "implement",
)

AMBIGUOUS_TASK_TERMS = (
    "improve",
    "better",
    "thing",
    "stuff",
    "clean up",
    "fix it",
)

RISKY_TASK_TERMS = (
    "delete",
    "remove",
    "drop",
    "reset",
    "migrate",
    "overwrite",
)


class PlanApprovalRequirement(str, Enum):
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"


class PlanApprovalState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISED = "revised"


@dataclass(frozen=True)
class PlanApprovalDecision:
    requirement: PlanApprovalRequirement
    reasons: tuple[str, ...] = ()

    @property
    def can_proceed(self) -> bool:
        return self.requirement is PlanApprovalRequirement.NOT_REQUIRED


@dataclass(frozen=True)
class PlanApprovalRequest:
    task: str
    affected_areas: tuple[str, ...]
    verification: tuple[str, ...]
    expected_output: str

    def render(self) -> str:
        return "\n".join(
            (
                "Plan Approval Required",
                "",
                f"- Intended actions: {self.task}",
                f"- Affected areas: {', '.join(self.affected_areas)}",
                f"- Verification: {', '.join(self.verification)}",
                f"- Expected output: {self.expected_output}",
            )
        )


@dataclass
class PlanApprovalSession:
    request: PlanApprovalRequest
    state: PlanApprovalState = PlanApprovalState.PENDING
    approved_plan_text: str | None = None
    rejection_reason: str | None = None

    def approve(self) -> None:
        self.state = PlanApprovalState.APPROVED
        self.approved_plan_text = self.request.render()

    def reject(self, reason: str) -> None:
        self.state = PlanApprovalState.REJECTED
        self.rejection_reason = reason
        self.approved_plan_text = None

    def revise(self, request: PlanApprovalRequest) -> None:
        self.request = request
        self.state = PlanApprovalState.REVISED
        self.rejection_reason = None
        self.approved_plan_text = None


def assess_task_for_plan_approval(
    task: str,
    *,
    autonomy_level: AutonomyLevel = AutonomyLevel.EDIT,
) -> PlanApprovalDecision:
    normalized = task.lower()
    reasons: list[str] = []

    if autonomy_level is AutonomyLevel.EDIT and any(
        _contains_term(normalized, term) for term in DELIVERY_ACTION_TERMS
    ):
        reasons.append("delivery_action")

    if any(_contains_term(normalized, term) for term in LARGE_TASK_TERMS):
        reasons.append("large_task")

    if any(_contains_term(normalized, term) for term in AMBIGUOUS_TASK_TERMS):
        reasons.append("ambiguous_task")

    if any(_contains_term(normalized, term) for term in RISKY_TASK_TERMS):
        reasons.append("risky_task")

    if reasons:
        return PlanApprovalDecision(
            requirement=PlanApprovalRequirement.REQUIRED,
            reasons=tuple(reasons),
        )

    return PlanApprovalDecision(requirement=PlanApprovalRequirement.NOT_REQUIRED)


def build_plan_approval_request(
    task: str,
    *,
    affected_areas: tuple[str, ...],
    verification: tuple[str, ...],
    expected_output: str,
) -> PlanApprovalRequest:
    return PlanApprovalRequest(
        task=task,
        affected_areas=affected_areas,
        verification=verification,
        expected_output=expected_output,
    )


def _contains_term(text: str, term: str) -> bool:
    return re.search(rf"\b{re.escape(term)}\b", text) is not None
