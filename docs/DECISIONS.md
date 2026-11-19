# Engineering decisions

## 2026-11-19 00:00 America/New_York — initial slice

- **Stack:** Python standard library plus Tkinter. This is immediately runnable on the inspected Windows host (Python 3.14) and keeps the first slice dependency-free.
- **Boundary:** planner emits only `find_newest_pdf`, `copy_file`, and `open_file`; executor validates permissions and paths. No planner can execute a shell command.
- **Offline first:** the initial file workflow has no HTTP or model dependency. Flexible planners will be adapters with explicit cloud/offline configuration.
- **Permissions:** Downloads read, Documents write, and opening a verified result are narrowly modeled grants. External effects are denied by default and must hand off.
- **Connected reads:** Heat-Signal is the sole allow-listed browser site in this milestone. The executor, not the planner or page, validates its HTTPS host before opening a bounded read-only request.
- **Local state:** editable scopes and run history are local under `%LOCALAPPDATA%\\RelayPilot`; history redacts common secret patterns and none of it is committed to Git.
- **Reliability:** timeout handling uses reconciliation before a maximum of one retry. The generic utility is ready for actions with external effects; current local copy checks its hash directly.
- **Delivery:** `scripts/package.ps1` produces a Python zipapp. A signed installer is deliberately not fabricated because it requires a real signing identity and installer toolchain.

