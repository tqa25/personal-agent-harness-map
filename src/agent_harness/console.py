from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from agent_harness.agent import build_agent
from agent_harness.config import HarnessConfig


async def run_console(config: HarnessConfig) -> None:
    agent = build_agent(config)
    session = agent.create_session()

    print("Agent Harness")
    print("Commands: /todos, /mode, /session-export <file>, /session-import <file>, /exit")
    print("Starting in plan mode. The harness mode provider may adjust execution internally.\n")

    while True:
        try:
            user_input = await asyncio.to_thread(input, "you> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        message = user_input.strip()
        if not message:
            continue

        if message == "/exit":
            return

        if message.startswith("/"):
            session = await _handle_command(agent, session, message)
            continue

        await _run_agent_turn(agent, session, message)


def run_console_sync(config: HarnessConfig) -> None:
    asyncio.run(run_console(config))


async def _run_agent_turn(agent: Any, session: Any, message: str) -> None:
    print("agent> ", end="", flush=True)
    response_or_stream = agent.run(message, stream=True, session=session)

    if hasattr(response_or_stream, "__aiter__"):
        last_text = ""
        async for update in response_or_stream:
            text = _extract_text(update)
            if text:
                print(text, end="", flush=True)
                last_text += text
        if not last_text:
            print(_render_object(update), end="", flush=True)  # type: ignore[name-defined]
        print()
        return

    response = await response_or_stream
    print(_extract_text(response) or _render_object(response))


async def _handle_command(agent: Any, session: Any, command: str) -> Any:
    parts = command.split(maxsplit=1)
    name = parts[0]
    argument = parts[1] if len(parts) > 1 else ""

    if name == "/todos":
        print(_format_session_section(session, "todo"))
        return session

    if name == "/mode":
        print(_format_session_section(session, "mode"))
        return session

    if name == "/session-export":
        if not argument:
            print("Usage: /session-export <file>")
            return session
        path = Path(argument).expanduser()
        path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")
        print(f"Exported session to {path}")
        return session

    if name == "/session-import":
        if not argument:
            print("Usage: /session-import <file>")
            return session
        path = Path(argument).expanduser()
        data = json.loads(path.read_text(encoding="utf-8"))
        imported = _session_from_dict(data)
        print(f"Imported session from {path}")
        return imported

    print(f"Unknown command: {name}")
    return session


def _session_from_dict(data: dict[str, Any]) -> Any:
    try:
        from agent_framework._sessions import AgentSession
    except ImportError as exc:
        raise RuntimeError("Could not import AgentSession from Agent Framework.") from exc

    return AgentSession.from_dict(data)


def _format_session_section(session: Any, keyword: str) -> str:
    data = session.to_dict()
    matches = _find_key_matches(data, keyword)
    if not matches:
        return f"No {keyword} state found in the current session."
    return json.dumps(matches, indent=2, ensure_ascii=False)


def _find_key_matches(value: Any, keyword: str) -> list[Any]:
    keyword = keyword.lower()
    matches: list[Any] = []

    if isinstance(value, dict):
        for key, child in value.items():
            if keyword in str(key).lower():
                matches.append({key: child})
            matches.extend(_find_key_matches(child, keyword))
    elif isinstance(value, list):
        for child in value:
            matches.extend(_find_key_matches(child, keyword))

    return matches


def _extract_text(value: Any) -> str:
    for attr in ("text", "content", "message"):
        attr_value = getattr(value, attr, None)
        if isinstance(attr_value, str):
            return attr_value

    if hasattr(value, "to_dict"):
        data = value.to_dict()
        for key in ("text", "content", "message", "value"):
            item = data.get(key)
            if isinstance(item, str):
                return item

    return ""


def _render_object(value: Any) -> str:
    if hasattr(value, "to_dict"):
        return json.dumps(value.to_dict(), indent=2, ensure_ascii=False)
    return str(value)
