from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext, ttk

from .config import RelaySettings, default_settings_path
from .engine import RelayEngine
from .history import RunHistory


class RelayPilotApp(ttk.Frame):
    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root, padding=20)
        self.root = root
        downloads = Path(os.environ.get("USERPROFILE", Path.home())) / "Downloads"
        documents = Path.home() / "Documents"
        self.settings_path = default_settings_path()
        fallback = RelaySettings.defaults(downloads, documents)
        self.settings = RelaySettings.load(self.settings_path, fallback)
        if not self.settings_path.exists():
            self.settings.save(self.settings_path)
        history_path = self.settings_path.with_name("history.jsonl")
        self.history = RunHistory(history_path)
        self.engine = RelayEngine(downloads, documents, settings=self.settings, history=self.history)
        self.status = tk.StringVar(value="Ready — dictation is text only until you explicitly submit.")
        self.command = tk.StringVar()
        self._build()
        root.bind("<Control-Return>", self._submit)
        root.bind("<Control-Shift-Escape>", self._stop)

    def _build(self) -> None:
        self.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="RelayPilot", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(self, text="Type or dictate, then explicitly submit.").grid(row=1, column=0, sticky="w", pady=(0, 10))
        entry = ttk.Entry(self, textvariable=self.command, font=("Segoe UI", 11))
        entry.grid(row=2, column=0, sticky="ew")
        entry.focus_set()
        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, sticky="w", pady=10)
        ttk.Button(buttons, text="Run (Ctrl+Enter)", command=self._submit).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Stop (Ctrl+Shift+Esc)", command=self._stop).grid(row=0, column=1)
        ttk.Button(buttons, text="Permissions", command=self._show_permissions).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(buttons, text="History", command=self._show_history).grid(row=0, column=3, padx=(8, 0))
        ttk.Label(self, textvariable=self.status).grid(row=4, column=0, sticky="w")
        self.feed = scrolledtext.ScrolledText(self, height=18, state="disabled", wrap="word")
        self.feed.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        self.rowconfigure(5, weight=1)

    def _submit(self, _event=None) -> str:
        command = self.command.get().strip()
        if not command:
            self.status.set("Enter a command, then explicitly submit it.")
            return "break"
        self.status.set("Running locally…")
        threading.Thread(target=self._run, args=(command,), daemon=True).start()
        return "break"

    def _run(self, command: str) -> None:
        result = self.engine.run(command)
        self.root.after(0, lambda: self._show(result))

    def _show(self, result) -> None:
        self.status.set(f"{result.state.value.title()}: {result.reason or 'verified'}")
        self.feed.configure(state="normal")
        for event in result.events:
            self.feed.insert("end", f"• {event.message}\n  {event.evidence}\n")
        self.feed.insert("end", "\n")
        self.feed.configure(state="disabled")
        self.feed.see("end")

    def _stop(self, _event=None) -> str:
        self.engine.request_stop()
        self.status.set("Stop requested; RelayPilot will issue no further actions.")
        return "break"

    def _show_permissions(self) -> None:
        self.feed.configure(state="normal")
        self.feed.insert(
            "end",
            "• Local permission settings\n"
            f"  Downloads read: {self.settings.downloads}\n"
            f"  Documents write: {self.settings.documents}\n"
            f"  Browser read sites: {', '.join(self.settings.allowed_sites)}\n"
            f"  Edit/revoke scopes in: {self.settings_path}\n\n",
        )
        self.feed.configure(state="disabled")
        self.feed.see("end")

    def _show_history(self) -> None:
        records = self.history.recent()
        self.feed.configure(state="normal")
        self.feed.insert("end", "• Recent local runs\n")
        if records:
            for record in records:
                self.feed.insert("end", f"  {record['at']} — {record['state']}: {record['command']}\n")
        else:
            self.feed.insert("end", "  No prior local runs.\n")
        self.feed.insert("end", "\n")
        self.feed.configure(state="disabled")
        self.feed.see("end")


def main() -> None:
    root = tk.Tk()
    root.title("RelayPilot")
    root.geometry("760x520")
    RelayPilotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

