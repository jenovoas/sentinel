#!/bin/bash
# Test script para eBPF LSM
# Prueba comandos permitidos y bloqueados

echo "🧪 Testing eBPF LSM - Guardian Alpha"
echo "======================================"
echo ""

echo "📋 Test 1: Comandos PERMITIDOS (deberían funcionar)"
echo "--------------------------------------"

# Comandos en whitelist
echo "✅ Testing: ls"
ls /tmp > /dev/null 2>&1 && echo "   ✅ ls: PERMITIDO" || echo "   ❌ ls: BLOQUEADO"

echo "✅ Testing: pwd"
pwd > /dev/null 2>&1 && echo "   ✅ pwd: PERMITIDO" || echo "   ❌ pwd: BLOQUEADO"

echo "✅ Testing: whoami"
whoami > /dev/null 2>&1 && echo "   ✅ whoami: PERMITIDO" || echo "   ❌ whoami: BLOQUEADO"

echo "✅ Testing: date"
date > /dev/null 2>&1 && echo "   ✅ date: PERMITIDO" || echo "   ❌ date: BLOQUEADO"

echo ""
echo "📋 Test 2: Comandos BLOQUEADOS (deberían fallar)"
echo "--------------------------------------"

# Comandos NO en whitelist (peligrosos)
echo "🚫 Testing: rm (debería bloquearse)"
rm --version > /dev/null 2>&1 && echo "   ❌ rm: PERMITIDO (MAL!)" || echo "   ✅ rm: BLOQUEADO (BIEN!)"

echo "🚫 Testing: curl (debería bloquearse)"
curl --version > /dev/null 2>&1 && echo "   ❌ curl: PERMITIDO (MAL!)" || echo "   ✅ curl: BLOQUEADO (BIEN!)"

echo "🚫 Testing: wget (debería bloquearse)"
wget --version > /dev/null 2>&1 && echo "   ❌ wget: PERMITIDO (MAL!)" || echo "   ✅ wget: BLOQUEADO (BIEN!)"

echo ""
echo "======================================"
echo "📊 Verificar logs del kernel:"
echo "   sudo dmesg | tail -20 | grep Guardian"
echo ""
echo "📊 Ver eventos en ring buffer:"
echo "   sudo cat /sys/kernel/debug/tracing/trace_pipe"
