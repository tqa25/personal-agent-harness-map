from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Callable

from agent_harness.config import HarnessConfig
from agent_harness.instructions import GENERAL_AGENT_INSTRUCTIONS
from agent_harness.tools import TOOLS


Tool = Callable[..., object]


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
    FoundryChatClient, AzureCliCredential, create_harness_agent = _load_agent_framework()

    client = FoundryChatClient(
        project_endpoint=config.foundry_project_endpoint,
        model=config.foundry_model,
        credential=AzureCliCredential(),
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


def _load_agent_framework() -> tuple[type[Any], type[Any], Callable[..., Any]]:
    try:
        from agent_framework import create_harness_agent
        from agent_framework.foundry import FoundryChatClient
        from azure.identity import AzureCliCredential
    except ImportError as exc:
        raise RuntimeError(
            "Microsoft Agent Framework dependencies are not installed. "
            "Run `uv sync --extra dev` first."
        ) from exc

    return FoundryChatClient, AzureCliCredential, create_harness_agent
