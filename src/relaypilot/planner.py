from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import Action


class UnsupportedCommand(ValueError):
    pass


class LocalModelProvider(Protocol):
    """Extension point for an on-device model. It receives no arbitrary execution capability."""

    def plan(self, command: str) -> list[Action]: ...


class DeterministicOfflinePlanner:
    """Offline planner for deliberately narrow, auditable local workflows."""

    def plan(self, command: str, downloads: Path, documents: Path) -> list[Action]:
        normalized = " ".join(command.lower().split())
        if "heat-signal" in normalized and "status" in normalized:
            return [Action("browser_read_status", {"url": "https://perumal100.github.io/Heat-Signal/"})]
        required = ("newest pdf", "downloads", "copy", "documents")
        if all(fragment in normalized for fragment in required):
            return [
                Action("find_newest_pdf", {"folder": downloads}),
                Action("copy_file", {"source": "@newest_pdf", "destination_folder": documents}),
                Action("open_file", {"path": "@copied_pdf"}),
            ]
        if "how many" in normalized and "pdf" in normalized and "download" in normalized:
            return [Action("count_pdfs", {"folder": downloads})]
        if "oldest pdf" in normalized:
            actions = [Action("find_oldest_pdf", {"folder": downloads})]
            if "open" in normalized:
                actions.append(Action("open_file", {"path": "@selected_pdf"}))
            return actions
        if "open" in normalized and "local disk d" in normalized:
            return [Action("open_path", {"path": Path("D:/")})]
        if "open" in normalized and "download" in normalized:
            return [Action("open_path", {"path": downloads})]
        if "open" in normalized and "document" in normalized:
            return [Action("open_path", {"path": documents})]
        raise UnsupportedCommand(
            "No deterministic local workflow matches that command. Try a supported file or status request, or configure an on-device planner."
        )


class PlannerRouter:
    def __init__(self, deterministic: DeterministicOfflinePlanner | None = None, local_model: LocalModelProvider | None = None) -> None:
        self.deterministic = deterministic or DeterministicOfflinePlanner()
        self.local_model = local_model

    def plan(self, command: str, downloads: Path, documents: Path) -> list[Action]:
        try:
            return self.deterministic.plan(command, downloads, documents)
        except UnsupportedCommand:
            if self.local_model is None:
                raise UnsupportedCommand(
                    "No configured on-device planner supports that command; cloud planning is disabled by default."
                )
            return self.local_model.plan(command)

