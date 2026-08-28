# 🔬 Diagnóstico e Ingeniería: PAI-Neural Daemon e Integración Ring-0 eBPF
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor Target:** Fan (`10.88.0.1`)  
> **Daemon Ring-0:** `pai_neural_daemon` (`me-60os-core/src/bin/pai_neural_daemon.rs`)  
> **Servicio Systemd:** `sentinel-pai-neural.service`  
> **Mapa eBPF Target:** `/sys/fs/bpf/cortex_events` (ID 36)  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Diagnóstico de la Brecha PAI-Neural en Ring-0

1. **Ruta del RingBuffer Pinned**:
   En [`me-60os-core/src/bin/pai_neural_daemon.rs:L23`](file:///home/jnovoas/Proyectos/sentinel/me-60os-core/src/bin/pai_neural_daemon.rs#L23), el daemon intentaba abrir `/sys/fs/bpf/sentinel/events` (ruta legada de versiones anteriores).
2. **Ubicación Pinned Real en Kernel**:
   En el kernel actual de Fan, los programas LSM Ring-0 (`ai_guardian.c`) publican sus eventos de entropía sexagesimal en la ruta pineada:
   `👉 /sys/fs/bpf/cortex_events`

---

## 🛠️ 2. Solución Aplicada en Código Fuente

Actualizamos la ruta del mapa pineado en [`me-60os-core/src/bin/pai_neural_daemon.rs:L23`](file:///home/jnovoas/Proyectos/sentinel/me-60os-core/src/bin/pai_neural_daemon.rs#L23) para que apunte directamente a `/sys/fs/bpf/cortex_events`:

```rust
// Apuntamos al mapa pinned real cargado por LSM ai_guardian
let ringbuf_path = if Path::new("/sys/fs/bpf/cortex_events").exists() {
    "/sys/fs/bpf/cortex_events"
} else {
    "/sys/fs/bpf/sentinel/events"
};
```
