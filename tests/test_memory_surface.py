from __future__ import annotations

from datetime import UTC, datetime

from agent_harness.memory_surface import MemorySurface


def test_repo_learning_creates_memory_surface_and_appends_entry(tmp_path) -> None:
    memory = MemorySurface(tmp_path)

    result = memory.write(
        "repo_learning",
        "Use pytest's tmp_path for repository-backed file behavior.",
        context="Added Memory Surface writer tests.",
        timestamp=datetime(2026, 6, 26, 12, 0, tzinfo=UTC),
    )

    assert result.written is True
    assert result.path == tmp_path / ".learnings" / "LEARNINGS.md"
    assert (tmp_path / ".learnings" / "ERRORS.md").exists()
    assert (tmp_path / ".learnings" / "FEATURE_REQUESTS.md").exists()

    learnings = (tmp_path / ".learnings" / "LEARNINGS.md").read_text()
    assert "## 2026-06-26T12:00:00+00:00 - Repo Learning" in learnings
    assert "Use pytest's tmp_path for repository-backed file behavior." in learnings
    assert "Context: Added Memory Surface writer tests." in learnings


def test_memory_types_route_to_expected_files(tmp_path) -> None:
    memory = MemorySurface(tmp_path)
    timestamp = datetime(2026, 6, 26, 12, 0, tzinfo=UTC)

    research = memory.write(
        "research_learning",
        "Official docs say use the stable API.",
        context="Compared current documentation.",
        timestamp=timestamp,
    )
    error = memory.write(
        "recurring_error",
        "Pytest collection failed when the module was missing.",
        context="Verified by running pytest.",
        timestamp=timestamp,
    )
    feature = memory.write(
        "feature_request",
        "Add a command that summarizes recent Memory Writes.",
        context="Follow-up idea from implementation.",
        timestamp=timestamp,
    )
    preference = memory.write(
        "working_preference",
        "Prefer terse completion reports.",
        context="Confirmed by the Primary User.",
        confirmed=True,
        timestamp=timestamp,
    )

    assert research.path == tmp_path / ".learnings" / "LEARNINGS.md"
    assert error.path == tmp_path / ".learnings" / "ERRORS.md"
    assert feature.path == tmp_path / ".learnings" / "FEATURE_REQUESTS.md"
    assert preference.path == tmp_path / ".learnings" / "LEARNINGS.md"

    assert "Research Learning" in (tmp_path / ".learnings" / "LEARNINGS.md").read_text()
    assert "Working Preference" in (tmp_path / ".learnings" / "LEARNINGS.md").read_text()
    assert "Recurring Error" in (tmp_path / ".learnings" / "ERRORS.md").read_text()
    assert "Feature Request" in (tmp_path / ".learnings" / "FEATURE_REQUESTS.md").read_text()


def test_working_preference_requires_confirmation(tmp_path) -> None:
    memory = MemorySurface(tmp_path)

    result = memory.write(
        "working_preference",
        "Prefer terse completion reports.",
        context="Inferred from a single request.",
        confirmed=False,
        timestamp=datetime(2026, 6, 26, 12, 0, tzinfo=UTC),
    )

    assert result.written is False
    assert result.reason == "working_preference_requires_confirmation"
    assert "Prefer terse completion reports." not in (
        tmp_path / ".learnings" / "LEARNINGS.md"
    ).read_text()


def test_duplicate_memory_write_is_skipped(tmp_path) -> None:
    memory = MemorySurface(tmp_path)
    timestamp = datetime(2026, 6, 26, 12, 0, tzinfo=UTC)

    first = memory.write(
        "repo_learning",
        "Use pytest tmp_path for repository backed file behavior.",
        context="First observation.",
        timestamp=timestamp,
    )
    duplicate = memory.write(
        "repo_learning",
        "Use pytest's tmp_path for repository-backed file behavior!",
        context="Repeated observation.",
        timestamp=timestamp,
    )

    learnings = (tmp_path / ".learnings" / "LEARNINGS.md").read_text()
    assert first.written is True
    assert duplicate.written is False
    assert duplicate.reason == "duplicate"
    assert learnings.count("Repo Learning") == 1


def test_memory_write_redacts_obvious_secrets(tmp_path) -> None:
    memory = MemorySurface(tmp_path)

    memory.write(
        "recurring_error",
        "Request failed with OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890.",
        context="Bearer ghp_abcdefghijklmnopqrstuvwxyz1234567890abcdef was in logs.",
        timestamp=datetime(2026, 6, 26, 12, 0, tzinfo=UTC),
    )

    errors = (tmp_path / ".learnings" / "ERRORS.md").read_text()
    assert "sk-proj-" not in errors
    assert "ghp_" not in errors
    assert "OPENAI_API_KEY=[REDACTED]" in errors
    assert "Bearer [REDACTED]" in errors
