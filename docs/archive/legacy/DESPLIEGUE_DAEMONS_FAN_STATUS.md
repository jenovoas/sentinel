# 🌐 Matriz de Despliegue de Daemons en Servidor Fan (Producción)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Nodo de Prueba/Navegación:** Laptop (`10.88.0.2`)  
> **Fecha:** 29 de Julio, 2026

---

## 🟢 Estado de la Trinidad de Daemons en Producción

| Daemon Systemd | Binario Compilado | Componente Teórico / Función | Estado en Fan |
|----------------|-------------------|------------------------------|---------------|
| `sentinel-cortex.service` | `sentinel-cortex` | API Axum (:8000), Prometheus Exporter (:9091), Ingestión Ring-0 + Termodinámica CPU | 🟢 Active (Running) |
| `sentinel-gamma-watchdog.service` | `gamma_watchdog` | LSM/eBPF Ring-0 Metavigilancia inotify `/sys/fs/bpf` + Heartbeat 17s | 🟢 Active (Running) |
| `sentinel-qhc-agent.service` | `qhc_agent` | Modulador de Fase Armónica 10-5-6-5 (YHWH Driver) | 🟢 Active (Running) |
| `sentinel-pai-neural.service` | `pai_neural_daemon` | Polleo eBPF Ring Buffer → Actualización Memoria Neuronal PAI-60 | 🟢 Active (Running) |
| `sentinel-vid-agent.service` | `vid_agent` | Dynamic Inertia & Optomechanical Cooling (Ajuste dinámico de masa de buffer) | 🟢 Active (Running) |
| `sentinel-hex-daemon.service` | `hex_daemon` | Pilar 2: Control Geométrico Hexagonal (91 Nodos) + Estabilización Salto 17 | 🟢 Active (Running) |

---

## 📊 Endpoints de Observabilidad Activos en Fan

- **Prometheus Metrics (Port 9091 / HTTP 8000 `/metrics`)**:
  - `sentinel_cpu_temperature_celsius` (Sensor térmico CPU real)
  - `sentinel_lattice_total_energy` (Energía total de la Matriz Resonante S60)
  - `sentinel_lattice_node_amplitude{node="X"}` (Amplitud por nodo)
- **Grafana (Port 3005)**:
  - Dashboard: `Sentinel - Time Crystal & Resonant Lattice Matrix`
- **Cortex API REST (Port 8000)**:
  - `GET /health`
  - `GET /api/v1/lattice`
