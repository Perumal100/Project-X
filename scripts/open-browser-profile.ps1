param(
    [string]$Url = "https://perumal100.github.io/Heat-Signal/"
)

$ErrorActionPreference = "Stop"
$profile = Join-Path $env:LOCALAPPDATA "RelayPilot\browser-profile"
New-Item -ItemType Directory -Force -Path $profile | Out-Null
Start-Process "chrome.exe" "--user-data-dir=`"$profile`"", $Url
Write-Host "Opened the user-managed RelayPilot browser profile. Sign-in, MFA, CAPTCHAs, and browser dialogs require your direct action."
