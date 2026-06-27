from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from agent_harness.secrets import (
    SecretConfig,
    SecretConfigError,
    SecretWriteDenied,
    redact_secret_values,
    write_env_local,
)


def test_secret_config_reports_missing_required_variables() -> None:
    with pytest.raises(SecretConfigError) as exc_info:
        SecretConfig.from_env(
            ["OPENAI_API_KEY", "SEARCH_PROVIDER_API_KEY"],
            environ={},
        )

    message = str(exc_info.value)
    assert "OPENAI_API_KEY" in message
    assert "SEARCH_PROVIDER_API_KEY" in message
    assert "Set the missing environment variables" in message


def test_secret_config_reads_environment_values_without_repr_leaks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_secret = "model-provider-secret-value"
    search_secret = "search-provider-secret-value"
    monkeypatch.setenv("OPENAI_API_KEY", model_secret)
    monkeypatch.setenv("SEARCH_PROVIDER_API_KEY", search_secret)

    config = SecretConfig.from_env(
        ["OPENAI_API_KEY", "SEARCH_PROVIDER_API_KEY"],
    )

    assert config.value("OPENAI_API_KEY") == model_secret
    assert config.value("SEARCH_PROVIDER_API_KEY") == search_secret
    assert model_secret not in repr(config)
    assert search_secret not in repr(config)
    assert "[REDACTED]" in repr(config)


def test_approved_secret_write_creates_env_local_with_redacted_result(tmp_path) -> None:
    raw_secret = "approved-secret-value"
    env_path = tmp_path / ".env.local"

    result = write_env_local(
        {"OPENAI_API_KEY": raw_secret},
        env_path=env_path,
        approved=True,
    )

    assert env_path.read_text() == "OPENAI_API_KEY=approved-secret-value\n"
    assert result.written_variables == ("OPENAI_API_KEY",)
    assert raw_secret not in str(result)
    assert raw_secret not in repr(result)
    assert "[REDACTED]" in repr(result)


def test_denied_secret_write_does_not_create_env_local(tmp_path) -> None:
    raw_secret = "denied-secret-value"
    env_path = tmp_path / ".env.local"

    with pytest.raises(SecretWriteDenied) as exc_info:
        write_env_local(
            {"OPENAI_API_KEY": raw_secret},
            env_path=env_path,
            approved=False,
        )

    assert not env_path.exists()
    message = str(exc_info.value)
    assert "Primary User approval" in message
    assert "OPENAI_API_KEY" in message
    assert raw_secret not in message


def test_redact_secret_values_scrubs_raw_values_from_output() -> None:
    raw_secret = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"

    output = redact_secret_values(
        f"Request failed with OPENAI_API_KEY={raw_secret}.",
        [raw_secret],
    )

    assert raw_secret not in output
    assert "OPENAI_API_KEY=[REDACTED]" in output


def test_env_local_is_ignored_by_git() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        ["git", "check-ignore", ".env.local"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
