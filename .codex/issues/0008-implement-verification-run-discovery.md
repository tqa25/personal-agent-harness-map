# Implement Verification Run discovery

## Goal

Implement discovery and execution of relevant Verification Runs after Repository Edits.

## Context

The Personal Copilot must run relevant tests and static checks after Repository Edits when the Current Repository defines them. If no relevant check exists, the Completion Report must say so.

Relevant domain terms:

- `Verification Run`
- `Repository Edit`
- `Completion Report`
- `Current Repository`

## Requirements

- Discover common verification commands from repository files such as `pyproject.toml`, package manifests, scripts, or existing test conventions.
- Prefer focused checks related to changed files when practical.
- Fall back to broader checks when focused checks are unavailable.
- Capture pass, fail, skipped, and unavailable states.
- Include command names and concise outcomes in the Completion Report.
- Avoid silently ignoring failed checks.
- Allow verification commands to be configured explicitly if discovery is insufficient.

## Acceptance Criteria

- Unit tests cover discovery from `pyproject.toml` and fallback behavior when no checks exist.
- Tests cover pass, fail, skipped, and unavailable outcomes.
- Repository Edits can attach Verification Run results to Completion Reports.
- Failed checks are reported as residual risk or blockers.
- Verification does not mutate repo-tracked files except for normal test artifacts ignored by git.

## Out of Scope

- Full CI orchestration.
- Performance benchmarking.
- Cloud test runners.
- Multi-repo verification routing.
