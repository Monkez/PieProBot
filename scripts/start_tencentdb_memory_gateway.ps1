param(
    [string]$RepoPath = $env:TENCENTDB_AGENT_MEMORY_HOME,
    [int]$Port = 8420,
    [string]$HostName = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

if (-not $RepoPath) {
    throw "Set TENCENTDB_AGENT_MEMORY_HOME or pass -RepoPath pointing to Tencent/TencentDB-Agent-Memory."
}

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Repo = Resolve-Path $RepoPath

$env:TDAI_GATEWAY_HOST = $HostName
$env:TDAI_GATEWAY_PORT = [string]$Port
$env:TDAI_DATA_DIR = Join-Path $Root "runtime\tencentdb-agent-memory"

Set-Location $Repo

if (-not (Test-Path "node_modules")) {
    npm install
}

node --import tsx src/gateway/server.ts

