# Deployment and trial guide

## Trial the Windows app

1. Clone the `develop` branch and install Python 3.11+.
2. In PowerShell, set `$env:PYTHONPATH = "$PWD\src"`.
3. Run `py -m unittest discover -s tests -v`; the current automated suite should pass all 12 tests.
4. Start the app with `py -m relaypilot.app`. RelayPilot opens a dedicated modern local app window.
5. Approve microphone access only if you choose the Voice control; alternatively, dictate with Wispr into the command composer. Review transcription, then press **Run task** or `Ctrl+Enter`. Confirm the shown evidence path and the copy in Documents.
6. Try `Open Heat-Signal and report the visible status`. It requires network access and only reads the granted site.
7. Use the visible **Stop** control during a run. Test a second monitor and mixed-DPI window discovery separately; that needs an interactive Windows session.

## Package for a Python-equipped Windows PC

Run `powershell -ExecutionPolicy Bypass -File scripts\package.ps1`. This produces `dist\RelayPilot.pyz`, launched with `py dist\RelayPilot.pyz`. It is a portable package, not a signed installer. A signed MSI/EXE remains a release-engineering task because it requires a chosen signing identity and an installer toolchain.

## Publish the synthetic demo on GitHub Pages

1. Keep the repository private unless you explicitly decide the demo may be public.
2. In the repository settings, enable GitHub Pages with **GitHub Actions** as the source. Confirm that your GitHub plan supports Pages for this private repository; otherwise use a separate public demo repository containing only `demo/`.
3. Run the **Deploy demo to GitHub Pages** workflow manually from Actions.
4. GitHub will show the deployment URL in that workflow's environment summary. Verify the page and ensure it remains labeled **simulation**.

The demo includes only synthetic data. Do not add screenshots, credentials, local paths, browser profiles, prompts, or real account data to the Pages artifact.

## Local data location

By default, settings and local run history are stored in `%USERPROFILE%\AppData\Local\RelayPilot`. In managed or sandboxed environments, set `RELAYPILOT_DATA_DIR` before launch to use another user-writable location:

```powershell
$env:RELAYPILOT_DATA_DIR = "C:\RelayPilotData"
py -m relaypilot.app
```
