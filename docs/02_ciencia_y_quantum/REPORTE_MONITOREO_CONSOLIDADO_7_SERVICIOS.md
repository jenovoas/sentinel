# 📊 Monitoreo Integrado de los 7 Daemons Activos de Sentinel en Fan

> **Servidor:** Fan (`10.88.0.1`)  
> **Grafana Master:** `http://10.88.0.1:3001`  
> **Dashboard:** `Sentinel Cluster Master - 7 Systemd Daemons Telemetry` (UID: `akxpvg`)  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 Estado de los 7 Servicios y Trazas en Loki

Toda la pila de **7 servicios systemd** de Sentinel se encuentra siendo ingerida en tiempo real por **Promtail** y almacenada en **Loki 3.4** con etiquetas unificadas (`job="sentinel_systemd"`, `job="sentinel_file_logs"`):

| Servicio | Uptime / Tiempo | Estado | Trazas Verificadas en Loki |
|----------|------------------|--------|----------------------------|
| **`sentinel-cortex.service`** | ~13 min | Active (`RUNNING`) | Ingesta HTTP, Ring-0 eBPF fallback y LiquidLattice 3x3. |
| **`sentinel-hex-daemon.service`** | ~2h 27 min | Active (`RUNNING`) | `🔷 TICK 9065 \| Hex Lattice Nodes: 127 \| Status: STABLE (Salto 17)` |
| **`sentinel-qhc-agent.service`** | ~9h | Active (`RUNNING`) | `🔹 TICK 34120 \| Pattern: Y (10) \| Mod: 10` (Fase YHWH) |
| **`sentinel-vid-agent.service`** | ~2h 29 min | Active (`RUNNING`) | `⚡ ACTION: COOLING (v=SPA[-000; 02, 00, 00, 00]) \| Resize` |
| **`sentinel-pai-neural.service`** | ~9h | Active (`RUNNING`) | RingBuffer Event Poller eBPF. |
| **`sentinel-gamma-watchdog.service`** | ~9h | Active (`RUNNING`) | `{"event_type":18,"guardian_code":5,"source":"gamma_watchdog"}` |
| **`ebpf-forwarder.service`** | ~11h | Active (`RUNNING`) | bpftool state sync (PID & Maps tracker). |

---

## 📈 Paneles Configurados en Grafana (`http://10.88.0.1:3001/d/akxpvg`)

1. **`Sentinel Cortex - Thermal Noise CPU (°C)`** (Gauge): Monitorea la temperatura real física en vivo.
2. **`LiquidLattice Memory 3x3 Retention Score (EXP-009)`** (Gauge): Medición en tiempo real de la tasa de retención S60 ($\ge 0.72$).
3. **`Total Raw Energy in Lattice`** (Stat): Energía raw instantánea en el espacio de estados.
4. **`System Active Daemons Status (7 Services)`** (Stat): Estado global de los 7 daemons de systemd.
5. **`Daemons Memory Usage (7 Services)`** (Timeseries): Consumo continuo de RAM (rango 236K - 1.9M - 142M).
6. **`Daemons CPU Consumed Time (7 Services)`** (Timeseries): Consumo continuo de ciclos CPU por proceso.
7. **`Loki Logs - Combined Journal Streams (7 Services)`** (Logs Panel): Logstream unificado de los 7 daemons en tiempo real.

