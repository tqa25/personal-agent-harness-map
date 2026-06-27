from __future__ import annotations

import pytest

from agent_harness.config import ConfigError, HarnessConfig
from agent_harness.autonomy import AutonomyLevel


def test_config_uses_openrouter_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)

    config = HarnessConfig.from_env()

    assert config.openrouter_model == "~openai/gpt-latest"
    assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
    assert config.default_autonomy_level is AutonomyLevel.EDIT
    assert config.disable_todo is False
    assert config.disable_web_search is False


def test_config_reads_feature_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_DISABLE_TODO", "true")
    monkeypatch.setenv("AGENT_DISABLE_WEB_SEARCH", "1")

    config = HarnessConfig.from_env()

    assert config.disable_todo is True
    assert config.disable_web_search is True


def test_config_rejects_invalid_autonomy_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_DEFAULT_AUTONOMY_LEVEL", "ship")

    with pytest.raises(ConfigError, match="Invalid autonomy mode 'ship'"):
        HarnessConfig.from_env()
