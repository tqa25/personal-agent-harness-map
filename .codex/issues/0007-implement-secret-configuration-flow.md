# Implement Secret Configuration flow

## Goal

Implement a safe local Secret Configuration flow for provider credentials and API keys.

## Context

The Personal Copilot needs model provider and Search Provider credentials, but secrets must not be committed. Secret Configuration may be written to `.env.local` only after Primary User approval.

Relevant domain terms:

- `Secret Configuration`
- `Search Provider`
- `Web Research`
- `Delivery Action`

## Requirements

- Read required credentials from environment variables by default.
- Detect missing provider configuration and report actionable errors.
- Support writing approved secrets to `.env.local`.
- Require explicit Primary User approval before writing `.env.local`.
- Ensure `.env.local` is ignored by git.
- Never print raw secret values in CLI output, logs, tests, or Completion Reports.
- Support separate credentials for model provider and Search Provider when needed.

## Acceptance Criteria

- Unit tests cover missing config, env config, approved `.env.local` writes, and denied writes.
- Tests verify raw secret values are redacted in output.
- `.env.local` remains ignored by git.
- CLI errors explain which variable is missing without exposing values.

## Out of Scope

- Cloud secret managers.
- Multi-user credential management.
- Rotating secrets automatically.
- Storing secrets in the Memory Surface.
