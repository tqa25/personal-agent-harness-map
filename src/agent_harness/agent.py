from __future__ import annotations

import os
from dataclasses import dataclass
from collections.abc import Sequence
from typing import Any, Callable

from agent_harness.autonomy import AutonomyConfig
from agent_harness.autonomy import AutonomySession
from agent_harness.config import HarnessConfig
from agent_harness.instructions import GENERAL_AGENT_INSTRUCTIONS
from agent_harness.memory_surface import MemorySurface
from agent_harness.search import SearchProvider
from agent_harness.search import SearchProviderUnavailable
from agent_harness.search import select_search_provider
from agent_harness.tools import TOOLS


Tool = Callable[..., object]


@dataclass
class AgentRuntime:
    agent: Any
    config: HarnessConfig
    memory_surface: MemorySurface
    autonomy_session: AutonomySession
    search_provider_name: str
    search_provider_available: bool
    search_provider_detail: str
    search_provider: SearchProvider | None = None


def build_agent(
    config: HarnessConfig,
    *,
    instructions: str = GENERAL_AGENT_INSTRUCTIONS,
    tools: Sequence[Tool] = TOOLS,
) -> Any:
    """Create a Microsoft Agent Framework harness agent.

    Imports are deliberately local so unit tests can run without contacting
    Azure or importing optional provider packages.
    """
    OpenAIChatClient, create_harness_agent = _load_agent_framework()

    client = OpenAIChatClient(
        model=config.openrouter_model,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=config.openrouter_base_url,
    )

    return create_harness_agent(
        client=client,
        agent_instructions=instructions,
        tools=list(tools),
        disable_todo=config.disable_todo,
        disable_mode=config.disable_mode,
        disable_memory=config.disable_memory,
        disable_web_search=config.disable_web_search,
    )


def build_runtime(
    config: HarnessConfig,
    *,
    instructions: str = GENERAL_AGENT_INSTRUCTIONS,
    tools: Sequence[Tool] = TOOLS,
    agent_factory: Callable[..., Any] = build_agent,
    fake_search_provider: SearchProvider | None = None,
    microsoft_search_backend: Callable[[str], Sequence[dict[str, object]]] | None = None,
) -> AgentRuntime:
    memory_surface = MemorySurface(config.repository_root)
    autonomy_session = AutonomySession.default(
        AutonomyConfig(default_level=config.default_autonomy_level)
    )
    search_provider, available, detail = resolve_search_provider(
        config,
        fake_search_provider=fake_search_provider,
        microsoft_search_backend=microsoft_search_backend,
    )
    agent = agent_factory(config, instructions=instructions, tools=tools)
    return AgentRuntime(
        agent=agent,
        config=config,
        memory_surface=memory_surface,
        autonomy_session=autonomy_session,
        search_provider_name=config.search_provider,
        search_provider_available=available,
        search_provider_detail=detail,
        search_provider=search_provider,
    )


def resolve_search_provider(
    config: HarnessConfig,
    *,
    fake_search_provider: SearchProvider | None = None,
    microsoft_search_backend: Callable[[str], Sequence[dict[str, object]]] | None = None,
) -> tuple[SearchProvider | None, bool, str]:
    if config.disable_web_search:
        return None, False, "Web Research is disabled by configuration."

    if config.search_provider == "microsoft" and microsoft_search_backend is None:
        return (
            None,
            True,
            "Microsoft hosted web search is enabled and managed by the harness service.",
        )

    try:
        provider = select_search_provider(
            config.search_provider,
            fake_provider=fake_search_provider,
            microsoft_search_backend=microsoft_search_backend,
        )
    except SearchProviderUnavailable as exc:
        return None, False, str(exc)

    return provider, True, f"Search provider ready: {config.search_provider}"


def _load_agent_framework() -> tuple[type[Any], Callable[..., Any]]:
    try:
        from agent_framework import create_harness_agent
        from agent_framework.openai import OpenAIChatClient
    except ImportError as exc:
        raise RuntimeError(
            "Microsoft Agent Framework dependencies are not installed. "
            "Run `uv sync --extra dev` first."
        ) from exc

    return OpenAIChatClient, create_harness_agent
