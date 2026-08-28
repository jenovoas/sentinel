# 📊 Monitoreo Completo de los Nodos de la Rejilla Resonante (`Lattice Nodes 0 a 63`)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Prometheus Endpoint:** `http://127.0.0.1:8000/metrics`  
> **Grafana Master:** `http://10.88.0.1:3001/d/a5s799/securepenguin-e28094-monitoreo`  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Métricas de Nodos Expuestas en Tiempo Real por `sentinel-cortex`

Auditamos la salida del endpoint `/metrics` en Fan y confirmamos la exportación de las series temporales de **todos los nodos de la Lattice** (Nodos 0 a 63):

1. **Amplitudes Dinámicas de Nodos (`sentinel_lattice_node_amplitude{node="N"}`)**:
   - `node="0"`: `96,750,065,127` (Nodo Ancla Central acoplado al sensor térmico de CPU).
   - `node="1"` a `node="63"`: Gradiente de propagación de difusión sexagesimal S60.
2. **Fases Harmónicas de Nodos (`sentinel_lattice_node_phase{node="N"}`)**:
   - Fases sincronizadas al pulso $S60$ (`20,967,034` tercia).
3. **Total Energy in Lattice (`sentinel_lattice_total_energy`)**:
   - Suma total de energía en el espacio de estados.

---

## 📈 2. Paneles Incorporados al Dashboard de Grafana

Actualizamos el Dashboard Master (`http://10.88.0.1:3001/d/a5s799/securepenguin-e28094-monitoreo`) integrando dos paneles dedicados a la visualización de la Lattice:

* **Panel 8 — `Resonant Lattice 64-Node Amplitudes Distribution (Nodes 0 to 63)`**:
  - Gráfico de series temporales en vivo con las curvas de amplitud de cada uno de los 64 nodos.
* **Panel 9 — `Resonant Lattice 64-Node Harmonic Phases (Nodes 0 to 63)`**:
  - Gráfico en vivo de la evolución de fase de todos los nodos.
* **Panel 4 — `Hex Lattice Nodes Status (127 Nodes - sentinel-hex-daemon)`**:
  - Contador en vivo de los nodos activos en el clúster.
