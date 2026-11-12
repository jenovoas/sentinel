---
titulo: P0.2 — Guardian y aislamiento temporal por PID
aliases:
  - Contrato P0.2 de aislamiento del Guardian
tags:
  - sentinel
  - p0-2
  - guardian-lsm
estado: preparado-localmente
updated: 2026-11-12
---

# P0.2 — Guardian y aislamiento temporal por PID

## Contrato implementado

- `requester_pid` es un campo opcional de la tarea SOMA. Solo un rechazo semántico intenta aislar ese PID; una coherencia insuficiente bloquea el despacho sin aislar procesos.
- Los eventos eBPF `EVENT_FILE_BLOCKED` (1) y `EVENT_EXEC_BLOCKED` (2) aplican aislamiento temporal. `EVENT_FLOAT_CONTAMINATION` (10) queda como telemetría y no aísla.
- El mapa `pid_isolation_map` usa una clave `u32` (PID) y un valor `u64` (caducidad en nanosegundos monotónicos). Guardian Alpha bloquea futuras llamadas `execve` de ese PID hasta que expire el plazo de 300 segundos.
- El aislamiento no termina un proceso existente ni cierra sus descriptores. El PID puede reutilizarse durante el TTL.
- La ruta de mapa esperada por el usuario es `/sys/fs/bpf/sentinel/pid_isolation_map`; el cargador debe fijar los mapas del objeto en `/sys/fs/bpf/sentinel` para que el proceso Rust y el LSM compartan la misma instancia.
- La caducidad de Rust usa `CLOCK_MONOTONIC`; `bpf_ktime_get_ns()` tiene la misma referencia temporal según `/usr/include/linux/bpf.h`.

## Trazabilidad

- Código: `me-60os-core/src/guardian_lsm.rs`, `me-60os-core/src/resonance_engine.rs`, `me-60os-core/src/soma_orchestrator.rs`, `sentinel-cortex/src/security/bio_resonance.rs`, `sentinel-cortex/src/main.rs` y `ebpf/guardian_alpha_lsm.c`.
- CI eBPF incluye la compilación focal de `guardian_alpha_lsm.o` en `.github/workflows/ebpf.yml`.
- Validación local del 2026-11-12: compiló `guardian_alpha_lsm.o` con `make -C ebpf guardian_alpha_lsm.o`; `cargo check -p me60os --bin soma-orchestrator` y `cargo check -p sentinel-cortex` terminaron correctamente; `cargo fmt --all -- --check` y `git diff --check` pasaron.
- Estado operativo: preparación local. No se cargó ni conectó el objeto eBPF, no se modificó Fan y no se desplegó producción.

## Referencias

- [Procedimiento de despliegue multinodo](PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md)
- Contexto de decisiones: `personalvault/docs/AGENT_BRAIN.md` (P0.2/P0.3 estaba en pausa; Jaime reanudó el trabajo en esta sesión).
