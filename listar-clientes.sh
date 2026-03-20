#!/bin/bash
echo "Clientes activos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for cliente_dir in ~/clientes/sitios/*; do
  if [ -d "$cliente_dir" ]; then
    cliente=$(basename "$cliente_dir")
    compose_file="$cliente_dir/compose.yaml"

    if [ -f "$compose_file" ]; then
      dominio=$(grep "Host" "$compose_file" | head -1 | sed -E 's/.*Host\(`([^`]+)`\).*/\1/')
      status=$(podman ps --filter "name=$cliente" --format "{{.Status}}" | head -1 || echo "Detenido")

      printf "%-20s %-30s %s\n" "$cliente" "$dominio" "$status"
    fi
  fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"