from __future__ import annotations

import argparse
import sys

from agent_harness.config import ConfigError, HarnessConfig
from agent_harness.console import run_console_sync
from agent_harness.secrets import SecretConfig
from agent_harness.secrets import SecretConfigError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Python agent harness.")
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate environment configuration and exit without starting the console.",
    )
    args = parser.parse_args(argv)

    try:
        config = HarnessConfig.from_env()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if args.check_config:
        print("Configuration OK")
        print(f"Model: {config.openai_model}")
        print(f"Base URL: {config.openai_base_url or 'default'}")
        print(f"Org ID: {config.openai_org_id or 'default'}")
        print(f"Repository root: {config.repository_root}")
        print(f"Memory dir: {config.memory_dir}")
        print(f"Search provider: {config.search_provider}")
        print(f"Default autonomy: {config.default_autonomy_level.value}")
        _print_secret_status(config)
        return 0

    try:
        run_console_sync(config)
    except RuntimeError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def _print_secret_status(config: HarnessConfig) -> None:
    required_variables = ["OPENAI_API_KEY"]
    if config.search_provider not in {"microsoft", "fake"}:
        required_variables.append("SEARCH_PROVIDER_API_KEY")

    try:
        SecretConfig.from_env(required_variables)
    except SecretConfigError as exc:
        print(f"Secret status: {exc}")
        return

    print("Secret status: configured")
