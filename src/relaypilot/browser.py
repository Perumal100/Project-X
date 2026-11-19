from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .config import default_settings_path


@dataclass(frozen=True)
class BrowserHandoff:
    url: str
    reason: str
    profile_path: Path


class BrowserProfile:
    """Owns only a local profile location; the user completes sign-in/MFA/CAPTCHA."""

    def __init__(self, path: Path | None = None) -> None:
        default = default_settings_path().with_name("browser-profile")
        self.path = path or default

    def prepare(self) -> Path:
        self.path.mkdir(parents=True, exist_ok=True)
        return self.path

    def handoff_for_authentication(self, url: str, reason: str) -> BrowserHandoff:
        return BrowserHandoff(url=url, reason=reason, profile_path=self.prepare())
