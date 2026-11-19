from __future__ import annotations

from pathlib import Path

from .models import Action


class UnsupportedCommand(ValueError):
    pass


class DeterministicOfflinePlanner:
    """Offline planner for deliberately narrow, auditable local workflows."""

    def plan(self, command: str, downloads: Path, documents: Path) -> list[Action]:
        normalized = " ".join(command.lower().split())
        required = ("newest pdf", "downloads", "copy", "documents")
        if not all(fragment in normalized for fragment in required):
            raise UnsupportedCommand(
                "Offline mode currently supports the newest-PDF Downloads-to-Documents workflow."
            )
        return [
            Action("find_newest_pdf", {"folder": downloads}),
            Action("copy_file", {"source": "@newest_pdf", "destination_folder": documents}),
            Action("open_file", {"path": "@copied_pdf"}),
        ]

