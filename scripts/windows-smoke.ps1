param(
    [string]$DownloadDirectory = (Join-Path $env:USERPROFILE "Downloads"),
    [string]$DocumentDirectory = [Environment]::GetFolderPath("MyDocuments")
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = (Join-Path $PSScriptRoot "..\src")
py -m unittest discover -s tests -v
Write-Host "Tests passed. Launch with: py -m relaypilot.app"
Write-Host "Manual check: dictate into the command box, then press Ctrl+Enter to explicitly submit."
Write-Host "Configured roots: $DownloadDirectory -> $DocumentDirectory"

