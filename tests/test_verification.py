from __future__ import annotations

import sys

from agent_harness.verification import VerificationCommand
from agent_harness.verification import discover_verification_commands
from agent_harness.verification import run_verification


def test_pyproject_pytest_discovery_runs_passing_tests(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\n"
        'testpaths = ["tests"]\n'
        'pythonpath = ["."]\n'
    )
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_sample.py").write_text(
        "def test_sample_passes():\n"
        "    assert True\n"
    )

    result = run_verification(tmp_path)

    assert [run.name for run in result.report_runs] == ["python -m pytest"]
    assert result.report_runs[0].status == "passed"
    assert result.report_runs[0].detail == "exit code 0"


def test_pyproject_pytest_discovery_prefers_changed_test_file(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_focused.py").write_text(
        "def test_focused_passes():\n"
        "    assert True\n"
    )
    (tests_dir / "test_unrelated.py").write_text(
        "def test_unrelated_fails():\n"
        "    assert False\n"
    )

    result = run_verification(
        tmp_path,
        changed_files=["tests/test_focused.py"],
    )

    assert result.results[0].outcome == "passed"
    assert result.report_runs[0].name == "python -m pytest tests/test_focused.py"


def test_no_discovered_checks_reports_unavailable_verification(tmp_path) -> None:
    result = run_verification(tmp_path)

    assert len(result.results) == 1
    assert result.results[0].outcome == "unavailable"
    assert result.report_runs[0].name == "verification"
    assert result.report_runs[0].status == "not_run"
    assert result.report_runs[0].detail == "No verification command discovered."


def test_unavailable_command_reports_not_run_instead_of_crashing(tmp_path) -> None:
    result = run_verification(
        tmp_path,
        explicit_commands=[
            VerificationCommand(
                name="missing tool",
                args=("definitely-not-a-real-verification-tool",),
            )
        ],
    )

    assert result.results[0].outcome == "unavailable"
    assert result.report_runs[0].name == "missing tool"
    assert result.report_runs[0].status == "not_run"
    assert result.report_runs[0].detail == "Command executable was not found."


def test_scripts_test_discovery_runs_repository_script(tmp_path) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    script = scripts_dir / "test"
    script.write_text("#!/bin/sh\nexit 0\n")
    script.chmod(0o755)

    result = run_verification(tmp_path)

    assert result.results[0].outcome == "passed"
    assert result.report_runs[0].name == "scripts/test"
    assert result.report_runs[0].status == "passed"


def test_package_json_test_script_is_discovered(tmp_path) -> None:
    (tmp_path / "package.json").write_text(
        '{"scripts": {"test": "node --test"}}\n'
    )

    commands = discover_verification_commands(tmp_path)

    assert [command.name for command in commands] == ["npm test"]


def test_configured_failing_command_reports_failure_and_risk(tmp_path) -> None:
    result = run_verification(
        tmp_path,
        explicit_commands=[
            VerificationCommand(
                name="custom check",
                args=(
                    sys.executable,
                    "-c",
                    "import sys; print('broken check'); sys.exit(3)",
                ),
            )
        ],
    )

    assert result.results[0].outcome == "failed"
    assert result.report_runs[0].name == "custom check"
    assert result.report_runs[0].status == "failed"
    assert result.report_runs[0].detail == "exit code 3"
    assert result.risks == ["Verification failed: custom check exited with code 3."]


def test_configured_command_can_be_skipped_when_required_path_is_missing(
    tmp_path,
) -> None:
    result = run_verification(
        tmp_path,
        explicit_commands=[
            VerificationCommand(
                name="frontend tests",
                args=(sys.executable, "-c", "raise SystemExit(99)"),
                required_paths=("package.json",),
            )
        ],
    )

    assert result.results[0].outcome == "skipped"
    assert result.report_runs[0].name == "frontend tests"
    assert result.report_runs[0].status == "not_run"
    assert result.report_runs[0].detail == "Skipped because package.json is missing."
    assert result.risks == []
