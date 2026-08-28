# 🔬 Reporte Técnico y Análisis de los 4 Puntos Críticos (Sin Interpretaciones)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor Target:** Fan (`10.88.0.1`)  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Análisis del SEGV de `sentinel-cortex` de las 13:52

- **Causa Raíz Identificada**: El coredump en `__vfprintf_internal` ocurrió al intentar invocar `MapHandle::from_pinned_path` de `libbpf-rs` mientras el pin de espacio de usuario no era accesible o estaba corrupto.
- **Estado Actual**: Se aisló con `std::panic::catch_unwind` y manejo de fallback en `ebpf_cortex_bridge.rs`. El proceso se mantiene totalmente estable desde las 18:13 sin crashes registrando `RING0_PINNED_ACTIVE`.

---

## 📉 2. Análisis del `retention_score = 0.0000` en LiquidLattice 3x3

- **Causa Raíz Identificada en Código**: En [`liquid_lattice.rs:L90`](file:///home/jnovoas/Proyectos/sentinel/sentinel-cortex/src/memory/liquid_lattice.rs#L90):
  ```rust
  (total_amp.to_base_units() as f64 / 1_000_000.0).min(1.0)
  ```
- **Falla en el Escalado**: `total_amp.to_base_units()` entrega el valor en Terceras sexagesimales ($216.000 = 1.0$). Si no ha habido inyección de eventos eBPF desde Ring-0 en el canal `rx_lattice` (o si la amplitud inicial es `S60::zero()`), la suma es `0.0000`. No es un desbordamiento, es que las amplitudes arrancan en 0 hasta que el RingBuffer inyecte entropía.

---

## 🐶 3. Análisis de los 2 Peers Faltantes en `gamma-watchdog`

- En [`gamma_watchdog.c:L44-L50`](file:///home/jnovoas/Proyectos/sentinel/ebpf/gamma_watchdog.c#L44-L50), la constante `PEERS[]` contiene 5 nombres:
  1. `guardian_alpha_lsm` $\rightarrow$ Registrado como `guardian_alpha`
  2. `guardian_cognitive` $\rightarrow$ Registrado (prog_id=8)
  3. `ai_guardian` $\rightarrow$ Registrado (prog_id=6)
  4. `lsm_ai_guardian` $\rightarrow$ **FALTANTE** (El pin `/sys/fs/bpf/lsm_ai_guardian` no existe)
  5. `float_detector` $\rightarrow$ Registrado (prog_id=7)
- **Diagnóstico**: `lsm_ai_guardian` y `guardian_alpha_lsm` usan nombres de pin ligeramente distintos (`guardian_alpha` en lugar de `guardian_alpha_lsm`). Por eso detecta 3 de 5 peers.

---

## 🛰️ 4. Análisis de `ebpf-forwarder` y `trace_pipe` Ocupado

- `sentinel-ebpf-forwarder.service` ejecuta `/usr/sbin/bpftool prog tracelog`.
- Al ejecutar `cat /sys/kernel/debug/tracing/trace_pipe` directamente en Fan, el kernel responde:
  `cat: /sys/kernel/debug/tracing/trace_pipe: Device or resource busy`.
- **Diagnóstico**: `bpftool prog tracelog` mantiene bloqueado en exclusiva el `trace_pipe` del kernel leyendo las trazas. Por eso no imprime logs nuevos en journald y redirige todo hacia `/var/log/sentinel/ebpf_trace.log`.
