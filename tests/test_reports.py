from __future__ import annotations

from agent_harness.reports import (
    CompletionReport,
    DeliveryAction,
    MemoryWrite,
    ReportFile,
    VerificationRun,
)


def test_simple_report_states_summary_no_files_and_no_verification() -> None:
    report = CompletionReport(
        summary="Answered the repository question.",
        verifications=[
            VerificationRun(
                name="pytest",
                status="not_run",
                detail="No relevant tests exist for a read-only answer.",
            )
        ],
    )

    rendered = report.render()

    assert "Completion Report" in rendered
    assert "Answered the repository question." in rendered
    assert "Files: No files changed." in rendered
    assert "Verification:" in rendered
    assert "- NOT RUN pytest: No relevant tests exist for a read-only answer." in rendered


def test_report_renders_changed_files() -> None:
    report = CompletionReport(
        summary="Implemented the report renderer.",
        changed_files=[
            ReportFile(
                path="src/agent_harness/reports.py",
                change="created structured report model",
            ),
            ReportFile(
                path="tests/test_reports.py",
                change="covered terminal rendering",
            ),
        ],
        verifications=[
            VerificationRun(name="pytest tests/test_reports.py", status="passed")
        ],
    )

    rendered = report.render()

    assert "Files:" in rendered
    assert "- src/agent_harness/reports.py: created structured report model" in rendered
    assert "- tests/test_reports.py: covered terminal rendering" in rendered
    assert "- PASS pytest tests/test_reports.py" in rendered


def test_report_renders_verification_failure_and_risks() -> None:
    report = CompletionReport(
        summary="Updated report formatting.",
        verifications=[
            VerificationRun(
                name="pytest",
                status="failed",
                detail="tests/test_reports.py::test_expected failed",
            )
        ],
        risks=["Renderer output may still need CLI integration."],
    )

    rendered = report.render()

    assert "- FAIL pytest: tests/test_reports.py::test_expected failed" in rendered
    assert "Risks / Blockers:" in rendered
    assert "- Renderer output may still need CLI integration." in rendered


def test_report_renders_memory_writes_delivery_actions_and_plan_reference() -> None:
    report = CompletionReport(
        summary="Finished the memory-backed task.",
        approved_plan="plan-2026-06-26",
        memory_writes=[
            MemoryWrite(
                path=".learnings/LEARNINGS.md",
                kind="Repo Learning",
                detail="Recorded report formatting convention.",
            )
        ],
        delivery_actions=[
            DeliveryAction(
                name="git commit",
                status="skipped",
                detail="Delivery Actions require explicit approval in Edit Mode.",
            )
        ],
    )

    rendered = report.render()

    assert "Approved Plan: plan-2026-06-26" in rendered
    assert "Memory Writes:" in rendered
    assert (
        "- .learnings/LEARNINGS.md: Repo Learning - Recorded report formatting convention."
        in rendered
    )
    assert "Delivery Actions:" in rendered
    assert (
        "- SKIPPED git commit: Delivery Actions require explicit approval in Edit Mode."
        in rendered
    )
    assert "- NOT RUN verification: No verification was available." in rendered


def test_blocked_report_renders_blocked_status_and_blockers() -> None:
    report = CompletionReport(
        summary="Could not finish verification discovery.",
        status="blocked",
        risks=[
            "Repository does not define a verification command.",
            "Need Primary User to choose whether to add one.",
        ],
    )

    rendered = report.render()

    assert "Status: BLOCKED" in rendered
    assert "Could not finish verification discovery." in rendered
    assert "- Repository does not define a verification command." in rendered
    assert "- Need Primary User to choose whether to add one." in rendered
