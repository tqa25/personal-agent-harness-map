from __future__ import annotations

import argparse
import sys

from agent_harness.config import ConfigError, HarnessConfig
from agent_harness.console import run_console_sync


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
        print(f"Endpoint: {config.foundry_project_endpoint}")
        print(f"Model: {config.foundry_model}")
        print(f"Memory dir: {config.memory_dir}")
        return 0

    try:
        run_console_sync(config)
    except RuntimeError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
