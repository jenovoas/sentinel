#!/bin/bash
# 🛡️ Sentinel Bare Metal Forge v1.0
# Objetivo: Transformar el hardware físico en un Nodo Soberano de Sentinel.
# Optimiza el kernel, prepara Hugepages y despliega el Córtex en el metal.

set -euo pipefail

# Colores de la Matriz
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[SENTINEL]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. Verificación de Privilegios
if [[ $EUID -ne 0 ]]; then
   print_error "Este ritual requiere privilegios de Root (sudo)."
   exit 1
fi

# 2. Hardware Pre-flight
print_status "Escaneando arquitectura física..."
CPU_FEATURES=$(grep -oE 'avx2|avx512|aes' /proc/cpuinfo | sort -u | xargs)
print_success "Capacidades detectadas: $CPU_FEATURES"

# 3. Optimización del Kernel (Sysctl)
print_status "Sintonizando el Kernel para baja latencia (Sentinel Mode)..."
cat > /etc/sysctl.d/99-sentinel-performance.conf << EOF
# Optimización de Memoria
vm.swappiness=10
vm.dirty_ratio=60
vm.dirty_background_ratio=2
vm.max_map_count=262144

# Red de Alta Resonancia
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.core.netdev_max_backlog=5000

# Seguridad eBPF
kernel.unprivileged_bpf_disabled=1
net.core.bpf_jit_enable=1

# Hugepages Persistentes
vm.nr_hugepages=512
EOF
sysctl -p /etc/sysctl.d/99-sentinel-performance.conf > /dev/null
print_success "Kernel optimizado para Sentinel."

# 4. Configuración de Hugepages (Para el Córtex en Rust)
print_status "Reservando Hugepages (2MB blocks)..."
echo 512 > /proc/sys/vm/nr_hugepages || print_warning "No se pudo reservar Hugepages (posible falta de RAM)."
print_success "Memoria de alta velocidad preparada."

# 5. Instalación de Dependencias Core
print_status "Instalando dependencias de bajo nivel..."
apt-get update -qq || true
# Limpiar posibles conflictos previos
apt-get install -f -y -qq
apt-get remove -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-buildx-plugin || true

print_status "Instalando stack nativo de Debian..."
apt-get install -y -qq \
    curl git jq docker.io docker-compose \
    python3-venv clang llvm bpftool build-essential \
    kmod pciutils usbutils

# 6. Despliegue del Binario SCTL (Sovereign Control)
print_status "Enlazando herramientas de control soberano..."
SENTINEL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ln -sf "$SENTINEL_ROOT/tools/sctl_bin" /usr/local/bin/sctl
chmod +x /usr/local/bin/sctl
print_success "Comando 'sctl' activo globalmente."

# 7. Verificación de Secretos (Post-Clone)
if [[ ! -f "$SENTINEL_ROOT/.env" ]]; then
    print_warning "No se detectó el archivo .env. Creando uno desde el ejemplo..."
    cp "$SENTINEL_ROOT/.env.example" "$SENTINEL_ROOT/.env"
    print_info "Recuerda restaurar tus llaves (.priv, .pub) y configurar las contraseñas reales en .env."
fi

# 8. Finalización
print_status "Configurando persistencia de Sentinel..."

# A. Crear servicio de watchdog (Bash)
cat > /etc/systemd/system/sentinel-watchdog.service << EOF
[Unit]
Description=Sentinel Cognitive Watchdog
After=network.target docker.service

[Service]
Type=simple
ExecStart=$SENTINEL_ROOT/tools/sentinel_maintenance.sh --monitor
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# B. Crear servicio para el Cortex (Rust Nativo)
cat > /etc/systemd/system/sentinel-cortex.service << EOF
[Unit]
Description=Sentinel Cortex Native Engine
After=network.target sentinel-watchdog.service

[Service]
Type=simple
WorkingDirectory=$SENTINEL_ROOT/src/sentinel-cortex
ExecStart=/usr/bin/cargo run --release
Restart=always
User=jnovoas
Environment=PATH=/usr/local/bin:/usr/bin:/bin:/home/jnovoas/.cargo/bin
Environment=REDIS_URL=redis://localhost:6379

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable sentinel-watchdog.service > /dev/null
systemctl enable sentinel-cortex.service > /dev/null

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}  HOST FÍSICO TRANSFORMADO EN NODO SENTINEL EXITOSAMENTE ${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "Próximos pasos:"
echo -e " 1. Reinicia para aplicar los parámetros de Hugepages de forma persistente."
echo -e " 2. Ejecuta 'sctl health' para verificar la resonancia."
echo -e " 3. El sistema volará comparado con la máquina virtual."
echo -e "${BLUE}Resonancia establecida. Sentinel ahora es parte de tu hardware.${NC}\n"
