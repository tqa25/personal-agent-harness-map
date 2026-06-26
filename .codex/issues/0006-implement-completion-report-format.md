# Implement Completion Report format

## Goal

Implement a consistent Completion Report format for CLI task results.

## Context

After work finishes, the Primary User needs a concise technical summary of what changed, which files matter, what verification ran, and what risks or blockers remain.

Relevant domain terms:

- `Completion Report`
- `Verification Run`
- `Repository Edit`
- `Delivery Action`
- `Memory Write`
- `Plan Approval`

## Requirements

- Define a structured Completion Report model.
- Include what changed.
- Include important files touched or created.
- Include Verification Runs and their pass/fail/not-run status.
- Include unresolved risks, blockers, or assumptions.
- Include Memory Writes made during the task.
- Include Delivery Actions performed or skipped.
- Match report length to task complexity.

## Acceptance Criteria

- Unit tests cover report rendering for simple tasks, repository edits, verification failures, memory writes, and blocked tasks.
- Reports clearly state when no verification was available.
- Reports clearly state when no files changed.
- Reports can reference an approved plan when one exists.
- CLI output remains readable in a terminal.

## Out of Scope

- HTML report generation.
- Persistent task history database.
- Telemetry dashboards.
- Long-form audit logs.
