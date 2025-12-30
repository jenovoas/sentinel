#!/bin/bash
# Sentinel Cortex - BPF Map Poisoning Audit Script
# Propósito: Verificar la integridad de los descriptores de archivos eBPF.

echo "🔍 Iniciando Auditoría de Mapas eBPF..."

BPF_FS="/sys/fs/bpf"

if [ ! -d "$BPF_FS" ]; then
    echo "❌ Error: El sistema de archivos BPF ($BPF_FS) no está montado."
    exit 1
fi

echo "📂 Listando permisos en $BPF_FS:"
ls -la "$BPF_FS"

# Verificar si hay permisos de escritura para "others"
WRITABLE_OTHERS=$(find "$BPF_FS" -perm -o+w)

if [ -n "$WRITABLE_OTHERS" ]; then
    echo "⚠️ ALERTA DE SEGURIDAD: Se detectaron descriptores de mapas BPF con permisos de escritura para todos:"
    echo "$WRITABLE_OTHERS"
    echo "❌ AUDITORÍA FALLIDA: Riesgo de Map Poisoning alto."
else
    echo "✅ ÉXITO: No se detectaron mapas BPF con permisos de escritura globales."
fi

# Verificar SELinux (si está presente)
if command -v getenforce >/dev/null 2>&1; then
    echo "🛡️ Estado de SELinux: $(getenforce)"
    ls -laZ "$BPF_FS"
else
    echo "ℹ️ SELinux no detectado en este entorno."
fi

echo "🏁 Auditoría de Mapas completada."
