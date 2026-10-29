#!/usr/bin/env bash
# code-review-graph: session start status (Gemini CLI hook)
# Must output ONLY JSON on stdout. Logs go to stderr. Never blocks the session.
set -euo pipefail

cat > /dev/null || true

# Sin el binario no hay estado que reportar (laptop sin entorno completo).
if ! command -v code-review-graph >/dev/null 2>&1; then
  echo '{"suppressOutput": true}'
  exit 0
fi

# El repo se resuelve con git: la ruta cambia entre laptop (Proyectos) y fenix.
repo="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
msg="$(code-review-graph status --repo "$repo" 2>&1 | head -n 1 || true)"

CRG_MSG="$msg" python3 -c '
import json,os
m=os.environ.get("CRG_MSG","")
print(json.dumps({"systemMessage":m,"suppressOutput":True}))
' 2>/dev/null || echo '{"suppressOutput": true}'
exit 0
