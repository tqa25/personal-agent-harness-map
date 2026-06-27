from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from agent_harness.agent import build_runtime
from agent_harness.autonomy import AutonomyLevel
from agent_harness.config import HarnessConfig
from agent_harness.console import ConsoleState
from agent_harness.console import handle_console_input
from agent_harness.search import FakeSearchProvider
from agent_harness.search import SearchResult


@dataclass
class FakeAgent:
    responses: list[str]

    def create_session(self) -> dict[str, str]:
        return {"session": "fake"}

    async def _response(self, _message: str, **_kwargs: object) -> FakeResponse:
        return FakeResponse(self.responses.pop(0))

    def run(self, message: str, **kwargs: object):
        return self._response(message, **kwargs)


@dataclass
class FakeResponse:
    text: str


def _build_config(tmp_path: Path) -> HarnessConfig:
    return HarnessConfig(
        openai_model="gpt-5.4",
        repository_root=tmp_path,
        default_autonomy_level=AutonomyLevel.EDIT,
    )


def _runtime(tmp_path: Path, responses: list[str] | None = None):
    agent = FakeAgent(responses or ["Task finished."])
    fake_provider = FakeSearchProvider(
        {
            "docs": [
                SearchResult(
                    title="Docs",
                    url="https://docs.example.test",
                    snippet="Current docs",
                    source_type="official",
                    retrieved_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
                )
            ]
        }
    )
    return build_runtime(
        _build_config(tmp_path),
        agent_factory=lambda *_args, **_kwargs: agent,
        fake_search_provider=fake_provider,
    )


def test_memory_preference_requires_confirmation(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    state = ConsoleState(session=runtime.agent.create_session())

    state, outputs = asyncio.run(
        handle_console_input(
            runtime,
            state,
            "Remember that I prefer concise completion reports",
        )
    )

    assert outputs == ["Working Preference needs confirmation. Use /memory-confirm."]
    assert state.pending_memory is not None

    state, outputs = asyncio.run(handle_console_input(runtime, state, "/memory-confirm"))

    assert outputs == [f"Memory written to {tmp_path / '.learnings' / 'LEARNINGS.md'}"]
    assert "prefer concise completion reports" in (
        tmp_path / ".learnings" / "LEARNINGS.md"
    ).read_text().lower()


def test_local_issue_task_creates_backlog_entry(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    state = ConsoleState(session=runtime.agent.create_session())

    _state, outputs = asyncio.run(
        handle_console_input(runtime, state, "Create a local issue for adding retry logging")
    )

    assert outputs == ["Created Local Issue 0001: Adding retry logging"]
    assert (tmp_path / ".codex" / "issues" / "0001-adding-retry-logging.md").exists()


def test_delivery_task_requires_plan_approval_then_runs_report(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path, responses=["Committed and pushed after approval."])
    state = ConsoleState(session=runtime.agent.create_session())

    state, outputs = asyncio.run(
        handle_console_input(runtime, state, "Commit these changes and push the branch")
    )

    assert "Plan Approval Required" in outputs[0]
    assert state.pending_plan is not None

    state, outputs = asyncio.run(handle_console_input(runtime, state, "/approve"))

    report = outputs[0]
    assert "Completion Report" in report
    assert "Approved Plan:" in report
    assert "Delivery Actions:" in report


def test_technical_task_runs_verification_and_reports_it(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_smoke.py").write_text("def test_smoke():\n    assert True\n")
    runtime = _runtime(tmp_path, responses=["Fixed the test."])
    state = ConsoleState(session=runtime.agent.create_session())

    _state, outputs = asyncio.run(
        handle_console_input(runtime, state, "Fix the failing pytest test in src/agent.py")
    )

    report = outputs[0]
    assert "Completion Report" in report
    assert "Verification:" in report
    assert "python -m pytest" in report


def test_session_export_import_round_trip_preserves_console_state(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    state = ConsoleState(session=runtime.agent.create_session())
    state.autonomy_level = "deliver"
    state.pending_memory = None
    export_path = tmp_path / "session.json"

    _state, outputs = asyncio.run(
        handle_console_input(runtime, state, f"/session-export {export_path}")
    )

    assert outputs == [f"Exported session to {export_path}"]

    imported_state, outputs = asyncio.run(
        handle_console_input(runtime, state, f"/session-import {export_path}")
    )

    assert outputs == [f"Imported session from {export_path}"]
    assert imported_state.autonomy_level == "deliver"
