from __future__ import annotations

import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SecretConfig:
    _values: Mapping[str, str]

    @classmethod
    def from_env(
        cls,
        required_variables: Iterable[str],
        *,
        environ: Mapping[str, str] | None = None,
    ) -> "SecretConfig":
        source = os.environ if environ is None else environ
        missing = [name for name in required_variables if not source.get(name)]
        if missing:
            missing_names = ", ".join(missing)
            raise SecretConfigError(
                f"Missing Secret Configuration: {missing_names}. "
                "Set the missing environment variables or write approved secrets "
                "to .env.local."
            )
        return cls({name: source[name] for name in required_variables})

    def value(self, name: str) -> str:
        return self._values[name]

    def __repr__(self) -> str:
        redacted = {name: "[REDACTED]" for name in self._values}
        return f"SecretConfig({redacted!r})"


class SecretConfigError(RuntimeError):
    """Raised when required Secret Configuration is missing or invalid."""


class SecretWriteDenied(RuntimeError):
    """Raised when a Secret Configuration write lacks Primary User approval."""


@dataclass(frozen=True)
class SecretWriteResult:
    path: Path
    written_variables: tuple[str, ...]

    def __repr__(self) -> str:
        return (
            f"SecretWriteResult(path={str(self.path)!r}, "
            f"written_variables={self.written_variables!r}, value='[REDACTED]')"
        )


def write_env_local(
    secrets: Mapping[str, str],
    *,
    env_path: Path,
    approved: bool,
) -> SecretWriteResult:
    if not approved:
        names = ", ".join(secrets)
        raise SecretWriteDenied(
            "Primary User approval is required before writing Secret "
            f"Configuration to .env.local: {names}."
        )

    lines = [f"{name}={value}\n" for name, value in secrets.items()]
    env_path.write_text("".join(lines))
    return SecretWriteResult(
        path=env_path,
        written_variables=tuple(secrets),
    )


def redact_secret_values(text: str, secret_values: Iterable[str]) -> str:
    redacted = text
    for value in secret_values:
        if value:
            redacted = redacted.replace(value, "[REDACTED]")
    return redacted
