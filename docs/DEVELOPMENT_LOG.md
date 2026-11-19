# Sanitized development log

## 2026-11-19 (America/New_York)

### 02:53

- Started RelayPilot from an empty local Git repository on Windows.
- Inspected available runtime: Python 3.14, Node 24, and Git are present; GitHub CLI is unavailable.
- Implemented and tested the first end-to-end deterministic offline file workflow with policy enforcement and verification.
- Created the empty `main` bootstrap and pushed the initial tested RelayPilot source to `develop`. No PR was created and `main` has no application source.
- CI initially failed because the hosted runner does not preinstall `setuptools`; replaced the packaging-dependent test setup with a direct `src`-path test invocation.
- CI passed on `develop` after the correction; local and hosted suites each passed all five tests.

### 03:02

- Added a bounded, read-only Heat-Signal status workflow with executor-side HTTPS allow-list enforcement.
- Added mocked connected-read, offline/connectivity, and ungranted-site regression tests; local suite passed 8 tests.
- Pushed the browser milestone to `develop`; the 8-test local and GitHub Actions suites passed.
- Opened review PR #1 from `develop` to `main`.

### 03:23

- Added configurable local settings, redacted local run history, a typed Windows window/monitor adapter, planner extension interfaces, and bounded timeout reconciliation.
- Added the synthetic interactive demo, manual GitHub Pages workflow, portable zipapp packaging script, and deployment/trial guide.
- Ran and passed 15 automated tests, built and inspected `RelayPilot.pyz`, and completed a live read-only Heat-Signal status trial. The initial restricted-network trial reported a clear connectivity blocker; the permitted live retry returned visible page status.
- Remaining verification is intentionally device/account dependent: real Wispr input, interactive multi-monitor operation, sign-in/MFA handoffs, clean-PC installation, and private GitHub Pages entitlement.

### 03:27

- Observed that PR #1 had been merged externally while the final-baseline commit was in progress. Opened PR #2 for the one remaining `develop` commit and left it unmerged.
- Corrected the engine so configured folder scopes drive both planning and permission checks, then added a regression test.

