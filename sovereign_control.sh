#!/bin/bash
# sovereign_control.sh
# Control de Inmutabilidad para Código Crítico de Sentinel

FILES=(
    "quantum/sovereign_math.py"
    "quantum/zpe_phase1_lab.py"
    "quantum/optomechanical_simulator.py"
    "quantum/vimana_shield_validation.py"
    "quantum/bimana_integrated_nav_sim.py"
)

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

function show_status {
    echo "--- Estado de Soberanía ---"
    for file in "${FILES[@]}"; do
        if [ -w "$file" ]; then
            echo -e "${RED}EDITABLE${NC} : $file"
        else
            echo -e "${GREEN}BLOQUEADO${NC}: $file"
        fi
    done
}

function lock_files {
    echo "🔒 Bloqueando archivos críticos contra edición automática..."
    chmod a-w "${FILES[@]}"
    echo "Hecho. Las IAs agénticas fallarán si intentan editar."
}

function unlock_files {
    echo "🔓 Desbloqueando archivos para mantenimiento manual..."
    chmod u+w "${FILES[@]}"
    echo "Hecho. ADVERTENCIA: Protege los archivos al terminar."
}

case "$1" in
    lock)
        lock_files
        ;;
    unlock)
        unlock_files
        ;;
    status)
        show_status
        ;;
    *)
        echo "Uso: $0 {lock|unlock|status}"
        show_status
        exit 1
esac
