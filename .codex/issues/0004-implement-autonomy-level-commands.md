# Implement Autonomy Level commands

## Goal

Implement configurable Autonomy Levels for the CLI Work Surface.

## Context

The Personal Copilot uses Autonomy Levels to decide how far it may go without stopping for approval. V1 defaults to Edit Mode, while Deliver Mode and Auto Mode can be selected explicitly.

Relevant domain terms:

- `Autonomy Level`
- `Edit Mode`
- `Deliver Mode`
- `Auto Mode`
- `Repository Edit`
- `Delivery Action`
- `Plan Approval`

## Requirements

- Add a configuration default for the Autonomy Level.
- Default V1 to Edit Mode.
- Add runtime commands to inspect and change the current Autonomy Level.
- Support at least `edit`, `deliver`, and `auto`.
- Enforce that Delivery Actions require Deliver Mode, Auto Mode, or explicit approval.
- Make Auto Mode boundaries explicit in config or command output.
- Include the current Autonomy Level in relevant Completion Reports.

## Acceptance Criteria

- Unit tests cover default mode selection, changing modes, invalid mode errors, and Delivery Action gating.
- CLI command output makes the current mode clear.
- Repository Edits remain allowed in Edit Mode.
- Delivery Actions are blocked in Edit Mode unless explicitly approved.
- Existing console commands continue to work.

## Out of Scope

- Organization policy engine.
- Per-tool permission matrices.
- Multi-user permissions.
- Cloud deployment approvals.
