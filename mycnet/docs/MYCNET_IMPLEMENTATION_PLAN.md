# MYCNET_IMPLEMENTATION_PLAN.md

## MycNet: Red Mesh Bio-Inspirada con Extensiones Sentinel (S60 + Modulación Armónica + Telemetría)

**Fecha:** 2026-01-14  
**Objetivo:** Construir y validar una red mesh WiFi/Ethernet inspirada en micelio (malla + rutas múltiples + auto-reparación) y alineada con Sentinel (métricas S60, modulación armónica en rebalanceo, dashboards S60).

**Plan Híbrido**: MinIO (Fase 1-4) → Ceph (Fase 5 opcional)

---

## 0) Resultados esperados (criterios de éxito globales)

### Resiliencia y convergencia

- **Red operativa** con pérdida de hasta **50% de nodos** (3/6)
- **Tiempo de convergencia**: **< 1 s** tras fallo
- **Pérdida de paquetes**: **< 2%** durante failover

### Latencia bajo carga

- **p95 RTT < 50 ms** bajo saturación (iperf3 10 flujos)
- Jitter controlado con AQM

### Storage distribuido

- Lecturas exitosas durante pérdida de 1 nodo
- Rebalanceo sin degradación severa

---

## 1) Arquitectura: capas y componentes

### 1.1 Capa de enlace (L2/L3 físico)

- **Ethernet** (recomendado Fase 1-4)
- WiFi mesh (opcional Fase 5)

### 1.2 Capa Mesh / Enrutamiento

- **batman-adv** sobre `bat0`
- Métrica: **TQ** (0–255) por vecino

### 1.3 Capa de colas / Congestión

- **fq_codel** o **cake** en `bat0`

### 1.4 Capa de storage distribuido

- **Fase 1-4**: MinIO (EC 4+2)
- **Fase 5**: Ceph (replicación 3x + CRUSH)

### 1.5 Observabilidad

- Métricas base: ping, iperf3, batctl
- **Extensión Sentinel**: TQ → S60, dashboard Grafana

---

## 2) Inventario y costos

### Hardware mínimo (6 nodos)

- 6× Raspberry Pi 4 (4GB)
- 6× SSD USB3 (128GB) - **obligatorio para Ceph**
- Switch Gigabit Ethernet
- **Costo estimado**: USD 300-600

### Software

- Ubuntu Server 22.04 LTS
- batman-adv, batctl, iperf3
- **MinIO** (Fase 1-4)
- **Ceph** (Fase 5)
- Prometheus + Grafana (opcional)

---

## 3) Plan de fases (15 días / 2 semanas)

### **Fase 0 — Preparación (1 día)**

- Flashear Ubuntu en 6 RPi4
- IPs estáticas (192.168.1.11–16)
- SSH + NTP

### **Fase 1 — Mesh básico batman-adv (2 días)**

**Objetivo**: `bat0` operativo, vecinos visibles

**Instalación**:

```bash
sudo apt -y install batctl
sudo modprobe batman-adv
sudo ip link set up dev eth1
sudo batctl if add eth1
sudo ip link set up dev bat0
sudo ip addr add 10.10.0.11/24 dev bat0  # ajustar por nodo
```

**Verificación**:

```bash
batctl n      # vecinos y TQ
batctl o      # originators
ping -c 5 10.10.0.12
```

**Criterio de éxito**: Todos los nodos ven ≥2 vecinos, ping < 10ms

---

### **Fase 2 — Storage MinIO (2 días)**

**Objetivo**: Cluster MinIO con EC 4+2

**Deployment**:

```bash
# En cada nodo (n1-n6):
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# Iniciar cluster (mismo comando en todos):
minio server http://n{1...6}:9000/data{1...6}
```

**Prueba**:

```bash
# Desde n1:
mc alias set mycnet http://n1:9000 minioadmin minioadmin
mc mb mycnet/test
dd if=/dev/urandom of=/tmp/blob.bin bs=1M count=100
mc cp /tmp/blob.bin mycnet/test/
mc ls mycnet/test/
```

**Criterio de éxito**: Lectura exitosa tras matar 1 nodo

---

### **Fase 3 — AQM y congestión (2 días)**

**Objetivo**: Reducir p95 RTT bajo carga

**Aplicar qdisc**:

```bash
sudo tc qdisc replace dev bat0 root fq_codel
```

**Prueba de carga**:

```bash
# Servidor:
iperf3 -s

# Clientes (10 flujos):
iperf3 -c 10.10.0.11 -P 10 -t 60

# Latencia paralela:
fping -D -p 20 -c 300 10.10.0.11 | tee latency.log
```

**Criterio de éxito**: p95 RTT mejora vs. baseline sin AQM

---

### **Fase 4 — Resiliencia (2 días)**

