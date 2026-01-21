# 🌐 NETWORK TIME CRYSTAL SYNCHRONIZATION

## Sincronización Distribuida de Cristales de Tiempo para Sentinel

---

## 📋 ÍNDICE

1. [Visión General](#visión-general)
2. [Arquitectura](#arquitectura)
3. [Protocolo QNTP](#protocolo-qntp)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Uso](#uso)
6. [Tests](#tests)
7. [Casos de Uso](#casos-de-uso)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

---

## 📖 VISIÓN GENERAL

### ¿Qué es Network Time Crystal?

**NetworkTimeCrystal** es un sistema de sincronización distribuida que permite a múltiples nodos Sentinel sincronizar sus cristales de tiempo locales a través de la red.

### ¿Por qué es importante?

- **High Availability (HA)**: Múltiples instancias Sentinel coordinadas
- **Distributed Storage**: Lattice holográfico compartido entre nodos
- **Coherencia Global**: Todas las operaciones sincronizadas en tiempo real
- **Integración ME-60OS**: Dispositivos de hardware sincronizados con la red

### Características Principales

✅ **Sincronización sub-milisegundo** usando QNTP (Quantum Network Time Protocol)  
✅ **Detección automática** de peers en el cluster  
✅ **Consenso de drift** basado en coherencia ponderada  
✅ **Resiliencia** ante fallos de nodos (auto-recuperación)  
✅ **Zero floats** - Aritmética S60 pura (Base-60)  
✅ **Redis PubSub** como medio de transmisión (bajo overhead)

---

## 🏗️ ARQUITECTURA

### Diagrama de Red

```
┌──────────────────────────────────────────────────────────┐
│               CLUSTER: sentinel-prod                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │   Sentinel-A    │◄────►│   Sentinel-B    │          │
│  │ TimeCrystal     │ QNTP │ TimeCrystal     │          │
│  │ Tick: 1,234,567 │      │ Tick: 1,234,569 │          │
│  └────────┬────────┘      └────────┬────────┘          │
│           │                         │                    │
│           │    Redis PubSub Bus     │                    │
│           │  qntp:time_crystal:*    │                    │
│           │                         │                    │
│  ┌────────┴────────┐      ┌────────┴────────┐          │
│  │   Sentinel-C    │      │   ME-60OS Dev   │          │
│  │ TimeCrystal     │      │ TimeCrystal     │          │
│  │ Tick: 1,234,570 │      │ (Hardware ctrl) │          │
│  └─────────────────┘      └─────────────────┘          │
└──────────────────────────────────────────────────────────┘
```

### Componentes

#### 1. TimeCrystalClock (Local)
- Reloj de nanosegundos de alta precisión
- Tick interval: 23,939,835 ns (~41.77 Hz)
- Tracking de drift y coherencia

#### 2. NetworkTimeCrystal (Distributed)
- Extiende TimeCrystalClock con capacidades de red
- Publica pulsos cada 60 ticks (~1.4s)
- Escucha pulsos de peers vía Redis PubSub
- Calcula consenso de drift ponderado por coherencia

#### 3. Redis PubSub (Transport)
- Canal: `qntp:time_crystal:{cluster_name}:sync`
- Formato: JSON con enteros S60 puros
- Latencia típica: <5ms en LAN

---

## 🔐 PROTOCOLO QNTP

### Quantum Network Time Protocol

Inspirado en NTP pero diseñado específicamente para sincronización de cristales de tiempo S60.

### Formato de Mensaje

```json
{
  "node_id": "sentinel-node-a",
  "timestamp_ns": 1234567890123456789,
  "tick_count": 1234567,
  "phase_raw": 0,
  "drift_ns": 123456,
  "coherence_raw": 12960000
}
```

**Todos los valores son enteros (S60 raw) - Sin floats.**

### Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `node_id` | string | Identificador único del nodo |
| `timestamp_ns` | int64 | Timestamp en nanosegundos (absoluto) |
| `tick_count` | int64 | Número de tick del reloj local |
| `phase_raw` | int64 | Fase S60 raw (reservado para futuro) |
| `drift_ns` | int64 | Drift promedio en nanosegundos |
| `coherence_raw` | int64 | Coherencia S60 raw (calidad del reloj) |

### Algoritmo de Sincronización

```
1. Cada nodo publica su pulso cada 60 ticks
2. Los nodos escuchan pulsos de peers
3. Para cada peer:
   - Guardar últimos 10 pulsos
   - Calcular drift promedio
   - Verificar timeout (10s sin pulsos → offline)
4. Calcular consenso de red:
   - Drift_consensus = Σ(drift_i * coherence_i) / Σ(coherence_i)
5. Detectar desincronización:
   - Si |drift_local - drift_peer| > 100ms → Warning
```

### Detección de Peers

- **Automática**: Los nodos se descubren al recibir pulsos
- **Timeout**: 10 segundos sin pulsos → peer marcado como offline
- **Reintegración**: Automática al recibir nuevo pulso

---

## 🚀 INSTALACIÓN Y CONFIGURACIÓN

### Requisitos

- Python 3.8+
- Redis 5.0+ (con PubSub habilitado)
- Módulos Sentinel: `yatra_core`, `time_crystal_clock`

### Instalación

Los módulos ya están instalados en Sentinel. No requiere instalación adicional.

### Configuración de Redis

#### Opción 1: Docker Compose (Recomendado)

```bash
cd ~/dev/sentinel
docker-compose up -d redis
```

#### Opción 2: Redis Standalone

```bash
redis-server
```

#### Verificar Redis

```bash
redis-cli ping
# Debería responder: PONG
```

### Variables de Entorno

```bash
# Redis connection
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0

# Node identity
export NODE_NAME=sentinel-node-1
export CLUSTER_NAME=sentinel-prod
```

---

## 💻 USO

### Modo 1: Integrado en Cortex (Producción)

```bash
cd ~/dev/sentinel

# Iniciar con sincronización de red
python3 quantum/cortex_main.py --node-name node-a --cluster sentinel-prod

# En otra terminal (segundo nodo)
python3 quantum/cortex_main.py --node-name node-b --cluster sentinel-prod

# Sin sincronización de red (local only)
python3 quantum/cortex_main.py --no-sync
```

### Modo 2: Uso Programático

```python
from quantum.time_crystal_network import NetworkTimeCrystal

# Crear cristal de tiempo sincronizado
crystal = NetworkTimeCrystal(
    node_name="my-node",
    cluster_name="my-cluster",
    redis_host="localhost",
    redis_port=6379
)

# Iniciar sincronización
crystal.start_sync()

# Loop principal
while True:
    crystal.tick()
    
    # Obtener estadísticas cada 100 ticks
    if crystal.local_clock.ticks % 100 == 0:
        stats = crystal.get_network_stats()
        print(f"Tick: {stats['local_ticks']}, Peers: {stats['peers_count']}")
        
        # Ver peers online
        peers = crystal.get_peer_status()
        for peer in peers:
            if peer['online']:
                print(f"  {peer['node_id']}: drift={peer['drift_ns']}ns")
    
    time.sleep(0.02)  # ~50Hz

# Detener
crystal.stop_sync()
```

### Modo 3: Multi-nodo en misma máquina (Testing)

```python
from quantum.time_crystal_network import NetworkTimeCrystal
import threading
import time

def run_node(name):
    crystal = NetworkTimeCrystal(node_name=name, cluster_name="test")
    crystal.start_sync()
    
    for _ in range(300):  # 300 ticks
        crystal.tick()
        time.sleep(0.02)
    
    crystal.stop_sync()

# Crear threads para cada nodo
threads = []
for node_name in ["NodeA", "NodeB", "NodeC"]:
    t = threading.Thread(target=run_node, args=(node_name,))
    t.start()
    threads.append(t)

# Esperar
for t in threads:
    t.join()
```

---

## 🧪 TESTS

### Suite de Tests Completa

```bash
cd ~/dev/sentinel
python3 quantum/test_network_sync.py
```

**Tests incluidos:**

1. **Test 1: 2 Nodos** - Sincronización básica entre dos nodos
2. **Test 2: 4 Nodos** - Red completa de múltiples nodos
3. **Test 3: Resiliencia** - Falla y recuperación de nodos

### Ejecución Individual

```python
# Test rápido de 2 nodos
python3 << 'EOF'
from quantum.time_crystal_network import NetworkTimeCrystal
import time

nodeA = NetworkTimeCrystal(node_name="TestA", cluster_name="test")
nodeB = NetworkTimeCrystal(node_name="TestB", cluster_name="test")

nodeA.start_sync()
nodeB.start_sync()

for i in range(100):
    nodeA.tick()
    nodeB.tick()
    time.sleep(0.02)

statsA = nodeA.get_network_stats()
statsB = nodeB.get_network_stats()

print(f"NodeA: Pub={statsA['published_pulses']}, Rcv={statsA['received_pulses']}")
print(f"NodeB: Pub={statsB['published_pulses']}, Rcv={statsB['received_pulses']}")

nodeA.stop_sync()
nodeB.stop_sync()
EOF
```

### Verificación de Salud

```python
from quantum.time_crystal_network import NetworkTimeCrystal

crystal = NetworkTimeCrystal(node_name="health-check")
crystal.start_sync()

# Esperar sincronización
import time
time.sleep(5)

# Verificar
if crystal.is_network_healthy():
    print("✅ Network: HEALTHY")
else:
    print("⚠️  Network: NO PEERS")

crystal.stop_sync()
```

---

## 🎯 CASOS DE USO

### 1. High Availability (HA)

**Problema:** Un solo nodo Sentinel es punto único de falla.

**Solución:** Múltiples nodos sincronizados con failover automático.

```bash
# Nodo Primario
python3 quantum/cortex_main.py --node-name primary --cluster prod

# Nodo Secundario (standby)
python3 quantum/cortex_main.py --node-name secondary --cluster prod

# Si primary cae, secondary detecta timeout y asume control
```

### 2. Distributed Lattice Storage

**Problema:** Lattice holográfico limitado a un nodo.

**Solución:** Lattice distribuido con datos replicados entre nodos.

```python
# Cada nodo tiene acceso al mismo lattice lógico
# La sincronización de tiempo garantiza coherencia de escrituras

node_a = NetworkTimeCrystal(node_name="storage-a")
node_b = NetworkTimeCrystal(node_name="storage-b")

# Ambos nodos sincronizados → escrituras coherentes
# Si node_a escribe en tick 1234567
# node_b lee consistentemente después de tick 1234567
```

### 3. ME-60OS Device Integration

**Problema:** Dispositivos ME-60OS (BCI, Vimana) necesitan sincronización con infraestructura.

**Solución:** Dispositivos se unen al cluster como peers.

```python
# En dispositivo ME-60OS
device_crystal = NetworkTimeCrystal(
    node_name="vimana-01",
    cluster_name="sentinel-prod"
)
device_crystal.start_sync()

# Ahora el Vimana está sincronizado con todos los nodos Sentinel
# Comandos de control tienen timing coherente
```

### 4. Geo-Distributed Services

**Problema:** Servicios en múltiples datacenters necesitan coordinación.

**Solución:** Cada datacenter tiene nodos sincronizados globalmente.

```
DC-US-EAST:  sentinel-us-east-1, sentinel-us-east-2
DC-EU-WEST:  sentinel-eu-west-1, sentinel-eu-west-2
DC-ASIA:     sentinel-asia-1, sentinel-asia-2

Todos en cluster: sentinel-global
```

---

## 🔧 TROUBLESHOOTING

### Problema: Nodos no se encuentran

**Síntoma:**
```
Peers: 0
Published: 5
Received: 0
```

**Causas posibles:**

1. **Redis no corriendo**
   ```bash
   redis-cli ping
   # Si falla: docker-compose up -d redis
   ```

2. **Cluster name diferente**
   ```python
   # Verificar que todos usan el mismo cluster
   nodeA = NetworkTimeCrystal(cluster_name="prod")
   nodeB = NetworkTimeCrystal(cluster_name="prod")  # ← Mismo nombre
   ```

3. **Firewall bloqueando Redis**
   ```bash
   # Verificar puerto 6379 abierto
   telnet localhost 6379
   ```

### Problema: Desincronización frecuente

**Síntoma:**
```
⚠️  DESYNC detectado: node-b (diff=250000000ns)
```

**Causas posibles:**

1. **Carga alta del sistema**
   - Reducir carga de CPU
   - Aumentar prioridad del proceso Sentinel

2. **Latencia de red alta**
   - Verificar latencia Redis: `redis-cli --latency`
   - Debería ser <5ms en LAN

3. **Drift de hardware**
   - Verificar sincronización NTP del host
   - `timedatectl status`

### Problema: Peer marcado offline prematuramente

**Síntoma:**
```
📴 Peer offline: node-c
```

**Solución:**

Aumentar timeout (editar `NetworkTimeCrystal.PEER_TIMEOUT_S`):

```python
# En time_crystal_network.py
PEER_TIMEOUT_S = 20  # Default: 10s
```

### Problema: Redis memory overflow

**Síntoma:**
```
Redis: OOM command not allowed
```

**Solución:**

```bash
# Configurar eviction policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET maxmemory 100mb
```

---

## 📚 API REFERENCE

### NetworkTimeCrystal

#### Constructor

```python
NetworkTimeCrystal(
    redis_host: str = 'localhost',
    redis_port: int = 6379,
    redis_db: int = 0,
    node_name: Optional[str] = None,
    cluster_name: str = 'default'
)
```

**Parámetros:**
- `redis_host`: Host de Redis
- `redis_port`: Puerto de Redis
- `redis_db`: Base de datos Redis
- `node_name`: Identificador del nodo (default: UUID)
- `cluster_name`: Nombre del cluster (múltiples clusters pueden coexistir)

#### Métodos Principales

##### `start_sync()`
Inicia la sincronización de red (abre thread de escucha).

```python
crystal.start_sync()
```

##### `stop_sync()`
Detiene la sincronización de red.

```python
crystal.stop_sync()
```

##### `tick()`
Ejecuta un tick del reloj. Debe llamarse continuamente en loop.

```python
while running:
    crystal.tick()
    time.sleep(0.02)  # ~50Hz
```

##### `get_network_stats() -> dict`
Retorna estadísticas de sincronización.

```python
stats = crystal.get_network_stats()
# {
#   'node_id': 'node-a',
#   'cluster': 'prod',
#   'local_ticks': 12345,
#   'peers_count': 3,
#   'published_pulses': 205,
#   'received_pulses': 615,
#   'desync_events': 0,
#   'network_consensus_drift_ns': 12345,
#   'network_enabled': True
# }
```

##### `get_peer_status() -> List[dict]`
Retorna estado de peers conocidos.

```python
peers = crystal.get_peer_status()
# [
#   {
#     'node_id': 'node-b',
#     'last_tick': 12346,
#     'drift_ns': 12300,
#     'coherence': S60(...),
#     'pulses_received': 205,
#     'last_seen_ago': 1.2,
#     'online': True
#   }
# ]
```

##### `is_network_healthy() -> bool`
Verifica si la red está saludable (al menos 1 peer online).

```python
if crystal.is_network_healthy():
    print("Network OK")
```

#### Propiedades

##### `local_clock`
Acceso al TimeCrystalClock local.

```python
ticks = crystal.local_clock.ticks
coherence = crystal.local_clock.get_coherence()
```

##### `node_id`
Identificador único del nodo.

```python
print(f"My node: {crystal.node_id}")
```

### Constantes Configurables

```python
# En NetworkTimeCrystal class
SYNC_INTERVAL = 60          # Ticks entre publicaciones
CONSENSUS_WINDOW = 10        # Pulsos para consenso
DESYNC_THRESHOLD_NS = 100_000_000  # 100ms
PEER_TIMEOUT_S = 10          # Timeout para marcar peer offline
```

---

## 🎓 CONCEPTOS AVANZADOS

### Consenso de Drift Ponderado

El consenso de drift no es un simple promedio. Se pondera por la **coherencia** de cada nodo:

```
Drift_consensus = Σ(drift_i × coherence_i) / Σ(coherence_i)
```

**Razón:** Nodos con mayor coherencia (relojes más estables) tienen más peso en el consenso.

### Detección de Partición de Red

Si un nodo no ve peers durante `PEER_TIMEOUT_S`:
- Puede estar aislado (network partition)
- Puede ser el único nodo del cluster
- Debe operar en modo standalone

```python
if not crystal.is_network_healthy():
    # Operar en modo standalone
    logger.warning("No peers detected - operating standalone")
```

### Latencia y Jitter

El protocolo tolera latencias de red porque:
1. No requiere sincronización perfecta (tolerancia ~100ms)
2. Los ticks son locales (no bloqueantes)
3. El consenso suaviza jitter de red

Para aplicaciones que requieren sincronización <1ms, considerar PTP (Precision Time Protocol) en hardware.

---

## 📖 REFERENCIAS

- **NTP (Network Time Protocol)**: RFC 5905
- **PTP (Precision Time Protocol)**: IEEE 1588
- **Redis PubSub**: https://redis.io/docs/manual/pubsub/
- **ME-60OS Documentation**: `../ME-60OS/AI_SYSTEM_PROMPT.md`
- **TimeCrystalClock**: `time_crystal_clock.py`

---

## 📝 CHANGELOG

### v1.0.0 (2026-01-19)
- ✅ Implementación inicial de QNTP
- ✅ Sincronización multi-nodo vía Redis PubSub
- ✅ Detección automática de peers
- ✅ Consenso de drift ponderado por coherencia
- ✅ Detección de nodos offline (timeout)
- ✅ Suite completa de tests
- ✅ Integración con cortex_main.py

---

## 👥 CONTRIBUCIÓN

Este módulo es parte del proyecto **Sentinel** y sigue las directivas de **ME-60OS**.

**Reglas:**
- ❌ **NO usar floats** en código core (solo S60)
- ❌ **NO usar numpy/random**
- ✅ **Usar aritmética entera exacta**
- ✅ **Documentar todo cambio**

---

## 📜 LICENCIA

Parte del proyecto Sentinel - ME-60OS Development Team

---

**💎 Network Time Crystal - Sincronización Cuántica Distribuida 💎**