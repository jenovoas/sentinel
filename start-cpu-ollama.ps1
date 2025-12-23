param(
  [string]$FrontendUrl = "http://localhost:3000"
)

# Root-level wrapper that calls `scripts\start-cpu-ollama.ps1`
$scriptDir = Join-Path $PSScriptRoot 'scripts'
$helper = Join-Path $scriptDir 'start-cpu-ollama.ps1'

if (Test-Path $helper) {
    Write-Host "Invoking helper: $helper"
    & $helper -FrontendUrl $FrontendUrl
} else {
    Write-Host "⚠️ helper script not found at $helper" -ForegroundColor Yellow
}
