# 🧪 Reporte de Pruebas Manuales y Análisis de Seguridad de Sentinel
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Entorno:** Servidor Fan (`10.88.0.1`) — Producción Física  
> **Fecha:** 29 de Julio, 2026  
> **Metodología:** Verificación manual de endpoints, estado de daemons e inspección de vectores de vulnerabilidad.

---

## 🔬 1. RESULTADOS DE PRUEBAS MANUALES (END-TO-END)

| Componente | Prueba Realizada | Resultado | Detalle |
|------------|------------------|-----------|---------|
| **`sentinel-cortex` Health** | `curl -s http://127.0.0.1:8000/health` | 🟢 OK (`200 OK`) | Status OK, Coherence 100%, Efficiency 95% |
| **Matriz Resonante S60** | `curl -s http://127.0.0.1:8000/api/v1/lattice` | 🟢 OK (`200 OK`) | Total Energy `1,385,357,992,528`, 64 nodos activos en Base-60 |
| **Exporter Prometheus** | `curl -s http://127.0.0.1:8000/metrics` | 🟢 OK (`200 OK`) | Métrica `sentinel_cpu_temperature_celsius` (45.0°C) + Amplitudes por nodo |
| **`sentinel-gamma-watchdog`** | `systemctl status sentinel-gamma-watchdog` | 🟢 RUNNING | Hook LSM vigilando `/sys/fs/bpf`, latido de 17s en log (`detail: alive`) |
| **`sentinel-qhc-agent`** | `systemctl status sentinel-qhc-agent` | 🟢 RUNNING | Modulación de fase YHWH (Tick 25228 con Salto 17 correction) |
| **`sentinel-pai-neural`** | `systemctl status sentinel-pai-neural` | 🟢 RUNNING | Polleando eBPF Ring Buffer `/sys/fs/bpf/sentinel/events` |
| **`sentinel-vid-agent`** | `systemctl status sentinel-vid-agent` | 🟢 RUNNING | Dynamic Inertia actuando (`COOLING / CONTRACTING` según util de buffer) |
| **`sentinel-hex-daemon`** | `systemctl status sentinel-hex-daemon` | 🟢 RUNNING | Pilar 2 activo (127 nodos axiales, Salto 17 `STABLE`) |
| **Grafana Observabilidad** | `curl -s http://127.0.0.1:3001/api/health` | 🟢 OK (`200 OK`) | Escuchando en puerto **3001** (`GF_SERVER_HTTP_PORT=3001`) |
| **Loki Log Aggregator** | `curl -s http://127.0.0.1:3100/ready` | 🟡 INITIALIZING | Inicializando inyector |

---

## 🛡️ 2. ANÁLISIS DE FALLAS DE SEGURIDAD (SECURITY AUDIT)

A partir de la inspección del sistema en producción en Fan, se han identificado **5 hallazgos críticos de seguridad**:

### 🚨 Hallazgo 1: Falta de Autenticación en la API Cortex (`:8000`)
- **Vulnerabilidad:** Los endpoints HTTP `/health`, `/metrics` y `/api/v1/lattice` están expuestos sin Bearer token ni autenticación mTLS.
- **Riesgo:** Un atacante en la red local (`10.88.0.x`) podría pollear el estado de la matriz resonante o saturar el puerto con peticiones masivas.
- **Remediación:** Implementar un middleware de autenticación por Token de Sesión/API Key en Axum o restringir el binding a `127.0.0.1`.

### 🚨 Hallazgo 2: Permisos de eBPF Map Pinned (`/sys/fs/bpf/sentinel/events`)
- **Vulnerabilidad:** El mapa de Ring Buffer eBPF está fijado en `/sys/fs/bpf/sentinel/events`. Si los permisos del sistema de archivos eBPF no están restringidos a `root:root` (0600), un usuario no privilegiado en la máquina podría inyectar o corruptor eventos del kernel.
- **Remediación:** Enforzar `chmod 600 /sys/fs/bpf/sentinel/events` e inspeccionar SELinux/AppArmor labels.

### 🚨 Hallazgo 3: Fallback de Temperatura CPU Hardcoded
- **Vulnerabilidad:** Si `/sys/class/thermal/thermal_zone0/temp` falla o no existe (ej. en ciertos contenedores), el Cortex asume 45.0°C estáticos (`unwrap_or(45000)`).
- **Riesgo:** Si un atacante manipula el sensor térmico del sistema de archivos, podría alterar artificialmente el ruido térmico inyectado a la Lattice.
- **Remediación:** Validar la firma/origen de la lectura del sensor y alertar si la lectura permanece idéntica o fuera de rango físico.

### 🚨 Hallazgo 4: Grafana en Modo por Defecto (`3001`)
- **Vulnerabilidad:** Grafana está expuesto en el puerto 3001 con credenciales por defecto si no han sido modificadas.
- **Remediación:** Forzar el cambio de clave `admin` y restringir el acceso a través de un proxy inverso con HTTPS (Nginx/Traefik).

### 🚨 Hallazgo 5: Intentos de Fallback en Redis sin Cifrado (TLS)
- **Vulnerabilidad:** La conexión a Redis (`redis://127.0.0.1:6379`) no usa TLS (`rediss://`).
- **Remediación:** Si el tráfico de Redis cruza la red hacia el nodo de laptop, debe encriptarse a través de la interfaz WireGuard `wg0` o usar TLS habilitado en Redis.
