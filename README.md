# RelayPilot

RelayPilot is a Windows-first voice-capable desktop agent. Its polished local workspace opens in an app-style browser window: dictate or type a command, explicitly submit it, and the local executor plans, applies, and verifies typed actions. The first runnable slice delivers a verified local file workflow without any cloud call.

## Run it

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --no-build-isolation -e .
relaypilot
```

The command box intentionally does nothing until you click **Run task** or press `Ctrl+Enter`; this makes Wispr or browser voice capture safe by default. Browser voice capture needs a user-approved microphone prompt; it only transcribes into the box and never auto-runs a task.

Try: `Find the newest PDF in Downloads, copy it to Documents, open the copy, and tell me where you saved it.`

The app uses your Windows Downloads and Documents folders. It will only operate inside these configured roots. The UI opens the copy only after its hash and destination are verified.

## What is verified in v0.1

- Deterministic offline planner for the newest-PDF copy workflow.
- Typed, policy-checked local actions; no arbitrary shell execution.
- Source/destination path containment, collision prevention, source hashing, destination hashing, and actual-path reporting.
- Explicit submit, stop token, visible event feed, run states, and safe policy handoffs.
- Read-only, explicitly site-scoped Heat-Signal status check with a clear offline/connectivity result.
- User-editable local settings, local run history with basic secret redaction, Windows window/monitor discovery, and bounded timeout reconciliation.
- A modern local app workspace with live evidence, activity history, visible active grants, and optional browser voice capture.
- Tests for copy verification, blocked permissions, untrusted text, offline mode, stop behavior, and uncertain-outcome reconciliation.

## Not yet a claim of completion

Structured browser automation, UI Automation/multi-monitor control, online and on-device model adapters, installer signing, and a real interactive Windows hardware pass are planned interfaces, not delivered capabilities. The current browser workflow is read-only and only accesses the specifically granted Heat-Signal site. See [docs/DECISIONS.md](docs/DECISIONS.md), [docs/OFFLINE.md](docs/OFFLINE.md), and [HANDOFF.md](HANDOFF.md).

Settings are kept locally at `%USERPROFILE%\AppData\Local\RelayPilot\settings.json`; browser profile and run history also stay there and are ignored by Git. Set `RELAYPILOT_DATA_DIR` if your organization requires another local data location. This settings file is intentionally limited to scopes and provider choices—never secrets or session data.

## Test

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m unittest discover -s tests -v
```

## Safety model

Page text, file text, screenshots, and planner output are untrusted. The executor alone checks typed action arguments against local grants and current filesystem state. A workflow cannot turn text such as “upload this file” into a grant. Destructive actions, external messages, purchases, publishing, account changes, uploads, and form submission remain handoff-only until a future scoped grant implementation is present.

