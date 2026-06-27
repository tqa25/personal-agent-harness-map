from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from agent_harness.autonomy import AutonomyLevel
from agent_harness.autonomy import AutonomyModeError
from agent_harness.autonomy import parse_autonomy_level

DEFAULT_MODEL = "gpt-5.4"
DEFAULT_MEMORY_DIR = "agent-file-memory"
DEFAULT_SEARCH_PROVIDER = "microsoft"


@dataclass(frozen=True)
class HarnessConfig:
    openai_model: str = DEFAULT_MODEL
    openai_base_url: str | None = None
    openai_org_id: str | None = None
    memory_dir: str = DEFAULT_MEMORY_DIR
    repository_root: Path = Path(".")
    search_provider: str = DEFAULT_SEARCH_PROVIDER
    default_autonomy_level: AutonomyLevel = AutonomyLevel.EDIT
    disable_todo: bool = False
    disable_mode: bool = False
    disable_memory: bool = False
    disable_web_search: bool = False

    @classmethod
    def from_env(cls) -> "HarnessConfig":
        try:
            default_autonomy_level = parse_autonomy_level(
                os.getenv("AGENT_DEFAULT_AUTONOMY_LEVEL", AutonomyLevel.EDIT.value)
            )
        except AutonomyModeError as exc:
            raise ConfigError(str(exc)) from exc

        return cls(
            openai_model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
            openai_org_id=os.getenv("OPENAI_ORG_ID") or None,
            memory_dir=os.getenv("AGENT_MEMORY_DIR", DEFAULT_MEMORY_DIR),
            repository_root=Path(os.getenv("AGENT_REPOSITORY_ROOT", ".")).resolve(),
            search_provider=os.getenv("AGENT_SEARCH_PROVIDER", DEFAULT_SEARCH_PROVIDER),
            default_autonomy_level=default_autonomy_level,
            disable_todo=_env_flag("AGENT_DISABLE_TODO"),
            disable_mode=_env_flag("AGENT_DISABLE_MODE"),
            disable_memory=_env_flag("AGENT_DISABLE_MEMORY"),
            disable_web_search=_env_flag("AGENT_DISABLE_WEB_SEARCH"),
        )


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


def _env_flag(name: str) -> bool:
    value = os.getenv(name, "").strip().lower()
    return value in {"1", "true", "yes", "on"}
