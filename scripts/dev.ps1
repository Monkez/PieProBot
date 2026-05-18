$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

if (-not (Test-Path ".venv")) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\install.ps1"
}

New-Item -ItemType Directory -Force -Path "logs" | Out-Null

$backend = Start-Process powershell `
    -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$Root\scripts\start_backend.ps1`"" `
    -RedirectStandardOutput "$Root\logs\backend.out.log" `
    -RedirectStandardError "$Root\logs\backend.err.log" `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 2

$frontend = Start-Process powershell `
    -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$Root\scripts\start_frontend.ps1`"" `
    -RedirectStandardOutput "$Root\logs\frontend.out.log" `
    -RedirectStandardError "$Root\logs\frontend.err.log" `
    -WindowStyle Hidden `
    -PassThru

Write-Host "PiePro local dev started."
Write-Host "Backend PID:  $($backend.Id)  http://127.0.0.1:8000"
Write-Host "Frontend PID: $($frontend.Id) http://127.0.0.1:3000/dashboard"
Write-Host "Logs: $Root\logs"
