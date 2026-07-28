#!/bin/bash
if [ $# -lt 1 ]; then
  echo "Uso: $0 <nombre-cliente>"
  exit 1
fi

CLIENTE_SLUG="$1"
SITIO_DIR="$HOME/clientes/sitios/$CLIENTE_SLUG"

if [ ! -d "$SITIO_DIR" ]; then
  echo "Error: Cliente '$CLIENTE_SLUG' no encontrado"
  exit 1
fi

echo "⚠️  ADVERTENCIA: Esto eliminará el cliente '$CLIENTE_SLUG' y todos sus datos"
read -p "¿Estás seguro? (escribir 'eliminar' para confirmar): " confirmacion

if [ "$confirmacion" != "eliminar" ]; then
  echo "Cancelado"
  exit 0
fi

echo "🗑️  Deteniendo contenedores..."
cd "$SITIO_DIR" && podman-compose down -v

echo "🗑️  Eliminando directorio..."
rm -rf "$SITIO_DIR"

echo "✅ Cliente '$CLIENTE_SLUG' eliminado"