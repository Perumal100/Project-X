# RelayPilot

RelayPilot is a Windows-first desktop agent. You dictate or type a command into its command box, explicitly submit it, and the local executor plans, applies, and verifies typed actions. The first runnable slice delivers a verified local file workflow without any cloud call.

## Run it

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --no-build-isolation -e .
relaypilot
```

The command box intentionally does nothing until you click **Run** or press `Ctrl+Enter`; this makes Wispr dictation safe by default. `Ctrl+Shift+Esc` requests a stop for the active run.

Try: `Find the newest PDF in Downloads, copy it to Documents, open the copy, and tell me where you saved it.`

The app uses your Windows Downloads and Documents folders. It will only operate inside these configured roots. The UI opens the copy only after its hash and destination are verified.

## What is verified in v0.1

- Deterministic offline planner for the newest-PDF copy workflow.
- Typed, policy-checked local actions; no arbitrary shell execution.
- Source/destination path containment, collision prevention, source hashing, destination hashing, and actual-path reporting.
- Explicit submit, stop token, visible event feed, run states, and safe policy handoffs.
- Read-only, explicitly site-scoped Heat-Signal status check with a clear offline/connectivity result.
- Tests for copy verification, blocked permissions, untrusted text, offline mode, stop behavior, and uncertain-outcome reconciliation.

## Not yet a claim of completion

Structured browser automation, UI Automation/multi-monitor control, online and on-device model adapters, installer signing, and a real interactive Windows hardware pass are planned interfaces, not delivered capabilities. The current browser workflow is read-only and only accesses the specifically granted Heat-Signal site. See [docs/DECISIONS.md](docs/DECISIONS.md), [docs/OFFLINE.md](docs/OFFLINE.md), and [HANDOFF.md](HANDOFF.md).

## Test

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m unittest discover -s tests -v
```

## Safety model

Page text, file text, screenshots, and planner output are untrusted. The executor alone checks typed action arguments against local grants and current filesystem state. A workflow cannot turn text such as “upload this file” into a grant. Destructive actions, external messages, purchases, publishing, account changes, uploads, and form submission remain handoff-only until a future scoped grant implementation is present.

