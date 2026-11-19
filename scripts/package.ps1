param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\dist")
)

$ErrorActionPreference = "Stop"
$source = Join-Path $PSScriptRoot "..\src"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
py -m zipapp $source -m "relaypilot.app:main" -o (Join-Path $OutputDirectory "RelayPilot.pyz")
Write-Host "Created $OutputDirectory\RelayPilot.pyz"
Write-Host "Run it with: py $OutputDirectory\RelayPilot.pyz"
