param(
  [string]$FrontendUrl = "http://localhost:3000"
)

Write-Host "🔧 Starting Sentinel with Ollama (CPU-only profile)"

# Start docker compose with the AI profile (includes ollama and ollama-init)
docker compose --profile ai up -d --build

# Wait for Ollama API to be available
Write-Host "⏳ Waiting for Ollama API (http://localhost:11434/api/tags) ..."
for ($i = 0; $i -lt 60; $i++) {
  try {
    Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 | Out-Null
    Write-Host "✅ Ollama is reachable"
    break
  } catch {
    Start-Sleep -Seconds 2
  }
}

# Wait for backend health
Write-Host "⏳ Waiting for backend health (http://localhost:8000/health) ..."
for ($i = 0; $i -lt 60; $i++) {
  try {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 | Out-Null
    Write-Host "✅ Backend is healthy"
    break
  } catch {
    Start-Sleep -Seconds 2
  }
}

Write-Host "🌐 Opening frontend at $FrontendUrl"
Start-Process $FrontendUrl

Write-Host "🎉 Deployment requested. Check 'docker compose ps' and 'docker compose logs -f ollama' to follow progress."