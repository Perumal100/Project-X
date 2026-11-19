from __future__ import annotations

import json
import shutil
import subprocess
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any

from .config import RelaySettings, default_settings_path
from .engine import RelayEngine
from .history import RunHistory


class RelayService:
    """Local-only façade shared by the modern UI and executor."""

    def __init__(self, settings_path: Path | None = None) -> None:
        self.settings_path = settings_path or default_settings_path()
        fallback = RelaySettings.defaults(Path.home() / "Downloads", Path.home() / "Documents")
        self.settings = RelaySettings.load(self.settings_path, fallback)
        if not self.settings_path.exists():
            self.settings.save(self.settings_path)
        self.history = RunHistory(self.settings_path.with_name("history.jsonl"))
        self.engine = RelayEngine(Path(self.settings.downloads), Path(self.settings.documents), settings=self.settings, history=self.history)
        self._run_lock = threading.Lock()

    def run(self, command: str) -> dict[str, Any]:
        if not command.strip():
            return {"state": "blocked", "reason": "Enter a command, then explicitly submit it.", "events": []}
        if not self._run_lock.acquire(blocking=False):
            return {"state": "blocked", "reason": "A run is already active. Stop it or wait for completion.", "events": []}
        try:
            result = self.engine.run(command)
            return {
                "state": result.state.value,
                "reason": result.reason,
                "saved_path": str(result.saved_path) if result.saved_path else None,
                "events": [{"message": event.message, "evidence": event.evidence} for event in result.events],
            }
        finally:
            self._run_lock.release()

    def stop(self) -> dict[str, str]:
        self.engine.request_stop()
        return {"status": "Stop requested. No further actions will be issued."}

    def snapshot(self) -> dict[str, Any]:
        return {
            "folders": {"downloads": self.settings.downloads, "documents": self.settings.documents},
            "sites": self.settings.allowed_sites,
            "history": self.history.recent(8),
            "settings_path": str(self.settings_path),
        }


def make_handler(service: RelayService):
    class RelayHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path in {"/", "/index.html"}:
                self._send_bytes(HTTPStatus.OK, "text/html; charset=utf-8", _ui_bytes())
            elif self.path == "/api/snapshot":
                self._send_json(HTTPStatus.OK, service.snapshot())
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            payload = self._body_json()
            if self.path == "/api/run":
                self._send_json(HTTPStatus.OK, service.run(str(payload.get("command", ""))))
            elif self.path == "/api/stop":
                self._send_json(HTTPStatus.OK, service.stop())
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

        def _body_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            try:
                return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            except json.JSONDecodeError:
                return {}

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            self._send_bytes(status, "application/json; charset=utf-8", json.dumps(payload).encode("utf-8"))

        def _send_bytes(self, status: HTTPStatus, content_type: str, payload: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, _format: str, *_args: object) -> None:
            return

    return RelayHandler


def _ui_bytes() -> bytes:
    return files("relaypilot.ui").joinpath("index.html").read_bytes()


def open_app_window(url: str) -> None:
    chrome = shutil.which("chrome") or shutil.which("chrome.exe")
    if chrome:
        subprocess.Popen([chrome, f"--app={url}"], close_fds=True)  # noqa: S603
    else:
        webbrowser.open(url)


def serve(service: RelayService | None = None, *, open_window: bool = True) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(service or RelayService()))
    if open_window:
        open_app_window(f"http://127.0.0.1:{server.server_port}")
    return server


def main() -> None:
    server = serve()
    print(f"RelayPilot is running locally at http://127.0.0.1:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
