from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    source_type: str
    retrieved_at: datetime


@dataclass(frozen=True)
class SourceComparison:
    preferred: SearchResult | None
    sources_used: list[SearchResult]
    conflict: "SourceConflict | None" = None


@dataclass(frozen=True)
class SourceConflict:
    sources: list[SearchResult]
    reason: str


class SearchProvider(Protocol):
    def search(self, query: str) -> list[SearchResult]:
        """Return Web Research results for a query."""


class SearchProviderUnavailable(RuntimeError):
    """Raised when Web Research is configured but no backend is available."""


class FakeSearchProvider:
    def __init__(self, results_by_query: dict[str, list[SearchResult]]) -> None:
        self._results_by_query = results_by_query

    def search(self, query: str) -> list[SearchResult]:
        return list(self._results_by_query.get(query, []))


class MicrosoftHostedSearchProvider:
    def __init__(self, search_backend: Callable[[str], Sequence[Mapping[str, Any]]]) -> None:
        self._search_backend = search_backend

    def search(self, query: str) -> list[SearchResult]:
        retrieved_at = datetime.now(UTC)
        return [
            SearchResult(
                title=str(result.get("title", "")),
                url=str(result.get("url", "")),
                snippet=str(result.get("snippet", result.get("summary", ""))),
                source_type=str(result.get("source_type", "secondary")),
                retrieved_at=_coerce_datetime(result.get("retrieved_at"), retrieved_at),
            )
            for result in self._search_backend(query)
        ]


def select_search_provider(
    provider_name: str,
    *,
    fake_provider: SearchProvider | None = None,
    microsoft_search_backend: Callable[[str], Sequence[Mapping[str, Any]]] | None = None,
) -> SearchProvider:
    normalized_name = provider_name.strip().lower()
    if normalized_name == "fake":
        if fake_provider is None:
            raise SearchProviderUnavailable(
                "Fake search provider is unavailable because no fake provider was provided."
            )
        return fake_provider

    if normalized_name == "microsoft":
        if microsoft_search_backend is None:
            raise SearchProviderUnavailable(
                "Microsoft hosted web search is unavailable because no search backend "
                "was provided."
            )
        return MicrosoftHostedSearchProvider(microsoft_search_backend)

    raise SearchProviderUnavailable(
        f"Search provider '{provider_name}' is not configured."
    )


def compare_sources(results: Sequence[SearchResult]) -> SourceComparison:
    sources_used = sorted(results, key=_source_rank)
    primary_sources = [
        result for result in sources_used if result.source_type.lower() in {"official", "primary"}
    ]
    primary_claims = {_normalize_claim(result.snippet) for result in primary_sources}
    if len(primary_claims) > 1:
        return SourceComparison(
            preferred=None,
            sources_used=sources_used,
            conflict=SourceConflict(
                sources=primary_sources,
                reason="Sources contain conflicting primary sources.",
            ),
        )

    preferred = sources_used[0] if sources_used else None
    return SourceComparison(preferred=preferred, sources_used=sources_used)


def _source_rank(result: SearchResult) -> tuple[int, datetime, str]:
    source_type_rank = {
        "official": 0,
        "primary": 0,
        "secondary": 1,
    }.get(result.source_type.lower(), 2)
    return (source_type_rank, result.retrieved_at, result.url)


def _normalize_claim(snippet: str) -> str:
    return " ".join(snippet.lower().split())


def _coerce_datetime(value: object, fallback: datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return fallback
