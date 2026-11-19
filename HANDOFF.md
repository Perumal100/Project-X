# RelayPilot handoff

## Current state

First end-to-end offline file workflow is implemented locally. The expected command finds the newest `.pdf` under Downloads, copies it into Documents, verifies both hashes, and opens the verified copy on Windows when that action is allowed.

## Resume steps

1. Run `py -m unittest discover -s tests -v`.
2. Launch with `py -m relaypilot.app` and exercise the command using a non-sensitive test PDF.
3. Add Windows UI Automation behind `DesktopAdapter` and Playwright behind `BrowserAdapter`; do not weaken `Policy` or expose shell access.
4. Continue committing all source work to `develop`. Open a PR to `main` only when you are ready to review and merge.

## Still unverified on Perumal's PC

- Wispr dictation focus and submit behavior.
- Interactive Windows open action, second monitor, and mixed-DPI UI automation.
- Browser sign-in/MFA handoffs and any online planner/provider.
- Clean-machine packaged installation.

