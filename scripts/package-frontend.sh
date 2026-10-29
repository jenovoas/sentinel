#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Uso: $0 <ruta-archivo-salida>" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend_dir="$repo_root/frontend"
standalone_dir="$frontend_dir/.next/standalone"
output_path="$1"

if [[ "$output_path" != /* ]]; then
  output_path="$repo_root/$output_path"
fi

if [[ "$output_path" == "$repo_root"/* ]]; then
  echo "El bundle debe guardarse fuera del repositorio." >&2
  exit 2
fi

if [[ ! -f "$standalone_dir/server.js" || ! -d "$frontend_dir/.next/static" ]]; then
  echo "Falta el build standalone; ejecuta npm ci y npm run build en frontend/." >&2
  exit 1
fi

mkdir -p "$standalone_dir/.next/static" "$standalone_dir/.next/cache" "$standalone_dir/public" "$(dirname "$output_path")"
cp -a "$frontend_dir/.next/static/." "$standalone_dir/.next/static/"
cp -a "$frontend_dir/public/." "$standalone_dir/public/"

tar -czf "$output_path" -C "$standalone_dir" .
(cd "$(dirname "$output_path")" && sha256sum "$(basename "$output_path")" > "$(basename "$output_path").sha256")
echo "Bundle: $output_path"
echo "SHA-256: $output_path.sha256"
