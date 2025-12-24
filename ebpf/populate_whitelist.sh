#!/bin/bash
# Poblar whitelist usando bpftool con flag correcto

echo "🔐 Poblando whitelist del eBPF LSM (v2)..."
echo "======================================"

# Comandos básicos permitidos (Paths completos requeridos por el nuevo eBPF)
COMMANDS=(
    "/usr/bin/bash"
    "/usr/bin/sh"
    "/usr/bin/ls"
    "/usr/bin/cat"
    "/usr/bin/pwd"
    "/usr/bin/date"
    "/usr/bin/sudo"
    "/usr/bin/bpftool"
    "/usr/bin/rm"
    "/usr/bin/ps"
    "/usr/bin/grep"
    "/usr/bin/awk"
    "/usr/bin/sed"
    "/usr/bin/python3"
    "/usr/bin/make"
    "/usr/bin/clang"
    "/usr/bin/llvm-strip"
    "/usr/bin/xxd"
    "/usr/sbin/ip"
    "/usr/sbin/ss"
)

# Encontrar el ID del map (ahora buscamos por nombre exacto y tipo)
MAP_ID=$(sudo bpftool map list | grep -E "name whitelist_map" | awk '{print $1}' | cut -d: -f1)

if [ -z "$MAP_ID" ]; then
    echo "❌ Error: No se encontró whitelist_map. ¿Está el eBPF LSM cargado?"
    exit 1
fi

echo "✅ Map ID: $MAP_ID"
echo ""

# Poblar con comandos
for cmd in "${COMMANDS[@]}"; do
    # Crear key de 256 bytes (comando + padding) - Coincide con struct en guardian_alpha_lsm.c
    key_hex=$(printf "%-256s" "$cmd" | xxd -p -c 512)
    
    # Valor: 01 (allowed) - 1 byte para __u8
    value_hex="01"
    
    # Intentar agregar
    sudo bpftool map update id $MAP_ID \
        key hex $key_hex \
        value hex $value_hex \
        any
    
    if [ $? -eq 0 ]; then
        echo "✅ $cmd"
    else
        echo "❌ Falló: $cmd"
    fi
done

echo ""
echo "======================================"
echo "✅ Intentado poblar ${#COMMANDS[@]} comandos"
echo ""
echo "📊 Verificar contenido del map:"
echo "   sudo bpftool map dump id $MAP_ID"
