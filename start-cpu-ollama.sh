#!/usr/bin/env bash
set -euo pipefail

# Root-level wrapper that calls the project's helper script
SCRIPT_DIR="$(dirname "$0")/scripts"

if [ -x "$SCRIPT_DIR/start-cpu-ollama.sh" ]; then
  "$SCRIPT_DIR/start-cpu-ollama.sh"
else
  echo "⚠️ helper script not executable or not found at $SCRIPT_DIR/start-cpu-ollama.sh"
  echo "Trying to run it with bash..."
  bash "$SCRIPT_DIR/start-cpu-ollama.sh"
fi
