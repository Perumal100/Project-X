# RelayPilot handoff

## Current state

The first two RelayPilot milestones are on `develop` and proposed for review in GitHub PR #1. The expected command finds the newest `.pdf` under Downloads, copies it into Documents, verifies both hashes, and opens the verified copy on Windows when that action is allowed.

The connected `Open Heat-Signal and report the visible status` workflow is now also available. It is read-only, checks a single granted HTTPS site, and reports a connectivity blocker instead of guessing when offline.

## Resume steps

1. Run `py -m unittest discover -s tests -v`.
2. Launch with `py -m relaypilot.app` and exercise the command using a non-sensitive test PDF.
3. Add Windows UI Automation behind `DesktopAdapter` and structured browser control behind `BrowserAdapter`; do not weaken `Policy` or expose shell access.
4. Continue committing all source work to `develop` and update PR #1. Merge it into `main` only after review.

## Still unverified on Perumal's PC

- Wispr dictation focus and submit behavior.
- Interactive Windows open action, second monitor, and mixed-DPI UI automation.
- Browser sign-in/MFA handoffs and any online planner/provider.
- Clean-machine packaged installation.

