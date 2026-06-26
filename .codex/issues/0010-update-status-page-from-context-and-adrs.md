# Update Status Page from CONTEXT and ADRs

## Goal

Update the static Status Page so it reflects the current Personal Copilot scope, glossary, ADRs, and V1 completion criteria.

## Context

The current `index.html` explains the initial harness scaffold. Since then, the domain language and architecture decisions have been clarified in `CONTEXT.md` and `docs/adr/`. The Status Page should not mislead the Primary User about what the system is becoming.

Relevant domain terms:

- `Status Page`
- `Status Page Update`
- `V1 Scope`
- `V1 Complete`
- `Current Repository`
- `Search Provider`
- `Memory Surface`
- `Autonomy Level`
- `Backlog`

## Requirements

- Update `index.html` to explain the Personal Copilot V1 scope.
- Show what is already implemented versus what is planned in Local Issues.
- Reflect that V1 is limited to the Current Repository.
- Reflect that Web Research uses a replaceable Search Provider.
- Reflect that `.learnings/` is the Memory Surface.
- Reflect that `.codex/issues/` is the Backlog.
- Reflect Autonomy Levels: Edit Mode, Deliver Mode, Auto Mode.
- Mention the ADRs and their decisions in plain language.
- Keep the page static and GitHub Pages compatible.

## Acceptance Criteria

- The page no longer describes the system as only a generic harness scaffold.
- The page includes the current V1 completion criteria.
- The page includes the current missing capabilities as roadmap items.
- The page renders on desktop and mobile without overlapping text.
- GitHub Pages can serve the updated page from `index.html`.

## Out of Scope

- Building an interactive app UI.
- Auto-generating the page from markdown.
- Adding authentication.
- Replacing the CLI Work Surface.