**Objetivo**: Validar tolerancia a fallos

**Kill tests**:

1. Apagar 1 nodo (puente)
2. Apagar 2 nodos (críticos)
3. Apagar 3 nodos (50%)

**Instrumentación**:

```bash
ping 10.10.0.12 -i 0.2 | ts '%s' | tee ping_stream.log
```

**Criterio de éxito**: Convergencia < 1s, pérdida < 2%

---

### **Fase 5 — Extensiones Sentinel (3 días) [OPCIONAL]**

#### **Mejora 1: Métricas S60**

Script `mycnet_s60_monitor.py` (ver sección 4.1)

**Criterio**: Coherencia S60 > 0.85 (S60[000; 51, ...])

#### **Mejora 2: YHWH Modulation en Ceph**

Script `ceph_yhwh_tuner.sh` (ver sección 4.2)

**Criterio**: p95 RTT estable durante rebalanceo

#### **Mejora 3: Dashboard Grafana S60**

Panel custom con formato S60 (ver sección 4.3)

---

## 4) Extensiones Sentinel (Fase 5)

### 4.1 Métricas S60 (TQ → S60)

**Script**: `mycnet_s60_monitor.py`

```python
#!/usr/bin/env python3
import json, subprocess
from dataclasses import dataclass

@dataclass(frozen=True)
class S60:
    d: int; m: int; s: int; t: int; q: int
    def __str__(self):
        return f"S60[{self.d:03d}; {self.m:02d}, {self.s:02d}, {self.t:02d}, {self.q:02d}]"

def dec_to_s60(x: float) -> S60:
    if x < 0: x = 0.0
    if x > 1: x = 1.0
    d = int(x); rem = x - d
    rem *= 60; m = int(rem); rem -= m
    rem *= 60; s = int(rem); rem -= s
    rem *= 60; t = int(rem); rem -= t
    rem *= 60; q = int(rem)
    return S60(d, m, s, t, q)

def tq_to_s60(tq: int) -> S60:
    return dec_to_s60(tq / 255.0)

# Ver script completo en mycnet/scripts/
```

### 4.2 YHWH Modulation en Ceph

**Script**: `ceph_yhwh_tuner.sh`

```bash
#!/usr/bin/env bash
PATTERN=(10 5 6 5)
HOUR=$(date +%H)
PHASE=$(( (10#$HOUR / 6) % 4 ))
FACTOR=${PATTERN[$PHASE]}

# Modular backfills según fase
if [ "$FACTOR" -ge 10 ]; then
  BACKFILLS=2; SLEEP=0.05
else
  BACKFILLS=1; SLEEP=0.20
fi

ceph config set osd osd_max_backfills "$BACKFILLS"
ceph config set osd osd_recovery_sleep "$SLEEP"
```

### 4.3 Dashboard Grafana S60

**Transform function**:

```javascript
function formatS60(x) {
  let d = Math.floor(x);
  let rem = (x - d) * 60;
  let m = Math.floor(rem);
  // ... (ver script completo)
  return `S60[${d.toString().padStart(3,'0')}; ${m.toString().padStart(2,'0')}, ...]`;
}
```

---

## 5) Plan de pruebas (matriz)

| Prueba | Métrica | Criterio |
|--------|---------|----------|
| **Vecinos** | batctl n | ≥2 vecinos |
| **Conectividad** | ping RTT | < 10ms |
| **Saturación + AQM** | p95 RTT | < 50ms |
| **Fail 1 nodo** | Convergencia | < 1s |
| **Fail 3 nodos** | Continuidad | Red no colapsa |
| **Storage fail** | Lectura OK | 100% OK |

---

## 6) Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| **Ceph en SD** | SSD USB3 obligatorio |
| **WiFi variable** | Ethernet + entorno controlado |
| **YHWH agresivo** | Límites conservadores |
| **Medición inconsistente** | Guion repetible |

---

## 7) Runbook de ejecución

1. **Fase 0**: Preparar nodos
2. **Fase 1**: Levantar bat0
3. **Fase 2**: Deploy MinIO
4. **Fase 3**: AQM + carga
5. **Fase 4**: Kill tests
6. **Fase 5** (opcional): Migrar a Ceph + S60

---

## 8) Entregables

- ✅ Plan completo (este documento)
- ✅ Scripts deployment
- ⏸️ Reporte resultados (gráficas + tablas)
- ⏸️ Demo video (opcional)

---

## 9) Decisiones cerradas

1. ✅ **Backhaul**: Ethernet
2. ✅ **Storage**: MinIO → Ceph (híbrido)
3. ✅ **Precisión S60**: Hasta segundos
4. ✅ **Convergencia**: 5 pings sin pérdida

---

**Siguiente paso**: Adquirir hardware y ejecutar Fase 0-1.
