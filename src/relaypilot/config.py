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
    allowed_sites: list[str] = field(default_factory=lambda: ["perumal100.github.io"])
    allowed_actions: list[str] = field(
        default_factory=lambda: ["find_newest_pdf", "copy_file", "open_file", "browser_read_status"]
    )
    cloud_planning_enabled: bool = False
    cloud_screen_sharing_enabled: bool = False
    local_model_provider: str | None = None

    @classmethod
    def defaults(cls, downloads: Path, documents: Path) -> "RelaySettings":
        return cls(str(downloads), str(documents))

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
        return Policy(
            (Path(self.downloads),),
            (Path(self.documents),),
            allowed_sites=set(self.allowed_sites),
            allowed_actions=set(self.allowed_actions),
        )


def default_settings_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return base / "RelayPilot" / "settings.json"
