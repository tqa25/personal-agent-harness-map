from __future__ import annotations

import pytest

from agent_harness.config import ConfigError, HarnessConfig


def test_config_requires_foundry_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)

    with pytest.raises(ConfigError, match="FOUNDRY_PROJECT_ENDPOINT"):
        HarnessConfig.from_env()


def test_config_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.delenv("FOUNDRY_MODEL", raising=False)

    config = HarnessConfig.from_env()

    assert config.foundry_project_endpoint == "https://example.test"
    assert config.foundry_model == "gpt-5.4"
    assert config.disable_todo is False
    assert config.disable_web_search is False


def test_config_reads_feature_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("AGENT_DISABLE_TODO", "true")
    monkeypatch.setenv("AGENT_DISABLE_WEB_SEARCH", "1")

    config = HarnessConfig.from_env()

    assert config.disable_todo is True
    assert config.disable_web_search is True
