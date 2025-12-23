$ApiUrl = "http://localhost:8000/api/v1/ai/query"
$Prompt = "Escribe una línea que diga: Hola desde Sentinel (prueba automática)."

Write-Host "🧪 Testing AI endpoint: $ApiUrl"

try {
    $payload = @{ prompt = $Prompt; max_tokens = 50; temperature = 0.3 } | ConvertTo-Json
    $resp = Invoke-RestMethod -Uri $ApiUrl -Method Post -Body $payload -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Response:" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 5
} catch {
    Write-Host "❌ Request failed. Ensure backend and Ollama are up." -ForegroundColor Red
    exit 1
}