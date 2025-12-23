#!/bin/bash
# Poblar whitelist usando bpftool con flag correcto

echo "🔐 Poblando whitelist del eBPF LSM (v2)..."
echo "======================================"

# Comandos básicos permitidos
COMMANDS=(
    "ls"
    "cat"
    "pwd"
    "date"
)

# Encontrar el ID del map
MAP_ID=$(sudo bpftool map list | grep whitelist_map | awk '{print $1}' | cut -d: -f1)

if [ -z "$MAP_ID" ]; then
    echo "❌ Error: No se encontró whitelist_map"
    exit 1
fi

echo "✅ Map ID: $MAP_ID"
echo ""

# Poblar con comandos
for cmd in "${COMMANDS[@]}"; do
    # Crear key de 64 bytes (comando + padding)
    key_hex=$(printf "%-64s" "$cmd" | xxd -p -c 256)
    
    # Valor: 01 (allowed)
    value_hex="01"
    
    # Intentar agregar (usando any flag para crear si no existe)
    sudo bpftool map update id $MAP_ID \
        key hex $key_hex \
        value hex $value_hex \
        any 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ $cmd"
    else
        echo "⚠️  $cmd (puede que ya exista)"
    fi
done

echo ""
echo "======================================"
echo "✅ Intentado poblar ${#COMMANDS[@]} comandos"
echo ""
echo "📊 Verificar contenido del map:"
echo "   sudo bpftool map dump id $MAP_ID"
