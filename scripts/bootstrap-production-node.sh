#!/bin/sh
# ==============================================================================
# Sentinel Platform — Script de Bootstrap Reproducible para Nodo Alpine Linux
# ==============================================================================
# Propósito: Automatizar la preparación y arranque completo de un nodo
# conforme a la especificación canónica en OpenSpec:
# - specs/sentinel/alpine-deployment/spec.md
# - specs/sentinel/openrc-daemons/spec.md
# ==============================================================================

set -eu

echo "=========================================================="
echo "🚀 Sentinel: Iniciando Bootstrap de Nodo (Alpine Linux)"
echo "=========================================================="

# 1. Validación de Sistema Operativo
if [ ! -f /etc/alpine-release ]; then
    echo "❌ ERROR: Este script está diseñado exclusivamente para Alpine Linux." >&2
    exit 1
fi

ALPINE_VERSION=$(cat /etc/alpine-release)
echo "ℹ️ Sistema detectado: Alpine Linux $ALPINE_VERSION"

# 2. Instalación de Dependencias del Sistema
echo "📦 Instalando dependencias de sistema con apk..."
apk update
apk add --no-cache \
    build-base \
    cargo \
    rust \
    clang \
    llvm \
    linux-headers \
    bpftool \
    libbpf-dev \
    docker \
    docker-cli-compose \
    nginx \
    curl \
    jq \
    coreutils

# 3. Habilitar servicios base de infraestructura
rc-update add docker boot || true
rc-service docker start || true

# 4. Creación de Directorios Canónicos de Runtime
echo "📁 Configurando directorios de runtime y logs..."
mkdir -p /var/log/sentinel
mkdir -p /var/lib/sentinel/backups
mkdir -p /var/lib/sentinel/soma
mkdir -p /run/soma
mkdir -p /run/sentinel

chmod 0750 /var/log/sentinel
chmod 0750 /var/lib/sentinel/backups
chmod 0750 /run/soma

# 5. Compilación de Artefactos Release en Rust
echo "⚙️ Compilando workspace de Rust en modo --release..."
cargo build --release --workspace

# 6. Instalación de Binarios en /usr/local/bin
echo "📥 Instalando binarios en /usr/local/bin/..."
install -m 0755 target/release/sentinel-cortex /usr/local/bin/sentinel-cortex
if [ -f target/release/qhc_agent ]; then
    install -m 0755 target/release/qhc_agent /usr/local/bin/qhc_agent
fi
if [ -f target/release/sentinel-verifier ]; then
    install -m 0755 target/release/sentinel-verifier /usr/local/bin/sentinel-verifier
fi
if [ -f target/release/sentinel_tui ]; then
    install -m 0755 target/release/sentinel_tui /usr/local/bin/sentinel_tui
fi

# 7. Instalación y Registro de Servicios OpenRC
echo "🔌 Instalando servicios en /etc/init.d/ y registrando en runlevel default..."
for service in sentinel-cortex sentinel-qhc-agent sentinel-verifier sentinel-stack sentinel-ebpf-load; do
    if [ -f "openrc/$service" ]; then
        install -m 0755 "openrc/$service" "/etc/init.d/$service"
        rc-update add "$service" default || true
        echo "   ✅ Servicio registrado: $service"
    fi
done

# 8. Carga de Programas eBPF Ring-0
if [ -x /etc/init.d/sentinel-ebpf-load ]; then
    echo "🛡️ Cargando guardianes eBPF en Ring-0..."
    rc-service sentinel-ebpf-load restart || true
fi

# 9. Arranque de Daemons Nativos
echo "🔄 Iniciando daemons de Sentinel..."
rc-service sentinel-cortex restart
rc-service sentinel-qhc-agent restart || true
rc-service sentinel-verifier restart || true

# 10. Verificación Final de Endpoints
echo "🔍 Verificando salud del nodo..."
sleep 2

HEALTH_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health || echo "000")
if [ "$HEALTH_HTTP" = "200" ]; then
    echo "✅ Cortex API respondiendo en http://127.0.0.1:8000/health (HTTP 200)"
else
    echo "⚠️ ADVERTENCIA: Cortex API devolvió HTTP $HEALTH_HTTP en /health"
fi

echo "=========================================================="
echo "🎉 Bootstrap de Nodo Alpine completado exitosamente."
echo "=========================================================="
