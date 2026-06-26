# Implement Memory Surface writer

## Goal

Implement a repository-backed Memory Surface writer for V1 so the Personal Copilot can persist reusable knowledge in the Current Repository.

## Context

The Memory Surface is `.learnings/` in the Current Repository:

- `.learnings/LEARNINGS.md` for reusable discoveries, conventions, solutions, Research Learnings, and confirmed Working Preferences.
- `.learnings/ERRORS.md` for recurring errors, failed attempts, root causes, and verified fixes.
- `.learnings/FEATURE_REQUESTS.md` for future capabilities that are not yet implementation-ready Local Issues.

Relevant domain terms:

- `Memory Surface`
- `Memory Write`
- `Working Preference`
- `Repo Learning`
- `Research Learning`
- `Knowledge Output`

## Requirements

- Add a small API for appending structured entries to the three Memory Surface files.
- Ensure the `.learnings/` directory and expected files are created if missing.
- Allow automatic Memory Writes for Repo Learnings, Research Learnings, and recurring errors.
- Require explicit Primary User confirmation before writing a Working Preference.
- Avoid duplicate or near-duplicate entries when practical.
- Include timestamps and enough context to make each entry useful later.
- Keep `CONTEXT.md` reserved for glossary terms and ADRs reserved for major decisions.

## Acceptance Criteria

- Unit tests cover creating missing memory files, appending each memory type, and routing entries to the correct file.
- Tests cover that Working Preferences are not written unless confirmation is provided.
- The writer never stores secrets or raw API keys.
- Completion Reports can mention when a Memory Write was made.

## Out of Scope

- Global memory outside the Current Repository.
- Vector database or semantic memory.
- Editing old memory entries beyond simple duplicate avoidance.
- Syncing memory across repos or cloud drives.
