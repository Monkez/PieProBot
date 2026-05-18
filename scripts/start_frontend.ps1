$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:NEXT_PUBLIC_API_BASE = "http://127.0.0.1:8000"
Set-Location (Join-Path $Root "frontend")

npm run dev -- -p 3000

