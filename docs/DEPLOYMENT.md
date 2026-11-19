# Deployment and trial guide

## Trial the Windows app

1. Clone the `develop` branch and install Python 3.11+.
2. In PowerShell, set `$env:PYTHONPATH = "$PWD\src"`.
3. Run `py -m unittest discover -s tests -v`; the current automated suite should pass all 12 tests.
4. Start the app with `py -m relaypilot.app`.
5. Put a harmless PDF in Downloads, dictate or type the documented command, then press `Ctrl+Enter`. Confirm the shown evidence path and the copy in Documents.
6. Try `Open Heat-Signal and report the visible status`. It requires network access and only reads the granted site.
7. Press `Ctrl+Shift+Esc` during a run to request a stop. Test a second monitor and mixed-DPI window discovery separately; that needs an interactive Windows session.

## Package for a Python-equipped Windows PC

Run `powershell -ExecutionPolicy Bypass -File scripts\package.ps1`. This produces `dist\RelayPilot.pyz`, launched with `py dist\RelayPilot.pyz`. It is a portable package, not a signed installer. A signed MSI/EXE remains a release-engineering task because it requires a chosen signing identity and an installer toolchain.

## Publish the synthetic demo on GitHub Pages

1. Keep the repository private unless you explicitly decide the demo may be public.
2. In the repository settings, enable GitHub Pages with **GitHub Actions** as the source. Confirm that your GitHub plan supports Pages for this private repository; otherwise use a separate public demo repository containing only `demo/`.
3. Run the **Deploy demo to GitHub Pages** workflow manually from Actions.
4. GitHub will show the deployment URL in that workflow's environment summary. Verify the page and ensure it remains labeled **simulation**.

The demo includes only synthetic data. Do not add screenshots, credentials, local paths, browser profiles, prompts, or real account data to the Pages artifact.
