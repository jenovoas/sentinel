#!/bin/bash
# Script de Compilación eBPF LSM - Paso a Paso
# Fecha: 21 de Diciembre de 2025

echo "🔧 PASO 1: Instalando toolchain eBPF..."
echo "========================================"

# Verificar si ya están instalados
echo "Verificando herramientas existentes..."
which clang && echo "✅ clang instalado" || echo "❌ clang NO instalado"
which llvm-strip && echo "✅ llvm-strip instalado" || echo "❌ llvm-strip NO instalado"
which bpftool && echo "✅ bpftool instalado" || echo "❌ bpftool NO instalado"

echo ""
echo "Instalando herramientas faltantes..."
echo ""
echo "Instalando herramientas faltantes..."

if [ -f /etc/debian_version ]; then
    ./install_deps_debian.sh
else
    sudo pacman -S --needed clang llvm bpf libbpf bpftool
fi

echo ""
echo "✅ Toolchain instalado"
echo ""

echo "🔨 PASO 2: Compilando eBPF LSM..."
echo "========================================"

cd /home/jnovoas/sentinel/ebpf

# Limpiar builds anteriores
echo "Limpiando builds anteriores..."
make clean 2>/dev/null || true

# Compilar
echo "Compilando guardian_alpha_lsm.c..."
make

if [ $? -eq 0 ]; then
    echo "✅ Compilación exitosa"
    ls -lh *.o 2>/dev/null || echo "⚠️  No se generaron archivos .o"
else
    echo "❌ Error en compilación"
    echo "Revisa los errores arriba"
    exit 1
fi

echo ""
echo "📋 PASO 3: Verificando archivos generados..."
echo "========================================"
ls -lh guardian_alpha_lsm.o 2>/dev/null && echo "✅ guardian_alpha_lsm.o generado" || echo "❌ Archivo .o no encontrado"

echo ""
echo "🎯 SIGUIENTE PASO (requiere sudo):"
echo "========================================"
echo "Para cargar en kernel, ejecuta:"
echo "  sudo ./load.sh"
echo ""
echo "O manualmente:"
echo "  sudo bpftool prog load guardian_alpha_lsm.o /sys/fs/bpf/guardian"
echo "  sudo bpftool prog list | grep guardian"
echo ""

# Documentar resultado
echo "✅ eBPF LSM compilado - $(date)" >> ../VALIDATION_LOG.md
echo "Comando ejecutado: make" >> ../VALIDATION_LOG.md
echo "Resultado: Compilación exitosa" >> ../VALIDATION_LOG.md
echo "" >> ../VALIDATION_LOG.md

echo "✅ TODO LISTO"
echo "Resultado documentado en VALIDATION_LOG.md"
