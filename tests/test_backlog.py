from __future__ import annotations

import pytest

from agent_harness.backlog import (
    IssueNotFoundError,
    close_issue,
    complete_issue,
    create_issue,
    list_issues,
    show_issue,
)


def test_create_issue_writes_numbered_markdown_and_lists_it(tmp_path) -> None:
    issue = create_issue(tmp_path, "Add memory writer", "Persist repo learnings.")

    assert issue.id == "0001"
    assert issue.title == "Add memory writer"
    assert issue.status == "open"
    assert issue.path == tmp_path / ".codex" / "issues" / "0001-add-memory-writer.md"
    assert issue.path.read_text() == (
        "# Add memory writer\n\n"
        "Status: open\n\n"
        "Persist repo learnings.\n"
    )

    assert list_issues(tmp_path) == [issue]


def test_create_issue_with_same_title_uses_next_number_without_overwriting(tmp_path) -> None:
    first = create_issue(tmp_path, "Repeat work", "First body.")
    second = create_issue(tmp_path, "Repeat work", "Second body.")

    assert first.path != second.path
    assert first.path.name == "0001-repeat-work.md"
    assert second.path.name == "0002-repeat-work.md"
    assert first.path.read_text().endswith("First body.\n")
    assert second.path.read_text().endswith("Second body.\n")


def test_show_issue_finds_by_id_or_slug_and_reports_missing_issue(tmp_path) -> None:
    issue = create_issue(tmp_path, "Find this issue", "Lookup body.")

    assert show_issue(tmp_path, "0001") == issue
    assert show_issue(tmp_path, "find-this-issue") == issue
    assert show_issue(tmp_path, "0001").content.endswith("Lookup body.\n")

    with pytest.raises(IssueNotFoundError, match="Local Issue '9999' was not found"):
        show_issue(tmp_path, "9999")


def test_close_issue_preserves_markdown_body_and_keeps_issue_readable(tmp_path) -> None:
    body = "## Goal\n\n- Keep this checklist.\n- Preserve details."
    issue = create_issue(tmp_path, "Close this issue", body)

    closed = close_issue(tmp_path, "close-this-issue")

    assert closed.status == "closed"
    assert show_issue(tmp_path, "0001").status == "closed"
    assert issue.path.read_text() == (
        "# Close this issue\n\n"
        "Status: closed\n\n"
        "## Goal\n\n"
        "- Keep this checklist.\n"
        "- Preserve details.\n"
    )


def test_close_issue_inserts_status_for_existing_markdown_without_status(tmp_path) -> None:
    issues_dir = tmp_path / ".codex" / "issues"
    issues_dir.mkdir(parents=True)
    path = issues_dir / "0004-existing-issue.md"
    path.write_text("# Existing Issue\n\n## Goal\n\nKeep legacy markdown.\n")

    assert show_issue(tmp_path, "0004").status == "open"

    close_issue(tmp_path, "0004")

    assert path.read_text() == (
        "# Existing Issue\n\n"
        "Status: closed\n\n"
        "## Goal\n\n"
        "Keep legacy markdown.\n"
    )


def test_complete_issue_marks_issue_completed_without_deleting_it(tmp_path) -> None:
    issue = create_issue(tmp_path, "Finish this issue", "Done criteria.")

    completed = complete_issue(tmp_path, "0001")

    assert completed.status == "completed"
    assert issue.path.exists()
    assert show_issue(tmp_path, "finish-this-issue").status == "completed"
    assert issue.path.read_text().endswith("Done criteria.\n")
