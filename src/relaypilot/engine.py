from __future__ import annotations

import threading
from pathlib import Path

from .executor import LocalExecutor, StopRequested
from .models import Event, RunResult, RunState
from .planner import DeterministicOfflinePlanner, UnsupportedCommand
from .policy import Policy, PolicyDenied


class RelayEngine:
    def __init__(self, downloads: Path, documents: Path, *, opener=None) -> None:
        self.downloads, self.documents = downloads, documents
        self._stop = threading.Event()
        self.planner = DeterministicOfflinePlanner()
        self.policy = Policy((downloads,), (documents,))
        self.opener = opener

    def request_stop(self) -> None:
        self._stop.set()

    def run(self, command: str) -> RunResult:
        self._stop.clear()
        events: list[Event] = [Event("Run started", "Explicit submit received; offline planner selected.")]
        try:
            plan = self.planner.plan(command, self.downloads, self.documents)
            executor = LocalExecutor(self.policy, self._stop.is_set, self.opener)
            context: dict[str, Path] = {}
            for action in plan:
                message, evidence = executor.execute(action, context)
                events.append(Event(message, evidence))
            saved = context.get("copied_pdf")
            return RunResult(RunState.COMPLETED, events, saved_path=saved)
        except StopRequested as error:
            events.append(Event("Run stopped", str(error)))
            return RunResult(RunState.STOPPED, events, reason=str(error))
        except PolicyDenied as error:
            events.append(Event("Permission handoff required", str(error)))
            return RunResult(RunState.HANDOFF, events, reason=str(error))
        except (UnsupportedCommand, FileNotFoundError, FileExistsError, IOError, ValueError) as error:
            events.append(Event("Run blocked", str(error)))
            return RunResult(RunState.BLOCKED, events, reason=str(error))
        except Exception as error:  # UI reports unexpected failures without hiding them.
            events.append(Event("Run failed", repr(error)))
            return RunResult(RunState.FAILED, events, reason=str(error))

