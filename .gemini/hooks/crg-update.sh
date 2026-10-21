#!/usr/bin/env bash
# code-review-graph: incremental update after write/replace (Gemini CLI hook)
# Must output ONLY JSON on stdout. Low-noise: no systemMessage.
set -euo pipefail

cat > /dev/null || true

# Sin el binario no hay nada que actualizar (laptop sin entorno completo).
if ! command -v code-review-graph >/dev/null 2>&1; then
  echo '{"suppressOutput": true}'
  exit 0
fi

# El repo se resuelve con git: la ruta cambia entre laptop (Proyectos) y fenix.
repo="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
code-review-graph update --skip-flows --repo "$repo" >/dev/null 2>&1 || true
echo '{"suppressOutput": true}'
exit 0
