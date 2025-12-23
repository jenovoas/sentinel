#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Starting Sentinel with Ollama (CPU-only profile)"

# Start docker compose with the AI profile (includes ollama and ollama-init)
docker compose --profile ai up -d --build

# Wait for Ollama API to be available
echo "⏳ Waiting for Ollama API (http://localhost:11434/api/tags) ..."
for i in {1..60}; do
  if curl --silent --fail http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is reachable"
    break
  fi
  printf "."
  sleep 2
done

# Wait for backend health (optional)
echo "⏳ Waiting for backend health (http://localhost:8000/health) ..."
for i in {1..60}; do
  if curl --silent --fail http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend is healthy"
    break
  fi
  printf "."
  sleep 2
done

# Open the frontend in the default browser (if available)
FRONTEND_URL="http://localhost:3000"
echo "🌐 Opening frontend at $FRONTEND_URL"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$FRONTEND_URL" >/dev/null 2>&1 || true
elif command -v gnome-open >/dev/null 2>&1; then
  gnome-open "$FRONTEND_URL" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "$FRONTEND_URL" >/dev/null 2>&1 || true
elif command -v python >/dev/null 2>&1; then
  python -m webbrowser "$FRONTEND_URL" >/dev/null 2>&1 || true
else
  echo "⚠️ Could not auto-open the browser. Please open: $FRONTEND_URL"
fi

echo "🎉 Deployment requested. Use 'docker compose ps' to inspect containers and 'docker compose logs -f ollama' to watch model downloads."