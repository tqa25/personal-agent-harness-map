from __future__ import annotations

import pytest

from agent_harness.config import ConfigError, HarnessConfig
from agent_harness.autonomy import AutonomyLevel


def test_config_uses_openai_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_ORG_ID", raising=False)

    config = HarnessConfig.from_env()

    assert config.openai_model == "gpt-5.4"
    assert config.openai_base_url is None
    assert config.openai_org_id is None
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
