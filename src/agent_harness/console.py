from __future__ import annotations

import asyncio
import json
import re
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from agent_harness.agent import AgentRuntime
from agent_harness.agent import build_runtime
from agent_harness.autonomy import AutonomyModeError
from agent_harness.autonomy import handle_autonomy_command
from agent_harness.config import HarnessConfig
from agent_harness.backlog import close_issue
from agent_harness.backlog import complete_issue
from agent_harness.backlog import create_issue
from agent_harness.backlog import list_issues
from agent_harness.backlog import show_issue
from agent_harness.intake import TaskType
from agent_harness.intake import classify_task
from agent_harness.memory_surface import MemoryWriteResult
from agent_harness.planning import PlanApprovalSession
from agent_harness.planning import assess_task_for_plan_approval
from agent_harness.planning import build_plan_approval_request
from agent_harness.reports import CompletionReport
from agent_harness.reports import DeliveryAction
from agent_harness.reports import MemoryWrite
from agent_harness.verification import run_verification


async def run_console(config: HarnessConfig) -> None:
    runtime = build_runtime(config)
    state = ConsoleState(
        session=runtime.agent.create_session(),
        autonomy_level=runtime.autonomy_session.level.value,
    )

    print("Personal Copilot")
    print(
        "Commands: /todos, /mode, /autonomy, /issues, /approve, /reject, "
        "/memory-confirm, /session-export, /session-import, /exit"
    )
    print(f"Web Research: {runtime.search_provider_detail}\n")

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

        state, outputs = await handle_console_input(runtime, state, message)
        for output in outputs:
            print(output)


def run_console_sync(config: HarnessConfig) -> None:
    asyncio.run(run_console(config))


@dataclass
class PendingMemoryWrite:
    memory_type: str
    text: str
    context: str


@dataclass
class ConsoleState:
    session: Any
    autonomy_level: str = "edit"
    pending_plan: PlanApprovalSession | None = None
    pending_task: str | None = None
    pending_memory: PendingMemoryWrite | None = None
    last_approved_plan: str | None = None

    def to_dict(self) -> dict[str, Any]:
        state = {
            "autonomy_level": self.autonomy_level,
            "pending_task": self.pending_task,
            "last_approved_plan": self.last_approved_plan,
        }
        if self.pending_memory is not None:
            state["pending_memory"] = asdict(self.pending_memory)
        if self.pending_plan is not None:
            state["pending_plan"] = {
                "task": self.pending_plan.request.task,
                "affected_areas": list(self.pending_plan.request.affected_areas),
                "verification": list(self.pending_plan.request.verification),
                "expected_output": self.pending_plan.request.expected_output,
                "state": self.pending_plan.state.value,
                "approved_plan_text": self.pending_plan.approved_plan_text,
                "rejection_reason": self.pending_plan.rejection_reason,
            }
        return state

    @classmethod
    def from_dict(cls, session: Any, data: dict[str, Any]) -> "ConsoleState":
        state = cls(
            session=session,
            autonomy_level=data.get("autonomy_level", "edit"),
            pending_task=data.get("pending_task"),
            last_approved_plan=data.get("last_approved_plan"),
        )
        pending_memory = data.get("pending_memory")
        if pending_memory:
            state.pending_memory = PendingMemoryWrite(**pending_memory)

        pending_plan = data.get("pending_plan")
        if pending_plan:
            request = build_plan_approval_request(
                pending_plan["task"],
                affected_areas=tuple(pending_plan["affected_areas"]),
                verification=tuple(pending_plan["verification"]),
                expected_output=pending_plan["expected_output"],
            )
            plan_session = PlanApprovalSession(request)
            plan_session.state = type(plan_session.state)(pending_plan["state"])
            plan_session.approved_plan_text = pending_plan["approved_plan_text"]
            plan_session.rejection_reason = pending_plan["rejection_reason"]
            state.pending_plan = plan_session

        return state


