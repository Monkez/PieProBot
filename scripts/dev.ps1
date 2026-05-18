$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

if (-not (Test-Path ".venv")) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\install.ps1"
}

& ".\.venv\Scripts\piepro.exe" start
