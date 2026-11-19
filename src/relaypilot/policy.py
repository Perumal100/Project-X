from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from .models import Action


class PolicyDenied(PermissionError):
    """Raised when a typed action is outside the user's standing grant."""


@dataclass
class Policy:
    readable_roots: tuple[Path, ...]
    writable_roots: tuple[Path, ...]
    allowed_sites: set[str] = field(default_factory=lambda: {"perumal100.github.io"})
    allowed_actions: set[str] = field(
        default_factory=lambda: {
            "find_newest_pdf", "find_oldest_pdf", "count_pdfs", "copy_file", "open_file", "open_path", "browser_read_status"
        }
    )
    allow_open_verified_file: bool = True

    def authorize(self, action: Action) -> None:
        if action.kind not in self.allowed_actions:
            raise PolicyDenied(f"'{action.kind}' is not within a standing grant")
        if action.external_effect:
            raise PolicyDenied("External effects require an explicit handoff")
        if action.kind == "copy_file":
            self._require_within(Path(action.arguments["source"]), self.readable_roots, "source")
            self._require_within(Path(action.arguments["destination"]), self.writable_roots, "destination")
        if action.kind in {"find_newest_pdf", "find_oldest_pdf", "count_pdfs"}:
            self._require_within(Path(action.arguments["folder"]), self.readable_roots, "folder")
        if action.kind in {"open_file", "open_path"}:
            self._require_within(Path(action.arguments["path"]), self.readable_roots, "path")
        if action.kind == "open_file" and not self.allow_open_verified_file:
            raise PolicyDenied("Opening files is not authorized")
        if action.kind == "browser_read_status":
            parsed = urlparse(str(action.arguments["url"]))
            if parsed.scheme != "https" or parsed.hostname not in self.allowed_sites:
                raise PolicyDenied("Browser read is outside the configured HTTPS site grant")

    @staticmethod
    def _require_within(candidate: Path, roots: tuple[Path, ...], label: str) -> None:
        resolved = candidate.resolve(strict=False)
        if not any(_is_relative_to(resolved, root.resolve()) for root in roots):
            raise PolicyDenied(f"{label} is outside configured folders: {candidate}")


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False

