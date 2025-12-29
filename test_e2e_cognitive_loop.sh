#!/bin/bash
# Test E2E: Cognitive Loop Validation
# Este script ejecuta los test cases para validar el ciclo cognitivo completo

set -e

echo "🧪 [E2E Test] Iniciando Test de Ciclo Cognitivo"
echo "================================================"
echo ""

# Verificar que eBPF está cargado
if ! sudo bpftool prog show pinned /sys/fs/bpf/guardian_alpha/guardian_prog &>/dev/null; then
    echo "❌ Error: eBPF Guardian no está cargado"
    echo "Por favor ejecuta: cd ebpf && sudo ./load.sh"
    exit 1
fi

echo "✅ eBPF Guardian está cargado"
echo ""

# Limpiar binarios de prueba anteriores
echo "🧹 Limpiando binarios de prueba anteriores..."
sudo rm -f /tmp/test_deployment_tool /tmp/test_rootkit_installer
echo ""

# Test Case 1: Binario "Seguro"
echo "📦 Test Case 1: Binario Seguro (deployment_tool)"
echo "------------------------------------------------"
cp /bin/true /tmp/test_deployment_tool
chmod +x /tmp/test_deployment_tool

echo "Intento 1: Ejecutando /tmp/test_deployment_tool (debería ser BLOQUEADO)..."
if /tmp/test_deployment_tool 2>&1; then
    echo "⚠️  WARNING: El binario NO fue bloqueado (inesperado)"
else
    echo "✅ Binario bloqueado correctamente por eBPF"
fi

echo ""
echo "⏳ Esperando 5 segundos para que la IA analice y actualice whitelist..."
sleep 5

echo "Intento 2: Ejecutando /tmp/test_deployment_tool (debería ser PERMITIDO)..."
if /tmp/test_deployment_tool 2>&1; then
    echo "✅ SUCCESS: Binario permitido después de análisis IA"
else
    echo "❌ FAIL: Binario sigue bloqueado (la IA no lo whitelistó)"
fi

echo ""
echo ""

# Test Case 2: Binario "Malicioso"
echo "🦠 Test Case 2: Binario Malicioso (rootkit_installer)"
echo "------------------------------------------------------"
cp /bin/true /tmp/test_rootkit_installer
chmod +x /tmp/test_rootkit_installer

echo "Intento 1: Ejecutando /tmp/test_rootkit_installer (debería ser BLOQUEADO)..."
if /tmp/test_rootkit_installer 2>&1; then
    echo "⚠️  WARNING: El binario NO fue bloqueado (inesperado)"
else
    echo "✅ Binario bloqueado correctamente por eBPF"
fi

echo ""
echo "⏳ Esperando 5 segundos para que la IA analice..."
sleep 5

echo "Intento 2: Ejecutando /tmp/test_rootkit_installer (debería seguir BLOQUEADO)..."
if /tmp/test_rootkit_installer 2>&1; then
    echo "❌ FAIL: Binario malicioso fue permitido (la IA falló)"
else
    echo "✅ SUCCESS: Binario malicioso sigue bloqueado (IA correcta)"
fi

echo ""
echo ""
echo "🎉 Test E2E Completado"
echo "================================================"
echo "Revisa los logs del monitor para ver las decisiones de la IA"
