from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

from .models import Action
from .policy import Policy


class StopRequested(RuntimeError):
    pass


class LocalExecutor:
    def __init__(self, policy: Policy, stop_requested=lambda: False, opener=None) -> None:
        self.policy = policy
        self.stop_requested = stop_requested
        self.opener = opener or self._default_open

    def execute(self, action: Action, context: dict[str, Path]) -> tuple[str, str]:
        self._check_stop()
        if action.kind == "find_newest_pdf":
            folder = Path(action.arguments["folder"])
            self.policy.authorize(Action("find_newest_pdf"))
            candidates = [p for p in folder.rglob("*.pdf") if p.is_file()]
            if not candidates:
                raise FileNotFoundError(f"No PDF found in {folder}")
            newest = max(candidates, key=lambda item: item.stat().st_mtime)
            context["newest_pdf"] = newest.resolve()
            return (f"Found newest PDF: {newest.name}", str(newest.resolve()))

        if action.kind == "copy_file":
            source = context["newest_pdf"] if action.arguments["source"] == "@newest_pdf" else Path(action.arguments["source"])
            destination_folder = Path(action.arguments["destination_folder"])
            destination = destination_folder / source.name
            self.policy.authorize(Action("copy_file", {"source": source, "destination": destination}))
            self._check_stop()
            if destination.exists():
                raise FileExistsError(f"Destination already exists: {destination}")
            source_hash = _sha256(source)
            shutil.copy2(source, destination)
            self._check_stop()
            destination_hash = _sha256(destination)
            if source_hash != destination_hash:
                destination.unlink(missing_ok=True)
                raise IOError("Verification failed: copied file hash does not match source")
            context["copied_pdf"] = destination.resolve()
            return (f"Copied and verified: {destination.name}", f"sha256={destination_hash}; path={destination.resolve()}")

        if action.kind == "open_file":
            target = context["copied_pdf"] if action.arguments["path"] == "@copied_pdf" else Path(action.arguments["path"])
            self.policy.authorize(Action("open_file"))
            self._check_stop()
            if not target.exists():
                raise FileNotFoundError(f"Verified file no longer exists: {target}")
            self.opener(target)
            return (f"Opened verified copy: {target.name}", str(target.resolve()))
        raise ValueError(f"Unsupported action: {action.kind}")

    def _check_stop(self) -> None:
        if self.stop_requested():
            raise StopRequested("Stop requested; no further input or actions were issued")

    @staticmethod
    def _default_open(path: Path) -> None:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

