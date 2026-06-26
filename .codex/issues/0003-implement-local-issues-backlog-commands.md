# Implement Local Issues backlog commands

## Goal

Implement CLI commands for managing the Local Issues Backlog stored in `.codex/issues/`.

## Context

Local Issues are markdown tasks concrete enough for the Personal Copilot or another agent to implement independently. Feature requests can remain rough ideas in `.learnings/FEATURE_REQUESTS.md`; implementation-ready work belongs in the Codex Issues Directory.

Relevant domain terms:

- `Local Issue`
- `Backlog`
- `Codex Issues Directory`
- `Feature Requests File`
- `Knowledge Output`

## Requirements

- Add commands to list Local Issues.
- Add commands to show a Local Issue by id or slug.
- Add commands to create a Local Issue from a title and body.
- Add commands to mark a Local Issue as closed or completed without deleting it.
- Use deterministic numbering such as `0001-title-slug.md`.
- Preserve markdown content when updating issue status.
- Keep Local Issues inside `.codex/issues/`.
- Do not use GitHub Issues for V1.

## Acceptance Criteria

- Unit tests cover issue creation, listing, lookup, and closing.
- Creating an issue with the same title does not overwrite an existing issue.
- Listing shows id, title, and status.
- Closed issues remain readable.
- CLI errors are clear when an issue id does not exist.

## Out of Scope

- GitHub Issues sync.
- Multi-repo issue routing.
- Issue assignment, labels, milestones, or kanban views.
- Automatically splitting every plan into issues.
