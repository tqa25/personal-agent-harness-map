from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ISSUES_DIR = Path(".codex") / "issues"


@dataclass(frozen=True)
class LocalIssue:
    id: str
    title: str
    status: str
    path: Path
    content: str


class IssueNotFoundError(ValueError):
    pass


def create_issue(repo_root: Path | str, title: str, body: str) -> LocalIssue:
    root = Path(repo_root)
    issues_dir = root / ISSUES_DIR
    issues_dir.mkdir(parents=True, exist_ok=True)

    issue_id = _next_issue_id(issues_dir)
    path = issues_dir / f"{issue_id}-{_slugify(title)}.md"
    content = f"# {title}\n\nStatus: open\n\n{body.rstrip()}\n"
    path.write_text(content)

    return LocalIssue(
        id=issue_id,
        title=title,
        status="open",
        path=path,
        content=content,
    )


def list_issues(repo_root: Path | str) -> list[LocalIssue]:
    issues_dir = Path(repo_root) / ISSUES_DIR
    if not issues_dir.exists():
        return []

    return [_read_issue(path) for path in sorted(issues_dir.glob("*.md"))]


def show_issue(repo_root: Path | str, issue_ref: str) -> LocalIssue:
    for issue in list_issues(repo_root):
        if issue.id == issue_ref or _path_slug(issue.path) == issue_ref:
            return issue

    raise IssueNotFoundError(f"Local Issue {issue_ref!r} was not found.")


def close_issue(repo_root: Path | str, issue_ref: str) -> LocalIssue:
    return _set_issue_status(repo_root, issue_ref, "closed")


def complete_issue(repo_root: Path | str, issue_ref: str) -> LocalIssue:
    return _set_issue_status(repo_root, issue_ref, "completed")


def _set_issue_status(repo_root: Path | str, issue_ref: str, status: str) -> LocalIssue:
    issue = show_issue(repo_root, issue_ref)
    lines = issue.path.read_text().splitlines(keepends=True)
    updated_lines = []
    status_updated = False

    for line in lines:
        if not status_updated and line.startswith("Status: "):
            newline = "\n" if line.endswith("\n") else ""
            updated_lines.append(f"Status: {status}" + newline)
            status_updated = True
        else:
            updated_lines.append(line)

    if not status_updated:
        insert_at = _status_insert_index(updated_lines)
        updated_lines.insert(insert_at, f"Status: {status}\n\n")

    issue.path.write_text("".join(updated_lines))
    return _read_issue(issue.path)


def _next_issue_id(issues_dir: Path) -> str:
    highest = 0
    for path in issues_dir.glob("*.md"):
        match = re.match(r"^(\d{4})-", path.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{highest + 1:04d}"


def _read_issue(path: Path) -> LocalIssue:
    text = path.read_text()
    title = path.stem
    status = "open"

    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("Status: "):
            status = line.removeprefix("Status: ").strip()

    match = re.match(r"^(\d{4})-", path.name)
    issue_id = match.group(1) if match else path.stem
    return LocalIssue(
        id=issue_id,
        title=title,
        status=status,
        path=path,
        content=text,
    )


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "issue"


def _path_slug(path: Path) -> str:
    match = re.match(r"^\d{4}-(.+)$", path.stem)
    return match.group(1) if match else path.stem


def _status_insert_index(lines: list[str]) -> int:
    if not lines:
        return 0

    if lines[0].startswith("# "):
        index = 1
        while index < len(lines) and lines[index].strip() == "":
            index += 1
        return index

    return 0
