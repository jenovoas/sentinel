# 🔍 Diagnóstico y Solución de Paneles "No Data" en Grafana Master

> **Servidor Target:** Fan  
> **Dashboard:** `SecurePenguin — Monitoreo` (`uid: a5s799`)  
> **Fecha:** 29 de Julio, 2026

---

## 📸 1. Análisis de la Captura de Pantalla del Usuario

En la captura de pantalla provista:
1. **Paneles Prometheus / Gauge & TimeSeries Operativos 🟢**:
   - `Sentinel Cortex - Thermal Noise CPU (°C)`: **38 °C**
   - `LiquidLattice Memory 3x3 Retention Score`: **0.0375**
   - `AIOpsShield Interceptions`: **2**
   - `Security Lane WAL Entries & XDP Network Firewall`: **WAL Entries = 2, XDP = 1**
   - `Resonant Lattice 64-Node Amplitudes & Phases`: Ondas de amplitud y fase resonantes en vivo.

2. **Paneles Loki en "No Data" 🔴**:
   - `Automated Invariant Verifier Logs (sentinel-verifier JSON Stream)`
   - `Ring-0 Kernel eBPF Syscall Trace Stream (ebpf-forwarder)`

---

## 🛠️ 2. Diagnóstico Técnico de la Causa Raíz

1. **Rechazo de Muestras Antiguas en Loki**:
   - Promtail estaba reintentando enviar logs antiguos de `/var/log/sentinel/sentinel_verifier.log` y `/var/log/sentinel/ebpf_trace.log`, pero Loki descartaba los bloques por exceder el parámetro de tiempo por defecto (`entry too far behind / ingestion rate limit exceeded`).

2. **Configuración de Filtro / Path**:
   - Promtail usaba la ruta antigua `/var/log/sentinel/*.log` pero Loki `tsdb` mantenía el índice desalineado con la etiqueta de servicio.

---

## ✅ 3. Solución Implementada

1. **Actualización del Config de Loki (`/etc/sentinel/loki.yaml`)**:
   - Desactivado el rechazo de muestras pasadas (`reject_old_samples: false`).
   - Incrementada la ventana de ingesta a 168 horas y la tasa a 32MB/s.
2. **Re-lanzamiento de Promtail (`promtail:3.4`)**:
   - Promtail ahora escanea y transmite en vivo los logs de `/var/log/sentinel/sentinel_verifier.log` y del Journal de Linux.
3. **Flujo de Trazas Habilitado**:
   - Los paneles se actualizarán automáticamente en los próximos ciclos de refresco de 5s en Grafana.

