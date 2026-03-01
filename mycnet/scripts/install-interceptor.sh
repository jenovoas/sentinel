#!/bin/bash
#
# Instalar MycNet Interceptor en nodo remoto
# Uso: ./install-interceptor.sh [nodo]
#

set -e

NODO="${1:-kingu}"
SSH_PORT="4222"
SSH_KEY="$HOME/.ssh/google_compute_engine"
REDIS_CONF="$HOME/.config/swarm/credentials/redis.conf"

echo "=== Instalando MycNet Interceptor en $NODO ==="

# Verificar conexión SSH
echo "[1/5] Verificando conexión SSH..."
if ! ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" -i "$SSH_KEY" "jnovoas@$NODO" "echo 'OK'" > /dev/null 2>&1; then
    echo "ERROR: No se pudo conectar a $NODO via SSH"
    exit 1
fi
echo "✓ Conexión SSH exitosa"

# Copiar script interceptor
echo "[2/5] Copiando script interceptor..."
scp -P "$SSH_PORT" -i "$SSH_KEY" \
    ~/.local/bin/mycnet_interceptor.py \
    "jnovoas@$NODO:~/.local/bin/mycnet_interceptor.py"

ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" -i "$SSH_KEY" "jnovoas@$NODO" \
    "chmod +x ~/.local/bin/mycnet_interceptor.py"
echo "✓ Script copiado"

# Copiar servicio systemd
echo "[3/5] Copiando servicio systemd..."
scp -P "$SSH_PORT" -i "$SSH_KEY" \
    ~/Development/sentinel/mycnet/systemd/mycnet-interceptor.service \
    "jnovoas@$NODO:/tmp/mycnet-interceptor.service"

ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" -i "$SSH_KEY" "jnovoas@$NODO" \
    "sudo mv /tmp/mycnet-interceptor.service /etc/systemd/system/ && sudo systemctl daemon-reload"
echo "✓ Servicio instalado"

# Copiar credenciales Redis (si existen)
echo "[4/5] Copiando configuración Redis..."
if [ -f "$REDIS_CONF" ]; then
    ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" -i "$SSH_KEY" "jnovoas@$NODO" \
        "mkdir -p ~/.config/swarm/credentials"
    scp -P "$SSH_PORT" -i "$SSH_KEY" \
        "$REDIS_CONF" \
        "jnovoas@$NODO:~/.config/swarm/credentials/redis.conf"
    echo "✓ Configuración Redis copiada"
else
    echo "⚠ No existe $REDIS_CONF, el interceptor usará conexión sin password"
fi

# Habilitar e iniciar servicio
echo "[5/5] Habilitando e iniciando servicio..."
ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" -i "$SSH_KEY" "jnovoas@$NODO" << 'EOF'
    sudo systemctl enable mycnet-interceptor.service
    sudo systemctl start mycnet-interceptor.service
    sleep 2
    sudo systemctl status mycnet-interceptor.service --no-pager
EOF

echo ""
echo "=== Instalación completada en $NODO ==="
echo ""
echo "Para verificar:"
echo "  ssh -p $SSH_PORT -i $SSH_KEY jnovoas@$NODO"
echo "  sudo systemctl status mycnet-interceptor.service"
echo "  redis-cli -h 10.10.10.2 -p 6379 KEY 'swarm:mesh:$NODO:*'"