async def handle_console_input(
    runtime: AgentRuntime,
    state: ConsoleState,
    message: str,
) -> tuple[ConsoleState, list[str]]:
    if message.startswith("/"):
        return await _handle_command(runtime, state, message)

    classification = classify_task(message)
    if classification.requires_clarification:
        return state, [classification.clarification_question or "Task is ambiguous."]

    if classification.task_type is TaskType.LOCAL_ISSUE_WORK:
        issue = create_issue(
            runtime.config.repository_root,
            _title_from_task(message),
            f"Created from task intake: {message}",
        )
        return state, [f"Created Local Issue {issue.id}: {issue.title}"]

    if classification.task_type is TaskType.MEMORY_WORK:
        return _handle_memory_task(runtime, state, message)

    decision = assess_task_for_plan_approval(
        message,
        autonomy_level=runtime.autonomy_session.level,
    )
    if decision.requirement.value == "required":
        request = build_plan_approval_request(
            message,
            affected_areas=("current repository",),
            verification=("repository verification if files change",),
            expected_output="Completion Report",
        )
        state.pending_plan = PlanApprovalSession(request)
        state.pending_task = message
        return state, [request.render(), "Use /approve to continue or /reject <reason>."]

    report = await _execute_task(runtime, state, message, classification.task_type)
    return state, [report.render()]


