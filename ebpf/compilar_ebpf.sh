#!/bin/bash
# Sentinel eBPF - Compilación completa (kernel + userspace)
set -e

BOLD='\033[1m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; exit 1; }

cd "$(dirname "$0")"

echo -e "\n${BOLD}── Verificando toolchain ─────────────────────────────────${NC}"
for tool in clang llvm-strip bpftool gcc; do
    command -v $tool &>/dev/null && ok "$tool" || warn "$tool NO encontrado"
done

# Instalar dependencias si faltan (RHEL9/CentOS9)
if ! command -v clang &>/dev/null; then
    echo "Instalando toolchain eBPF (dnf)..."
    sudo dnf install -y clang llvm bpftool libbpf-devel elfutils-libelf-devel
fi

echo -e "\n${BOLD}── Compilando todo ───────────────────────────────────────${NC}"
make clean 2>/dev/null || true
make all

echo -e "\n${BOLD}── Resultados ────────────────────────────────────────────${NC}"
echo "Kernel objects (.o):"
ls -lh ./*.o 2>/dev/null | awk '{print "  " $0}' || warn "ningún .o generado"
echo "Userspace binaries:"
for bin in event_monitor loader lsm_loader lsm_attach attacher benchmark_exec; do
    [ -x "./$bin" ] && ok "$bin" || warn "$bin no generado"
done

echo ""
ok "Compilación completa — ejecuta './load.sh' para cargar en kernel"
