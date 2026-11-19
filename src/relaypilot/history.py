from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .models import RunResult


class RunHistory:
    """Local-only JSONL history; it deliberately redacts common secret-bearing fragments."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, command: str, result: RunResult) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "at": datetime.now(timezone.utc).isoformat(),
            "command": _redact(command),
            "state": result.state.value,
            "reason": _redact(result.reason or ""),
            "evidence": [_redact(event.evidence) for event in result.events if event.evidence],
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 20) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in reversed(lines) if line.strip()]


def _redact(value: str) -> str:
    return re.sub(r"(?i)\b(password|token|api[_-]?key)\s*[:=]\s*\S+", r"\1=[redacted]", value)