async def _handle_command(
    runtime: AgentRuntime,
    state: ConsoleState,
    command: str,
) -> tuple[ConsoleState, list[str]]:
    parts = command.split(maxsplit=1)
    name = parts[0]
    argument = parts[1] if len(parts) > 1 else ""

    if name == "/todos":
        return state, [_format_session_section(state.session, "todo")]

    if name == "/mode":
        return state, [_format_session_section(state.session, "mode")]

    if name == "/autonomy":
        try:
            output = handle_autonomy_command(runtime.autonomy_session, command)
        except AutonomyModeError as exc:
            return state, [str(exc)]
        state.autonomy_level = runtime.autonomy_session.level.value
        return state, [output]

    if name == "/approve":
        if state.pending_plan is None or state.pending_task is None:
            return state, ["No pending plan approval."]
        state.pending_plan.approve()
        state.last_approved_plan = state.pending_plan.approved_plan_text
        task = state.pending_task
        state.pending_task = None
        state.pending_plan = None
        report = await _execute_task(runtime, state, task, TaskType.TECHNICAL_WORK)
        return state, [report.render()]

    if name == "/reject":
        if state.pending_plan is None:
            return state, ["No pending plan approval."]
        reason = argument or "Rejected by Primary User."
        state.pending_plan.reject(reason)
        state.pending_plan = None
        state.pending_task = None
        return state, [f"Plan rejected: {reason}"]

    if name == "/memory-confirm":
        if state.pending_memory is None:
            return state, ["No pending memory write."]
        result = runtime.memory_surface.write(
            state.pending_memory.memory_type,
            state.pending_memory.text,
            context=state.pending_memory.context,
            confirmed=True,
        )
        state.pending_memory = None
        return state, [_render_memory_result(result)]

    if name == "/memory-cancel":
        if state.pending_memory is None:
            return state, ["No pending memory write."]
        state.pending_memory = None
        return state, ["Pending memory write canceled."]

    if name == "/issues":
        return state, [_handle_issue_command(runtime.config.repository_root, argument)]

    if name == "/session-export":
        if not argument:
            return state, ["Usage: /session-export <file>"]
        path = Path(argument).expanduser()
        payload = {
            "agent_session": _session_to_dict(state.session),
            "console_state": state.to_dict(),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return state, [f"Exported session to {path}"]

    if name == "/session-import":
        if not argument:
            return state, ["Usage: /session-import <file>"]
        path = Path(argument).expanduser()
        data = json.loads(path.read_text(encoding="utf-8"))
        if "agent_session" in data:
            imported_session = _session_from_dict(data["agent_session"])
            imported_state = ConsoleState.from_dict(imported_session, data["console_state"])
            return imported_state, [f"Imported session from {path}"]
        imported_session = _session_from_dict(data)
        return ConsoleState(session=imported_session), [f"Imported session from {path}"]

    return state, [f"Unknown command: {name}"]


def _session_from_dict(data: dict[str, Any]) -> Any:
    try:
        from agent_framework._sessions import AgentSession
    except ImportError as exc:
        if isinstance(data, dict):
            return data
        raise RuntimeError("Could not import AgentSession from Agent Framework.") from exc

    return AgentSession.from_dict(data)


def _session_to_dict(session: Any) -> dict[str, Any]:
    if hasattr(session, "to_dict"):
        return session.to_dict()
    if isinstance(session, dict):
        return session
    raise TypeError("Session cannot be serialized to a dictionary.")


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


async def _execute_task(
    runtime: AgentRuntime,
    state: ConsoleState,
    message: str,
    task_type: TaskType | None,
) -> CompletionReport:
    summary = await _run_agent_turn(runtime.agent, state.session, message)
    verifications = []
    risks: list[str] = []
    memory_writes: list[MemoryWrite] = []

    if task_type is TaskType.TECHNICAL_WORK:
        verification_summary = run_verification(runtime.config.repository_root)
        verifications = verification_summary.report_runs
        risks.extend(verification_summary.risks)

    if task_type is TaskType.WEB_RESEARCH and not runtime.search_provider_available:
        risks.append(runtime.search_provider_detail)

    return CompletionReport(
        summary=summary or f"Handled task: {message}",
        approved_plan=state.last_approved_plan,
        verifications=verifications,
        memory_writes=memory_writes,
        delivery_actions=[
            DeliveryAction(
                name="delivery",
                status="skipped",
                detail=(
                    "Delivery Actions require deliver mode, auto mode, "
                    "or explicit approval."
                ),
            )
        ]
        if "commit" in message.lower() or "push" in message.lower()
        else [],
        risks=risks,
    )


async def _run_agent_turn(agent: Any, session: Any, message: str) -> str:
    response_or_stream = agent.run(message, stream=True, session=session)

    if hasattr(response_or_stream, "__aiter__"):
        last_text = ""
        async for update in response_or_stream:
            text = _extract_text(update)
            if text:
                last_text += text
        if last_text:
            return last_text
        return _render_object(update)  # type: ignore[name-defined]

    response = await response_or_stream
    return _extract_text(response) or _render_object(response)


def _handle_memory_task(
    runtime: AgentRuntime,
    state: ConsoleState,
    message: str,
) -> tuple[ConsoleState, list[str]]:
    lower = message.lower()
    if "prefer" in lower or "preference" in lower:
        state.pending_memory = PendingMemoryWrite(
            memory_type="working_preference",
            text=message,
            context="Requested from task intake.",
        )
        return state, ["Working Preference needs confirmation. Use /memory-confirm."]

    result = runtime.memory_surface.write(
        "repo_learning",
        message,
        context="Captured from task intake.",
    )
    return state, [_render_memory_result(result)]


def _render_memory_result(result: MemoryWriteResult) -> str:
    if result.written:
        return f"Memory written to {result.path}"
    return f"Memory write skipped: {result.reason}"


def _title_from_task(task: str) -> str:
    cleaned = re.sub(r"^(create|add|open)\s+(a\s+)?local issue\s+for\s+", "", task, flags=re.I)
    cleaned = cleaned.strip().rstrip(".")
    return cleaned[:1].upper() + cleaned[1:] if cleaned else "New local issue"


def _handle_issue_command(repository_root: Path, argument: str) -> str:
    if not argument:
        issues = list_issues(repository_root)
        if not issues:
            return "No Local Issues."
        return "\n".join(f"{issue.id} {issue.status} {issue.title}" for issue in issues)

    parts = argument.split(maxsplit=2)
    action = parts[0]

    if action == "list":
        issues = list_issues(repository_root)
        if not issues:
            return "No Local Issues."
        return "\n".join(f"{issue.id} {issue.status} {issue.title}" for issue in issues)

    if action == "show" and len(parts) >= 2:
        issue = show_issue(repository_root, parts[1])
        return issue.content

    if action == "close" and len(parts) >= 2:
        issue = close_issue(repository_root, parts[1])
        return f"Closed Local Issue {issue.id}: {issue.title}"

    if action == "complete" and len(parts) >= 2:
        issue = complete_issue(repository_root, parts[1])
        return f"Completed Local Issue {issue.id}: {issue.title}"

    if action == "create" and len(parts) >= 3:
        issue = create_issue(repository_root, parts[1], parts[2])
        return f"Created Local Issue {issue.id}: {issue.title}"

    return "Usage: /issues [list|show <id>|close <id>|complete <id>|create <title> <body>]"
