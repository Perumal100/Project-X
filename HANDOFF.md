# RelayPilot handoff

## Current state

The first two RelayPilot milestones were merged through GitHub PR #1. The final trial-baseline additions are on `develop` in GitHub PR #2 for review. The expected command finds the newest `.pdf` under Downloads, copies it into Documents, verifies both hashes, and opens the verified copy on Windows when that action is allowed.

The connected `Open Heat-Signal and report the visible status` workflow is now also available. It is read-only, checks a single granted HTTPS site, and reports a connectivity blocker instead of guessing when offline.

The local settings file makes allowed folders/sites editable, and a local JSONL history records redacted run evidence. `scripts/package.ps1` produces `dist\\RelayPilot.pyz`; `docs/DEPLOYMENT.md` contains the full trial and GitHub Pages process. The interactive synthetic demo is `demo/index.html` and the manual Pages workflow is `.github/workflows/pages.yml`.

Verified in this development environment: 15 automated tests, portable package contents, and a live read-only Heat-Signal status response. The test results are recorded in `docs/DEVELOPMENT_LOG.md`.

The current UI is served locally by `relaypilot.webapp` and launched as an app-style browser window by `relaypilot.app`. It provides optional browser voice capture as transcription only; the user still explicitly runs each task. Latest automated validation: 18 tests. Validate the visual layout and microphone browser prompt on the interactive Windows desktop after updating from `develop`.

Deterministic local file workflows now also cover counting PDFs in Downloads, opening the oldest PDF, opening the latest supported picture in Downloads, and opening approved local folders. File-launch evidence now accurately records the verified target and Windows launch request; it does not claim that an app window became visible. Add a local folder to `readable_folders` in settings before using it; latest automated validation is recorded in the development log.

## Resume steps

1. Run `py -m unittest discover -s tests -v`.
2. Launch with `py -m relaypilot.app` and exercise the command using a non-sensitive test PDF.
3. Add Windows UI Automation behind `DesktopAdapter` and structured browser control behind `BrowserAdapter`; do not weaken `Policy` or expose shell access.
4. Continue committing all source work to `develop` and update PR #2. Merge it into `main` only after review.

## Still unverified on Perumal's PC

- Wispr dictation focus and submit behavior.
- Interactive Windows open action, second monitor, and mixed-DPI UI automation.
- Browser sign-in/MFA handoffs and any online planner/provider.
- Clean-machine packaged installation.
- GitHub Pages availability/deployment for this private repository, which depends on the account's Pages entitlement and an explicit manual workflow run.

