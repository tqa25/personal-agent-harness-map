from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_MODEL = "gpt-5.4"
DEFAULT_MEMORY_DIR = "agent-file-memory"


@dataclass(frozen=True)
class HarnessConfig:
    foundry_project_endpoint: str
    foundry_model: str = DEFAULT_MODEL
    memory_dir: str = DEFAULT_MEMORY_DIR
    disable_todo: bool = False
    disable_mode: bool = False
    disable_memory: bool = False
    disable_web_search: bool = False

    @classmethod
    def from_env(cls) -> "HarnessConfig":
        endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        if not endpoint:
            raise ConfigError(
                "FOUNDRY_PROJECT_ENDPOINT is not set. "
                "Set it to your Microsoft Foundry project endpoint."
            )

        return cls(
            foundry_project_endpoint=endpoint,
            foundry_model=os.getenv("FOUNDRY_MODEL", DEFAULT_MODEL),
            memory_dir=os.getenv("AGENT_MEMORY_DIR", DEFAULT_MEMORY_DIR),
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
