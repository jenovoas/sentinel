@echo off
set API_URL=http://localhost:8000/api/v1/ai/query
set PROMPT=Escribe una línea que diga: Hola desde Sentinel (prueba automática).

powershell -NoProfile -ExecutionPolicy Bypass -Command "try{ $payload = @{ prompt = '%PROMPT%'; max_tokens = 50; temperature = 0.3 } | ConvertTo-Json; Invoke-RestMethod -Uri '%API_URL%' -Method Post -Body $payload -ContentType 'application/json'} catch { Write-Error 'Request failed. Ensure backend and Ollama are up.'; exit 1 }"
