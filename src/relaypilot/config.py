from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .policy import Policy


@dataclass
class RelaySettings:
    """Local, user-editable settings. Secrets and browser sessions never live here."""

    downloads: str
    documents: str
    readable_folders: list[str] = field(default_factory=list)
    allowed_sites: list[str] = field(default_factory=lambda: ["perumal100.github.io"])
    allowed_actions: list[str] = field(
        default_factory=lambda: [
            "find_newest_pdf", "find_oldest_pdf", "count_pdfs", "copy_file", "open_file", "open_path", "browser_read_status"
        ]
    )
    cloud_planning_enabled: bool = False
    cloud_screen_sharing_enabled: bool = False
    local_model_provider: str | None = None

    @classmethod
    def defaults(cls, downloads: Path, documents: Path) -> "RelaySettings":
        return cls(str(downloads), str(documents), readable_folders=[str(downloads), str(documents)])

    @classmethod
    def load(cls, path: Path, fallback: "RelaySettings") -> "RelaySettings":
        if not path.exists():
            return fallback
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        temporary.replace(path)

    def policy(self) -> Policy:
        readable = self.readable_folders or [self.downloads, self.documents]
        return Policy(
            tuple(Path(path) for path in readable),
            (Path(self.documents),),
            allowed_sites=set(self.allowed_sites),
            allowed_actions=set(self.allowed_actions),
        )


def default_settings_path() -> Path:
    override = os.environ.get("RELAYPILOT_DATA_DIR")
    if override:
        return Path(override) / "settings.json"
    profile = Path(os.environ.get("USERPROFILE", Path.home()))
    return profile / "AppData" / "Local" / "RelayPilot" / "settings.json"
