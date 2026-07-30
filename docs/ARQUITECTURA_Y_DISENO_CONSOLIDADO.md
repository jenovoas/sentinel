# 🏛️ Arquitectura Consolidada y Registro de Conocimiento de Sentinel

> **Fecha de Consolidación:** 29 de Julio, 2026
> **Estado:** 🟢 Producción Activa (Laptop ↔ Servidor Fan)
> **Workspace Consolidado:** `me-60os-core` importado dentro de `Proyectos/sentinel`

---

## 1. 📐 Fundamentación Teórica e Isomorfismo Físico

El proyecto **Sentinel** se fundamenta en la traslación de la matemática sexagesimal en Base-60 (inspirada en los principios hidráulicos de Plimpton 322) al cómputo distribuido moderno de baja latencia.

### Principios Fundamentales:
1. **Aritmética Entera Fija S60 (Cero Error de Redondeo)**:
   Se elimina el ruido térmico y la discrepancia infinitesimal introducida por el punto flotante IEEE-754. Toda la computación de fase, entropía y energía se ejecuta en base 60 pura (`me60os_core::spa::SPA`).

2. **Simetría Temporal y Conservación de Energía**:
   La matriz acoplada de 64 nodos (**Resonant Matrix / Time Crystal**) evoluciona mediante dinámica de campos discretos:
   $$\Delta A_i = -\left( \frac{(A_i - A_{i+1}) \cdot \kappa}{60} \right)$$
   donde $\kappa = \frac{10}{60} \approx 0.167$ modela el acoplamiento armónico entre nodos vecinos.

3. **Arquitectura Fisiológica de 7 Niveles & Dual Guardians**:
   - **Nervio A (Alpha Guardian - LSM)**: Intercepción determinista en el Kernel Ring-0 (`bprm_check_security`, `file_open`).
   - **Nervio B (Cognitive & Neural Guard)**: Evaluación semántica y correlación de patrones a nivel de espacio de usuario.
   - **Gamma Watchdog**: Daemon de metavigilancia en espacio de usuario que supervisa la integridad de los pins de eBPF e inyecta un latido armónico de 17 segundos en `/sys/fs/bpf/gamma_heartbeat`.

---

## 2. 🗂️ Estructura del Workspace Consolidado en `sentinel/`

Para evitar la dispersión de código y compilar todo desde un único punto de verdad, el núcleo `me-60os` fue importado directamente dentro de `sentinel/me-60os-core`:

```
Proyectos/sentinel/
├── Cargo.toml                      # Workspace unificado (cortex, neural-guard, me-60os-core)
├── me-60os-core/                   # Núcleo S60, Resonant Matrix y Daemons nativos
│   ├── src/
│   │   ├── resonant_matrix.rs      # Matriz Resonante de 64 nodos (Time Crystal)
│   │   ├── spa.rs                  # Aritmética de punto fijo S60 Base-60
│   │   ├── neural_memory.rs        # Estructura de Memoria Neuronal PAI-60
│   │   └── bin/
│   │       ├── pai_neural_daemon.rs # Consumidor de Ring Buffer eBPF
│   │       ├── qhc_agent.rs         # Modulador de fase YHWH 10-5-6-5
│   │       └── adm_agent.rs         # Modelo de Difusión Axial para mesh
├── sentinel-cortex/                # API Axum + Bridge Ring-0 + Exporter Prometheus
│   ├── src/
│   │   ├── main.rs                 # Servidor HTTP/WS (Puertos 8000 & 9091)
│   │   └── ebpf_cortex_bridge.rs   # Deserialización cero-copia del Ring Buffer
├── services/neural-guard/          # Motor de decisión y correlación de eventos
├── ebpf/                           # Código fuente C y hooks LSM/XDP
│   ├── gamma_watchdog.c            # Metavigilancia eBPF Ring-0
│   └── cortex_events.h             # Structs compartidos C/Rust
├── docs/                           # Documentación técnica, papers y estado
└── scripts/                        # Scripts de mantenimiento y despliegue
```

---

## 3. ⚙️ Daemons y Servicios Activos en Producción (Servidor Fan)

| Servicio | Binario | Propósito / Función | Estado |
|----------|---------|---------------------|--------|
| `sentinel-cortex.service` | `sentinel-cortex` | API Axum (:8000), Exporter Prometheus (:9091), Ingestión Ring-0 | ✅ Active (Running) |
| `sentinel-gamma-watchdog.service` | `gamma_watchdog` | Metavigilancia inotify en `/sys/fs/bpf`, Heartbeat 17s | ✅ Active (Running) |
| `sentinel-qhc-agent.service` | `qhc_agent` | Modulación de fase armónica 10-5-6-5 (YHWH Driver) | ✅ Active (Running) |
| `sentinel-pai-neural.service` | `pai_neural_daemon` | Polleo de `/sys/fs/bpf/sentinel/events` → Memoria Neuronal | ✅ Active (Running) |
| `redis-sentinel` | Podman | Broker de eventos y estado RAM asistido Lane A (:6379) | ✅ Active (Running) |
| `sentinel-prometheus` | Podman | Scraping de métricas cada 2s en `:9091` | ✅ Active (Running) |
| `sentinel-grafana` | Podman | Dashboard de observabilidad en `:3005` (admin/admin) | ✅ Active (Running) |

---

## 4. 📊 Endpoints e Interfaces de Observabilidad

1. **Dashboard en Grafana**:
   `http://10.88.0.1:3005/d/sentinel-time-crystal/sentinel-time-crystal-and-resonant-lattice-matrix`
2. **Prometheus Metrics Target**:
   `http://10.88.0.1:9091/targets` (Métricas `sentinel_lattice_total_energy`, `sentinel_lattice_node_amplitude`, etc.)
3. **Cortex API REST**:
   - `GET http://10.88.0.1:8000/health` — Health check
   - `GET http://10.88.0.1:8000/api/v1/lattice` — Estado raw de los 64 nodos del Cristal de Tiempo
   - `GET http://10.88.0.1:8000/metrics` — Formato estándar Prometheus

