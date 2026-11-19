from __future__ import annotations

import ctypes
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DesktopWindow:
    handle: int
    title: str
    monitor: int | None
    dpi: int | None


class WindowsDesktopAdapter:
    """Read and focus windows through typed Windows APIs; no planner shell access."""

    def list_windows(self) -> list[DesktopWindow]:
        if os.name != "nt":
            return []
        user32 = ctypes.windll.user32
        windows: list[DesktopWindow] = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def visitor(handle: int, _parameter: int) -> bool:
            if not user32.IsWindowVisible(handle):
                return True
            length = user32.GetWindowTextLengthW(handle)
            if not length:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(handle, buffer, len(buffer))
            monitor = user32.MonitorFromWindow(handle, 2)
            dpi = user32.GetDpiForWindow(handle) if hasattr(user32, "GetDpiForWindow") else None
            windows.append(DesktopWindow(int(handle), buffer.value, int(monitor) or None, dpi))
            return True

        user32.EnumWindows(callback_type(visitor), 0)
        return windows

    def focus_verified(self, handle: int) -> bool:
        if os.name != "nt":
            return False
        user32 = ctypes.windll.user32
        user32.SetForegroundWindow(handle)
        return int(user32.GetForegroundWindow()) == handle
