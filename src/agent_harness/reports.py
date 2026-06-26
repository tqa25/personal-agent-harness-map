from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


VerificationStatus = Literal["passed", "failed", "not_run"]
DeliveryActionStatus = Literal["performed", "skipped", "failed"]
CompletionStatus = Literal["completed", "blocked"]


@dataclass(frozen=True)
class VerificationRun:
    name: str
    status: VerificationStatus
    detail: str = ""

    def render(self) -> str:
        label = {
            "passed": "PASS",
            "failed": "FAIL",
            "not_run": "NOT RUN",
        }[self.status]
        suffix = f": {self.detail}" if self.detail else ""
        return f"- {label} {self.name}{suffix}"


@dataclass(frozen=True)
class ReportFile:
    path: str
    change: str

    def render(self) -> str:
        return f"- {self.path}: {self.change}"


@dataclass(frozen=True)
class MemoryWrite:
    path: str
    kind: str
    detail: str

    def render(self) -> str:
        return f"- {self.path}: {self.kind} - {self.detail}"


@dataclass(frozen=True)
class DeliveryAction:
    name: str
    status: DeliveryActionStatus
    detail: str = ""

    def render(self) -> str:
        label = {
            "performed": "PERFORMED",
            "skipped": "SKIPPED",
            "failed": "FAILED",
        }[self.status]
        suffix = f": {self.detail}" if self.detail else ""
        return f"- {label} {self.name}{suffix}"


@dataclass(frozen=True)
class CompletionReport:
    summary: str
    status: CompletionStatus = "completed"
    approved_plan: str | None = None
    changed_files: list[ReportFile] = field(default_factory=list)
    verifications: list[VerificationRun] = field(default_factory=list)
    memory_writes: list[MemoryWrite] = field(default_factory=list)
    delivery_actions: list[DeliveryAction] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            "Completion Report",
            "",
            f"Status: {self.status.upper()}",
            "",
            self.summary,
        ]

        if self.approved_plan:
            lines.extend(["", f"Approved Plan: {self.approved_plan}"])

        lines.append("")

        if self.changed_files:
            lines.append("Files:")
            lines.extend(file.render() for file in self.changed_files)
        else:
            lines.append("Files: No files changed.")

        lines.extend(["", "Verification:"])

        if self.verifications:
            lines.extend(verification.render() for verification in self.verifications)
        else:
            lines.append("- NOT RUN verification: No verification was available.")

        if self.risks:
            lines.extend(["", "Risks / Blockers:"])
            lines.extend(f"- {risk}" for risk in self.risks)

        if self.memory_writes:
            lines.extend(["", "Memory Writes:"])
            lines.extend(memory_write.render() for memory_write in self.memory_writes)

        if self.delivery_actions:
            lines.extend(["", "Delivery Actions:"])
            lines.extend(delivery_action.render() for delivery_action in self.delivery_actions)

        return "\n".join(lines)
