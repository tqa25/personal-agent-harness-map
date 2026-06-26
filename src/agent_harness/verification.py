from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from agent_harness.reports import VerificationRun


VerificationOutcome = Literal["passed", "failed", "skipped", "unavailable"]


@dataclass(frozen=True)
class VerificationCommand:
    name: str
    args: tuple[str, ...]
    required_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerificationResult:
    name: str
    outcome: VerificationOutcome
    detail: str = ""
    stdout: str = ""
    stderr: str = ""

    def to_report_run(self) -> VerificationRun:
        status = {
            "passed": "passed",
            "failed": "failed",
            "skipped": "not_run",
            "unavailable": "not_run",
        }[self.outcome]
        return VerificationRun(name=self.name, status=status, detail=self.detail)


@dataclass(frozen=True)
class VerificationSummary:
    results: list[VerificationResult] = field(default_factory=list)

    @property
    def report_runs(self) -> list[VerificationRun]:
        return [result.to_report_run() for result in self.results]

    @property
    def risks(self) -> list[str]:
        return [
            f"Verification failed: {result.name} exited with code {_exit_code(result.detail)}."
            for result in self.results
            if result.outcome == "failed"
        ]


def discover_verification_commands(
    root: Path,
    changed_files: list[str] | None = None,
) -> list[VerificationCommand]:
    script_path = root / "scripts" / "test"
    if script_path.exists():
        return [
            VerificationCommand(
                name="scripts/test",
                args=(str(script_path),),
            )
        ]

    package_path = root / "package.json"
    if package_path.exists():
        package = json.loads(package_path.read_text())
        if package.get("scripts", {}).get("test"):
            return [
                VerificationCommand(
                    name="npm test",
                    args=("npm", "test"),
                )
            ]

    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        return []

    with pyproject_path.open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    if "pytest" in pyproject.get("tool", {}):
        focused_tests = _changed_test_files(root, changed_files or [])
        pytest_args = (sys.executable, "-m", "pytest", *focused_tests)
        pytest_name = " ".join(("python", "-m", "pytest", *focused_tests))
        return [
            VerificationCommand(
                name=pytest_name,
                args=pytest_args,
            )
        ]

    return []


def run_verification(
    root: Path,
    explicit_commands: list[VerificationCommand] | None = None,
    changed_files: list[str] | None = None,
) -> VerificationSummary:
    commands = explicit_commands or discover_verification_commands(root, changed_files)
    if not commands:
        return VerificationSummary(
            results=[
                VerificationResult(
                    name="verification",
                    outcome="unavailable",
                    detail="No verification command discovered.",
                )
            ]
        )

    results = [_run_command(root, command) for command in commands]
    return VerificationSummary(results=results)


def _run_command(root: Path, command: VerificationCommand) -> VerificationResult:
    for required_path in command.required_paths:
        if not (root / required_path).exists():
            return VerificationResult(
                name=command.name,
                outcome="skipped",
                detail=f"Skipped because {required_path} is missing.",
            )

    try:
        completed = subprocess.run(
            command.args,
            cwd=root,
            capture_output=True,
            check=False,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        return VerificationResult(
            name=command.name,
            outcome="unavailable",
            detail="Command executable was not found.",
        )

    if completed.returncode == 0:
        outcome: VerificationOutcome = "passed"
    else:
        outcome = "failed"

    return VerificationResult(
        name=command.name,
        outcome=outcome,
        detail=f"exit code {completed.returncode}",
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _exit_code(detail: str) -> str:
    return detail.removeprefix("exit code ")


def _changed_test_files(root: Path, changed_files: list[str]) -> list[str]:
    return [
        changed_file
        for changed_file in changed_files
        if Path(changed_file).name.startswith("test_")
        and Path(changed_file).suffix == ".py"
        and (root / changed_file).exists()
    ]
