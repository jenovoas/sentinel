# OPS — Comandos de Operación y Verificación de Sentinel

> **Última actualización:** 2026-07-28
> **Nodos:** Laptop (10.10.0.11) ↔ Fan (10.10.0.12)

---

## 1. 🌐 Verificación de Red Mesh

### 1.1 WireGuard

```bash
# Estado de la interfaz
ip addr show wg0

# Estadísticas de peers
sudo wg show wg0

# Handshake y transferencia
sudo wg show wg0 transfer
```

### 1.2 VXLAN

```bash
# Verificar VXLAN
ip -d addr show vxlan0

# Ver VNI y MTU
bridge fdb show dev vxlan0
```

### 1.3 batman-adv

```bash
# Origen de vecinos
batctl o

# Tabla de routing mesh
batctl n

# Estadísticas de throughput
batctl t
```

### 1.4 MycNet Daemon

```bash
# Verificar proceso local
ps aux | grep mycnetd

# Health check
curl -s http://localhost:7474/health || curl -s http://127.0.0.1:7474/health

# Verificar conexión remota (Fan)
ssh fan systemctl status mycnet-interceptor
```

---

## 2. ⚛️ eBPF Ring-0

### 2.1 Listar Programas Cargados

```bash
# Todos los programas eBPF cargados
sudo bpftool prog list

# Solo programas Sentinel
sudo bpftool prog list | grep -E '(guardian|float|burst|xdp_firewall|cognitive)' -A5

# Detalles de un programa específico (por ID)
sudo bpftool prog show id 335
sudo bpftool prog show id 344
sudo bpftool prog show id 354
sudo bpftool prog show id 364
sudo bpftool prog show id 373
sudo bpftool prog show id 868

# Estadísticas de ejecución
sudo bpftool prog show id 335 stats
```

### 2.2 Mapas Pineados

```bash
# Ver árbol de mapas
sudo ls -la /sys/fs/bpf/
sudo ls -la /sys/fs/bpf/sentinel/
sudo ls -la /sys/fs/bpf/sentinel/gamma/

# Dump de un mapa específico
sudo bpftool map dump name god_mode_uids
sudo bpftool map dump name whitelist_map
sudo bpftool map dump name ai_whitelist_map
sudo bpftool map dump name ai_agents_map

# Contar entradas en whitelist
sudo bpftool map dump name whitelist_map | grep -c "key"
sudo bpftool map dump name ai_whitelist_map | grep -c "key"
```

### 2.3 Agregar/Quitar del Modo Dios

```bash
# Agregar UID al modo dios
sudo bpftool map update pinned /sys/fs/bpf/guardian_alpha_lsm key 0 0 0 0 value 1

# Quitar UID del modo dios
sudo bpftool map delete pinned /sys/fs/bpf/guardian_alpha_lsm key 0 0 0 0
```

### 2.4 Verificar Logs de eBPF

```bash
# Trace de kernel
sudo cat /sys/kernel/debug/tracing/trace_pipe | grep bpf

# Log del forwarder (si está activo)
sudo tail -f /var/log/sentinel/ebpf_trace.log
```

---

## 3. 🧠 Sentinel Cortex API

### 3.1 Iniciar/Detener (local)

```bash
# Iniciar manualmente (desde directorio sentinel)
./target/release/sentinel-cortex

# Con systemd (si está instalado)
sudo systemctl start sentinel-cortex
sudo systemctl enable sentinel-cortex

# Ver logs
sudo journalctl -u sentinel-cortex -f

# Verificar health
curl http://localhost:8000/health

# Ver estado del ring
curl http://localhost:8000/api/v1/sentinel_status

# Verificar truth claim
curl -X POST http://localhost:8000/api/v1/truth_claim \
  -H "Content-Type: application/json" \
  -d '{"engine":"test","claim_payload":"hello world","trust_threshold":0.5}'
```

### 3.2 WebSocket Telemetría

```bash
# Con wscat (si está instalado)
wscat -c ws://localhost:8000/api/v1/telemetry

# Con websocat
websocat ws://localhost:8000/api/v1/telemetry

# Verificar con curl (debe responder 101 Switching Protocols)
curl -v -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8000/api/v1/telemetry
```

---

## 4. 🔧 Daemons me-60os

### 4.1 Compilar y Ejecutar

```bash
# Compilar todos los daemons
cd /home/jnovoas/Proyectos/me-60os
cargo build --release --bin qhc_agent
cargo build --release --bin adm_agent
cargo build --release --bin pai_neural_daemon
cargo build --release --bin vid_agent

# Ejecutar individualmente
./target/release/qhc_agent &
./target/release/adm_agent &
./target/release/pai_neural_daemon &
./target/release/vid_agent &
```

### 4.2 Systemd (instalación en Fan)

