from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class TaskType(str, Enum):
    TECHNICAL_WORK = "technical_work"
    WEB_RESEARCH = "web_research"
    MEMORY_WORK = "memory_work"
    LOCAL_ISSUE_WORK = "local_issue_work"
    SECRET_CONFIGURATION = "secret_configuration"
    STATUS_PAGE_WORK = "status_page_work"


@dataclass(frozen=True)
class TaskClassification:
    task_type: TaskType | None
    route: str
    requires_clarification: bool
    clarification_question: str | None
    requires_plan_approval: bool
    requires_higher_autonomy: bool
    explanation: str
    bypasses_classification: bool = False


KEYWORDS: dict[TaskType, tuple[str, ...]] = {
    TaskType.TECHNICAL_WORK: (
        "code",
        "fix",
        "test",
        "pytest",
        "src/",
        "bug",
        "implement",
        "refactor",
    ),
    TaskType.WEB_RESEARCH: (
        "look up",
        "current",
        "docs",
        "web",
        "research",
        "source",
        "latest",
    ),
    TaskType.MEMORY_WORK: (
        "remember",
        "preference",
        "prefer",
        "learning",
        "learnings",
        "memory",
    ),
    TaskType.LOCAL_ISSUE_WORK: (
        "local issue",
        ".codex/issues",
        "backlog",
        "issue for",
        "triage",
    ),
    TaskType.SECRET_CONFIGURATION: (
        "api key",
        "secret",
        ".env",
        "credential",
        "token",
    ),
    TaskType.STATUS_PAGE_WORK: (
        "status page",
        "scope",
        "architecture",
        "glossary",
    ),
}

DELIVERY_ACTION_KEYWORDS = (
    "commit",
    "push",
    "pull request",
    "pr",
    "deploy",
    "publish",
    "release",
)


def _contains_delivery_action(normalized_task: str) -> bool:
    return any(
        re.search(rf"\b{re.escape(keyword)}\b", normalized_task)
        for keyword in DELIVERY_ACTION_KEYWORDS
    )


def classify_task(task: str) -> TaskClassification:
    stripped = task.strip()
    if stripped.startswith("/"):
        command_name = stripped.split(maxsplit=1)[0].lstrip("/")
        return TaskClassification(
            task_type=None,
            route="explicit_command",
            requires_clarification=False,
            clarification_question=None,
            requires_plan_approval=False,
            requires_higher_autonomy=False,
            explanation=f"Explicit command bypassed classification: {command_name}.",
            bypasses_classification=True,
        )

    normalized = task.lower()
    scores = {
        task_type: tuple(keyword for keyword in keywords if keyword in normalized)
        for task_type, keywords in KEYWORDS.items()
    }
    best_score = max(len(matches) for matches in scores.values())
    top_types = tuple(
        task_type for task_type, matches in scores.items() if len(matches) == best_score
    )
    task_type = top_types[0]
    matched = ", ".join(scores[task_type]) or "default"
    requires_clarification = best_score > 0 and len(top_types) > 1
    clarification_question = None
    ambiguity_note = ""
    if requires_clarification:
        labels = " or ".join(task_type.value for task_type in top_types)
        clarification_question = f"Should I handle this as {labels}?"
        ambiguity_note = f" ambiguous between: {', '.join(t.value for t in top_types)}."
    requires_higher_autonomy = _contains_delivery_action(normalized)
    risk_note = " delivery_action." if requires_higher_autonomy else ""
    return TaskClassification(
        task_type=task_type,
        route=task_type.value,
        requires_clarification=requires_clarification,
        clarification_question=clarification_question,
        requires_plan_approval=requires_higher_autonomy,
        requires_higher_autonomy=requires_higher_autonomy,
        explanation=(
            f"Classified as {task_type.value}; matched: {matched}; task: {task}."
            f"{ambiguity_note}{risk_note}"
        ),
    )
