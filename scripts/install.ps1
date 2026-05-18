$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

if (-not (Test-Path ".venv")) {
    $python = $env:PYTHON
    if (-not $python) {
        $python = "python"
    }
    & $python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\pip.exe" install -e ".[test]"

Set-Location (Join-Path $Root "frontend")
npm install

Write-Host "Install complete."
