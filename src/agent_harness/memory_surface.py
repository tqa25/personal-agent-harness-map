from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

_MEMORY_TYPES = {
    "repo_learning": ("LEARNINGS.md", "Repo Learning"),
    "research_learning": ("LEARNINGS.md", "Research Learning"),
    "working_preference": ("LEARNINGS.md", "Working Preference"),
    "recurring_error": ("ERRORS.md", "Recurring Error"),
    "feature_request": ("FEATURE_REQUESTS.md", "Feature Request"),
}


@dataclass(frozen=True)
class MemoryWriteResult:
    written: bool
    path: Path
    reason: str | None = None


class MemorySurface:
    def __init__(self, repository_root: Path | str) -> None:
        self.repository_root = Path(repository_root)
        self.memory_dir = self.repository_root / ".learnings"

    def write(
        self,
        memory_type: str,
        text: str,
        *,
        context: str,
        timestamp: datetime | None = None,
        confirmed: bool = False,
    ) -> MemoryWriteResult:
        filename, title = _MEMORY_TYPES[memory_type]
        self._ensure_files()
        path = self.memory_dir / filename
        if memory_type == "working_preference" and not confirmed:
            return MemoryWriteResult(
                written=False,
                path=path,
                reason="working_preference_requires_confirmation",
            )
        safe_text = self._redact_secrets(text)
        safe_context = self._redact_secrets(context)
        if self._contains_duplicate(path, safe_text):
            return MemoryWriteResult(written=False, path=path, reason="duplicate")
        written_at = timestamp or datetime.now(UTC)
        entry = self._format_entry(
            title=title,
            text=safe_text,
            context=safe_context,
            timestamp=written_at,
        )
        with path.open("a", encoding="utf-8") as file:
            file.write(entry)
        return MemoryWriteResult(written=True, path=path)

    def _ensure_files(self) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        for name in ("LEARNINGS.md", "ERRORS.md", "FEATURE_REQUESTS.md"):
            path = self.memory_dir / name
            if not path.exists():
                heading = name.removesuffix(".md").replace("_", " ").title()
                path.write_text(f"# {heading}\n\n", encoding="utf-8")

    def _format_entry(
        self, *, title: str, text: str, context: str, timestamp: datetime
    ) -> str:
        return f"## {timestamp.isoformat()} - {title}\n\n{text}\n\nContext: {context}\n\n"

    def _contains_duplicate(self, path: Path, text: str) -> bool:
        return self._normalize(text) in self._normalize(path.read_text(encoding="utf-8"))

    def _normalize(self, text: str) -> str:
        without_possessives = re.sub(r"'s\b", "", text.lower())
        return re.sub(r"[^a-z0-9]+", "", without_possessives)

    def _redact_secrets(self, text: str) -> str:
        redacted = re.sub(
            r"\b([A-Z][A-Z0-9_]*(?:API_KEY|TOKEN|SECRET|PASSWORD))\s*=\s*\S+",
            r"\1=[REDACTED]",
            text,
        )
        redacted = re.sub(
            r"\bBearer\s+[A-Za-z0-9_\-]{20,}", "Bearer [REDACTED]", redacted
        )
        redacted = re.sub(
            r"\b(?:sk|sk-proj|ghp)_[A-Za-z0-9_\-]{20,}", "[REDACTED]", redacted
        )
        redacted = re.sub(r"\bsk-proj-[A-Za-z0-9_\-]{20,}", "[REDACTED]", redacted)
        return redacted
