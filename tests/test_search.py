from __future__ import annotations

from datetime import UTC, datetime

import pytest

from agent_harness.search import (
    FakeSearchProvider,
    SearchProviderUnavailable,
    SearchResult,
    compare_sources,
    select_search_provider,
)


def test_fake_search_provider_returns_deterministic_results() -> None:
    retrieved_at = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    expected = [
        SearchResult(
            title="Official docs",
            url="https://docs.example.test/search",
            snippet="The canonical behavior.",
            source_type="official",
            retrieved_at=retrieved_at,
        )
    ]
    provider = FakeSearchProvider({"search provider": expected})

    results = provider.search("search provider")

    assert results == expected


def test_provider_selection_reports_missing_microsoft_backend() -> None:
    with pytest.raises(SearchProviderUnavailable, match="Microsoft hosted web search"):
        select_search_provider("microsoft")


def test_provider_selection_can_use_configured_fake_provider() -> None:
    provider = FakeSearchProvider({})

    selected = select_search_provider("fake", fake_provider=provider)

    assert selected is provider


def test_provider_selection_wraps_microsoft_backend_results() -> None:
    retrieved_at = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)

    def backend(query: str) -> list[dict[str, object]]:
        assert query == "agent framework search"
        return [
            {
                "title": "Agent Framework docs",
                "url": "https://learn.microsoft.com/example",
                "summary": "Microsoft-hosted result.",
                "source_type": "official",
                "retrieved_at": retrieved_at.isoformat(),
            }
        ]

    provider = select_search_provider("microsoft", microsoft_search_backend=backend)

    assert provider.search("agent framework search") == [
        SearchResult(
            title="Agent Framework docs",
            url="https://learn.microsoft.com/example",
            snippet="Microsoft-hosted result.",
            source_type="official",
            retrieved_at=retrieved_at,
        )
    ]


def test_source_comparison_prefers_official_sources() -> None:
    retrieved_at = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    secondary = SearchResult(
        title="Blog summary",
        url="https://blog.example.test/search",
        snippet="A useful but indirect explanation.",
        source_type="secondary",
        retrieved_at=retrieved_at,
    )
    official = SearchResult(
        title="Official docs",
        url="https://docs.example.test/search",
        snippet="The canonical behavior.",
        source_type="official",
        retrieved_at=retrieved_at,
    )

    comparison = compare_sources([secondary, official])

    assert comparison.preferred == official
    assert comparison.sources_used == [official, secondary]
    assert comparison.conflict is None


def test_source_comparison_represents_conflicting_primary_sources() -> None:
    retrieved_at = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    first = SearchResult(
        title="Official docs",
        url="https://docs.example.test/search",
        snippet="The feature is supported.",
        source_type="official",
        retrieved_at=retrieved_at,
    )
    second = SearchResult(
        title="Primary release notes",
        url="https://release.example.test/search",
        snippet="The feature is not supported.",
        source_type="primary",
        retrieved_at=retrieved_at,
    )

    comparison = compare_sources([first, second])

    assert comparison.preferred is None
    assert comparison.conflict is not None
    assert comparison.conflict.sources == [first, second]
    assert "conflicting primary sources" in comparison.conflict.reason