```bash
# Copiar binarios a Fan
scp /home/jnovoas/Proyectos/me-60os/target/release/qhc_agent fan:~/.local/bin/
scp /home/jnovoas/Proyectos/me-60os/target/release/adm_agent fan:~/.local/bin/
scp /home/jnovoas/Proyectos/me-60os/target/release/pai_neural_daemon fan:~/.local/bin/
scp /home/jnovoas/Proyectos/me-60os/target/release/vid_agent fan:~/.local/bin/

# Copiar servicios systemd
scp systemd/sentinel-*.service fan:~/
ssh fan "sudo mv ~/sentinel-*.service /etc/systemd/system/ && sudo systemctl daemon-reload"

# Habilitar e iniciar
ssh fan "sudo systemctl enable --now sentinel-qhc-agent"
ssh fan "sudo systemctl enable --now sentinel-cortex"
ssh fan "sudo systemctl enable --now sentinel-ebpf-forwarder"
```

---

## 5. 📊 Observabilidad (Fan)

### 5.1 Verificar Servicios

```bash
ssh fan "systemctl status grafana loki mimir promtail node_exporter"
```

### 5.2 Health Checks

```bash
# Grafana
curl -s http://fan:3001/api/health

# Loki
curl -s http://fan:3100/ready

# Mimir
curl -s http://fan:8080/ready

# node_exporter
curl -s http://fan:9100/metrics | head -20
```

### 5.3 Consultar Logs (Loki)

```bash
# Query básica en Loki
curl -s "http://fan:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="varlogs"}' \
  --data-urlencode 'start='$(date -d "1 hour ago" +%s) \
  --data-urlencode 'end='$(date +%s) \
  -G | python3 -m json.tool | head -50
```

### 5.4 Grafana

- **URL:** http://fan:3001
- **Usuario:** admin
- **Contraseña:** admin
- **Datasources:** Loki (:3100), Mimir (:8080/prometheus)

---

## 6. 🚀 Comandos de Diagnóstico Rápido

### 6.1 Health Check Completo

```bash
#!/bin/bash
# health_check.sh — Verifica todo el stack Sentinel
echo "=== Sentinel Health Check ==="
echo ""

# 1. Red Mesh
echo "--- WireGuard ---"
ip addr show wg0 2>/dev/null | grep inet || echo "✗ wg0 down"
echo "--- batman-adv ---"
batctl o 2>/dev/null || echo "✗ batman-adv not available"
echo "--- MycNet ---"
curl -s --connect-timeout 2 http://127.0.0.1:7474/health 2>/dev/null || echo "✗ mycnetd not responding"

# 2. eBPF
echo "--- eBPF Programs ---"
sudo bpftool prog list 2>/dev/null | grep -c "lsm" || echo "✗ no LSM progs"
sudo bpftool prog list 2>/dev/null | grep -c "xdp" || echo "✗ no XDP progs"

# 3. Cortex
echo "--- Cortex API ---"
curl -s --connect-timeout 2 http://127.0.0.1:8000/health 2>/dev/null || echo "✗ Cortex not responding"

# 4. Observabilidad en Fan (opcional)
echo "--- Fan Services ---"
ssh fan "systemctl is-active grafana loki mimir node_exporter" 2>/dev/null || echo "⚠️  Fan not reachable"
```

### 6.2 Logs Rápidos

```bash
# Últimos N eventos eBPF
sudo cat /sys/kernel/debug/tracing/trace | grep bpf | tail -20

# Journal de Cortex
sudo journalctl -u sentinel-cortex --no-pager -n 50

# Journal del forwarder eBPF
sudo journalctl -u sentinel-ebpf-forwarder --no-pager -n 50
```

### 6.3 Recargar eBPF

```bash
# Recargar un programa eBPF específico (desde ebpf/)
cd /home/jnovoas/Proyectos/sentinel/ebpf
clang -O2 -target bpf -c guardian_alpha_lsm.c -o guardian_alpha_lsm.o
sudo bpftool prog load guardian_alpha_lsm.o /sys/fs/bpf/guardian_alpha_lsm \
  map name god_mode_uids pinned /sys/fs/bpf/god_mode_uids \
  map name whitelist_map pinned /sys/fs/bpf/whitelist_map
```

---

## 7. 🔄 Systemd Services (Fuente → Instalación)

```bash
# Instalar servicios de Sentinel en laptop
sudo cp /home/jnovoas/Proyectos/sentinel/systemd/sentinel-*.service /etc/systemd/system/
sudo cp /home/jnovoas/Proyectos/sentinel/mycnet/systemd/mycnet-interceptor.service /etc/systemd/system/
sudo systemctl daemon-reload

# Habilitar
sudo systemctl enable --now sentinel-cortex
sudo systemctl enable --now sentinel-ebpf-forwarder
sudo systemctl enable --now sentinel-qhc-agent
```

---

## 8. 🐳 Comandos Legado (Fenix/Podman)

Si el stack de Fenix (Traefik, contenedores) sigue operativo:

```bash
# Ver pods de Podman
podman ps --pod

# Logs de servicios
podman logs sentinel-cortex
podman logs grafana

# Health check de Traefik
curl -s http://localhost:8080/api/http/routers
```
