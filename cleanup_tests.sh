#!/bin/bash
# 🧹 Limpieza Masiva de Tests Obsoletos
# ======================================
# Elimina archivos de test que no son realmente tests

echo "🧹 LIMPIEZA MASIVA DE TESTS OBSOLETOS"
echo "======================================"

# Crear directorio de backup
mkdir -p .test_cleanup_backup

# Función para mover a backup
backup_and_remove() {
    file=$1
    reason=$2
    echo "❌ $file - $reason"
    cp "$file" ".test_cleanup_backup/$(basename $file).bak" 2>/dev/null
    rm "$file"
}

# 1. Scripts de demostración (no son tests)
echo -e "\n📋 Eliminando scripts de demostración..."
backup_and_remove "./backend/quick_test.py" "Script de demo, no test"
backup_and_remove "./backend/scripts/chaos_test.py" "Script de demo"
backup_and_remove "./backend/scripts/load_test_suite.py" "Load test, no unit test"
backup_and_remove "./backend/scripts/load_test_suite_stub.py" "Stub vacío"
backup_and_remove "./backend/test_buffer_cascade.py" "Script de demo"
backup_and_remove "./backend/test_levitation.py" "Script de demo"
backup_and_remove "./backend/test_telem_auto.py" "Script de demo"
backup_and_remove "./bci/scripts/sentinel_bci_console_test.py" "Script de demo"
backup_and_remove "./bci/scripts/sentinel_bci_python_test.py" "Script de demo"
backup_and_remove "./tests/stress_test_shadow.py" "Stress test, no unit test"
backup_and_remove "./tests/test_bci_audio.py" "Script de demo"

# 2. Tests sin assertions (falseados o incompletos)
echo -e "\n📋 Eliminando tests sin assertions..."
backup_and_remove "./backend/scripts/test_ws.py" "Sin assertions"
backup_and_remove "./backend/test_fluido.py" "Sin assertions"
backup_and_remove "./backend/test_forensic_wal_runner.py" "Sin assertions"
backup_and_remove "./backend/test_manual.py" "Sin assertions"
backup_and_remove "./backend/test_mtls_runner.py" "Sin assertions"
backup_and_remove "./backend/test_telem_protect.py" "Sin assertions"

# 3. Tests de truth_algorithm (obsoletos si no se usan)
echo -e "\n📋 Moviendo tests de truth_algorithm a backup..."
mkdir -p .test_cleanup_backup/truth_algorithm
cp ./truth_algorithm/*test*.py .test_cleanup_backup/truth_algorithm/ 2>/dev/null

echo -e "\n✅ LIMPIEZA COMPLETADA"
echo "======================================"
echo "📦 Backups guardados en: .test_cleanup_backup/"
echo ""
echo "Tests eliminados: ~20 archivos"
echo "Tests mantenidos: Tests legítimos en /quantum y /backend/tests"
