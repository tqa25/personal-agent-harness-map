# Implement CLI Task Intake classification

## Goal

Implement Task Intake classification for the CLI Work Surface.

## Context

The Primary User should be able to enter tasks freely. The Personal Copilot should infer the likely task type and only ask follow-up questions when the classification affects execution, risk, or Autonomy Level.

Relevant domain terms:

- `Task Intake`
- `Technical Work`
- `Personal Knowledge Work`
- `Web Research`
- `Memory Write`
- `Local Issue`
- `Plan Approval`
- `Autonomy Level`

## Requirements

- Classify free-form tasks into at least technical work, web research, memory work, local issue work, secret configuration, and status page work.
- Detect when classification is ambiguous and ask a concise clarification.
- Route each classification to the relevant flow or command handler.
- Do not require the Primary User to choose a task type before every task.
- Detect when a task likely requires Plan Approval or a higher Autonomy Level.
- Keep classification explainable in debug or verbose output.

## Acceptance Criteria

- Unit tests cover representative tasks for each supported classification.
- Tests cover ambiguous task clarification.
- Tests cover detection of tasks requiring Plan Approval.
- Small clear tasks do not trigger unnecessary planning.
- Existing explicit commands continue to bypass classification where appropriate.

## Out of Scope

- Training a custom classifier.
- Multi-agent routing.
- Calendar, email, or messaging task classes.
- Full natural language workflow programming.
