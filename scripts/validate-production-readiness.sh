#!/bin/sh
# ==============================================================================
# Sentinel Platform — Validador Integral de Preparación para Producción
# ==============================================================================
# Ejecuta pruebas zero-trust contra todos los componentes del sistema en Fénix.
# ==============================================================================

set -eu

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

EXIT_CODE=0

log_pass() {
    printf "${GREEN}[PASS]${NC} %s\n" "$1"
}

log_fail() {
    printf "${RED}[FAIL]${NC} %s\n" "$1"
    EXIT_CODE=1
}

log_info() {
    printf "${YELLOW}[INFO]${NC} %s\n" "$1"
}

echo "=================================================================="
echo "🛡️ Sentinel: Auditoría de Preparación de Producción en Vivo"
echo "=================================================================="
# 1. Comprobación de Servicios OpenRC
log_info "Verificando daemons nativos en OpenRC..."
for svc in sentinel-cortex sentinel-qhc-agent sentinel-verifier sentinel-backup; do
    if sudo rc-service "$svc" status 2>&1 | grep -q "started"; then
        log_pass "Servicio $svc está activo y en ejecución"
    else
        log_fail "Servicio $svc NO está activo"
    fi
done

# 2. Comprobación de Programas eBPF en Kernel Ring-0
log_info "Verificando guardianes eBPF en Ring-0..."
if command -v bpftool >/dev/null 2>&1; then
    BPF_PROGS=$(sudo bpftool prog list 2>/dev/null || true)
    for prog in guardian_execve guardian_cognitive float_detector xdp_firewall_prog; do
        if echo "$BPF_PROGS" | grep -q "$prog"; then
            log_pass "Programa eBPF $prog cargado en kernel"
        else
            log_fail "Programa eBPF $prog NO detectado en kernel"
        fi
    done
else
    log_fail "bpftool no disponible para auditar eBPF"
fi

# 3. Comprobación de Endpoints REST de Cortex (Puerto 8000)
log_info "Auditando endpoints de Sentinel Cortex API..."

# /health
HEALTH_STATUS=$(curl -s http://127.0.0.1:8000/health | jq -r '.status // empty')
if [ "$HEALTH_STATUS" = "OK" ]; then
    log_pass "Endpoint /health responde OK con estado saludable"
else
    log_fail "Endpoint /health falló: $HEALTH_STATUS"
fi

# /api/v1/qhc/status
QHC_CONN=$(curl -s http://127.0.0.1:8000/api/v1/qhc/status | jq -r '.connected // false')
if [ "$QHC_CONN" = "true" ]; then
    log_pass "QHC Agent sincronizado y conectado con Cortex (/run/soma/qhc.sock)"
else
    log_fail "QHC Agent desconectado"
fi

# /api/v1/failsafe/status
FAILSAFE_STAT=$(curl -s http://127.0.0.1:8000/api/v1/failsafe/status | jq -r '.status // empty')
if [ "$FAILSAFE_STAT" = "operational" ] || [ "$FAILSAFE_STAT" = "runtime_available" ]; then
    log_pass "Plano de defensa /failsafe/status reporta $FAILSAFE_STAT"
else
    log_fail "Failsafe status no reporta operational"
fi

# /api/v1/backup/status
BACKUP_HEALTH=$(curl -s http://127.0.0.1:8000/api/v1/backup/status | jq -r '.health // empty')
if [ "$BACKUP_HEALTH" = "healthy" ]; then
    log_pass "Subsistema de respaldo /backup/status reporta healthy con archivos válidos"
else
    log_fail "Subsistema de respaldo reporta estado degradado: $BACKUP_HEALTH"
fi

# 4. Prueba de Ataque Malicioso y Bloqueo Forense WAL
log_info "Probando intercepción de ataque crítico (rm -rf /)..."
ATTACK_RESP=$(curl -s -X POST http://127.0.0.1:8000/api/v1/truth_claim \
    -H "Content-Type: application/json" \
    -d '{"engine":"validator","claim_payload":"rm -rf /","trust_threshold":0.5}')

BLOCKED=$(echo "$ATTACK_RESP" | jq -r '.security_blocked // false')
LOGGED=$(echo "$ATTACK_RESP" | jq -r '.security_event_logged // false')

if [ "$BLOCKED" = "true" ] && [ "$LOGGED" = "true" ]; then
    log_pass "Ataque interceptado con éxito (security_blocked=true, security_event_logged=true)"
else
    log_fail "Fallo de intercepción de seguridad en TruthClaim"
fi

# 5. Comprobación de la Doble Malla Resonante y SHM
log_info "Verificando compilación y ejecución de Doble Malla..."
if cargo test -p me60os test_warm_up_uses_configured_damping_and_dual_lanes_converge -- --nocapture >/dev/null 2>&1; then
    log_pass "Doble malla resonante y convergencia validadas sin errores"
else
    log_fail "Fallo en validación de doble malla"
fi

# 6. Comprobación de Persistencia .crystal de NeuralMemory
log_info "Verificando persistencia .crystal de SNN..."
if cargo test -p me60os test_neural_memory_crystal_persistence_roundtrip >/dev/null 2>&1; then
    log_pass "Serialización y deserialización de pesos sinápticos .crystal validada"
else
    log_fail "Fallo en persistencia .crystal"
fi

echo "=================================================================="
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "🎉 TODAS LAS COMPROBACIONES PASARON: Sistema listo para producción."
else
    echo "⚠️ SE DETECTARON FALLOS EN LA AUDITORÍA."
fi
echo "=================================================================="
exit $EXIT_CODE
