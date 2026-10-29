#!/bin/sh
# Dependencias eBPF para Alpine Linux (alpine_fenix branch)
# Equivalente a install_ebpf_deps.sh para Debian/Ubuntu
set -e

echo "=== Instalando dependencias eBPF en Alpine Linux ==="
apk add --no-cache \
    build-base musl-dev \
    clang llvm \
    libbpf-dev bpftool \
    elfutils-dev zlib-dev pkgconf \
    linux-headers \
    python3-dev \
    audit \
    curl git

# Verificar BTF vmlinux (necesario para CO-RE)
if [ -f /sys/kernel/btf/vmlinux ]; then
    echo "[OK] BTF vmlinux disponible: /sys/kernel/btf/vmlinux"
else
    echo "[WARN] /sys/kernel/btf/vmlinux no encontrado — CO-RE puede no funcionar"
    echo "       Asegurarse de usar linux-edge o linux-lts con CONFIG_DEBUG_INFO_BTF=y"
fi

# Verificar BPF LSM
if grep -q 'CONFIG_BPF_LSM=y' /proc/config.gz 2>/dev/null || \
   grep -q 'CONFIG_BPF_LSM=y' /boot/config-$(uname -r) 2>/dev/null; then
    echo "[OK] CONFIG_BPF_LSM=y activo"
else
    echo "[WARN] CONFIG_BPF_LSM no detectado — verificar kernel config"
fi

# Verificar BPF filesystem montado
if mount | grep -q 'type bpf'; then
    echo "[OK] BPF filesystem montado en /sys/fs/bpf"
else
    echo "[INFO] Montando BPF filesystem..."
    mount -t bpf bpf /sys/fs/bpf
fi

echo "=== Dependencias Alpine instaladas correctamente ==="
