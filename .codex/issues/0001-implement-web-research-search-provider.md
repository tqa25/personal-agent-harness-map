# Implement Web Research SearchProvider

## Goal

Implement the V1 Web Research capability behind a replaceable `SearchProvider` abstraction.

## Context

The Personal Copilot requires Web Research with Source Comparison. V1 should default to Microsoft hosted web search when available through Microsoft Agent Framework, but research behavior must not be hard-coded to one provider.

Relevant domain terms:

- `Web Research`
- `Search Provider`
- `Source Comparison`
- `Source Conflict`
- `Research Learning`

Relevant ADR:

- `docs/adr/0001-use-replaceable-search-provider.md`

## Requirements

- Add a `SearchProvider` interface or protocol in the Python package.
- Provide a Microsoft-hosted implementation or adapter that works with the current harness path when available.
- Provide a deterministic test/fake provider for unit tests.
- Support research results that include title, URL, snippet or summary, source type, and retrieval timestamp.
- Implement source comparison behavior that can inspect multiple results and prefer official or primary sources.
- Represent source conflicts explicitly instead of silently choosing one source.
- Keep provider selection configurable without changing the copilot's domain behavior.
- Update instructions so the copilot uses Web Research for current facts, external docs, library behavior, and public references.

## Acceptance Criteria

- Unit tests cover provider selection, fake search results, source comparison, and source conflict representation.
- The CLI can report clearly when Web Research is unavailable because provider config is missing.
- The Completion Report for research-backed answers can include sources used and any uncertainty.
- No secrets are committed. Provider credentials, if needed, are read from env or approved `.env.local`.

## Out of Scope

- Browser automation.
- Multi-repo research routing.
- Storing every search result in memory.
- Building a web dashboard for research results.
