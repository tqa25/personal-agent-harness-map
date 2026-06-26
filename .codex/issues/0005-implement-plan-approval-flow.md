# Implement Plan Approval flow

## Goal

Implement a Plan Approval flow for large, ambiguous, or risky tasks in the CLI Work Surface.

## Context

The Personal Copilot should accept free-form Task Intake. It should only ask follow-up questions or request Plan Approval when the task is ambiguous, risky, or requires a higher Autonomy Level.

Relevant domain terms:

- `Task Intake`
- `Plan Approval`
- `Autonomy Level`
- `Repository Edit`
- `Delivery Action`
- `Completion Report`

## Requirements

- Detect when a task likely needs Plan Approval because it is large, ambiguous, risky, or asks for Delivery Actions.
- Generate a short plan with intended actions, affected areas, verification approach, and expected output.
- Ask the Primary User to approve before execution.
- Allow small, clear tasks to proceed under the current Autonomy Level without forced planning.
- Preserve the approved plan in session context so the Completion Report can compare outcome against intent.
- Provide clear behavior for rejected or revised plans.

## Acceptance Criteria

- Unit tests cover tasks that do and do not require Plan Approval.
- Tests cover approved, rejected, and revised plan paths.
- Delivery Actions in Edit Mode require approval or mode change.
- Completion Reports can reference the approved plan when one exists.
- Existing console commands continue to work.

## Out of Scope

- Full PRD generation for every task.
- Multi-agent task delegation.
- Automatic issue decomposition for every approved plan.
- Long-form planning documents unless explicitly requested.
