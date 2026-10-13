# 🛡️ eBPF-Cortex Integration Status

**Fecha:** 6 de Agosto, 2026 (Actualizado)
**Estado:** ✅ Operativo / Path corregido
**Componentes:** Kernel Ring 0 <-> Userspace Ring Buffer

## 🚨 Incidente de Sincronización (Histórico)

Se detectó una discrepancia entre el `@SYSTEM_PROMPT` (que indicaba la integración como "Completada" el 19/01/2026) y el sistema de archivos (donde faltaban los componentes clave).

**Acción Correctiva:** Se han materializado y verificado los artefactos perdidos.

## ✅ Arquitectura Implementada (Actualizada 2026-08-06)

### 1. Verdad Compartida (`ebpf/cortex_events.h`)

- Definición de structs `cortex_event_t` y `s60_entropy_t`.
- Alineación C/Rust garantizada.
- Tipos `u60` simulados con enteros estrictos.

### 2. Kernel Modules (LSM - Multiple Variants)

- **`guardian_alpha_lsm.c`** — Versión base, hooks `file_open` + `bprm_check_security`
- **`lsm_ai_guardian.c`** — Versión avanzada con AI agent tracking
- **`ai_guardian.c`** — Versión completa ME-60OS con S60 entropy
- **`guardian_cognitive.c`** — Guardian cognitivo
- **`float_detector.c`** — Detector de contaminación float

**Mapas:** `BPF_MAP_TYPE_RINGBUF` (256KB) cada uno.
**Hooks:** `lsm/file_open` y `lsm/bprm_check_security`.
**Lógica:** Cálculo de entropía S60 determinista dentro del kernel.
**Estado:** Código compilado y respaldado.

### 3. Userspace Bridge (`sentinel-cortex/src/ebpf_cortex_bridge.rs`)

- Implementación Rust usando `libbpf-rs`.
- Deserialización segura de eventos desde el Ring Buffer.
- Mapeo a tipos nativos Rust.

### 4. Configuración & Paths Reales (2026-08-06)

- **LSM programs cargados en:** `/sys/fs/bpf/guardian_alpha_lsm`, `/sys/fs/bpf/lsm_ai_guardian`, `/sys/fs/bpf/ai_guardian`, `/sys/fs/bpf/guardian_cognitive`, `/sys/fs/bpf/float_detector`
- **Ring buffer principal (PAI daemon):** `/sys/fs/bpf/sentinel/events` (pinned por `guardian_gamma.c` via `bpftool prog loadall ... pinmaps /sys/fs/bpf/sentinel`)
- **Gamma watchdog:** `/sys/fs/bpf/sentinel/gamma`
- **Configuración:** `sentinel-cortex/Cargo.toml`: dependencias `libbpf-rs` y `libc`
- **PAI Neural Daemon:** Lee de `/sys/fs/bpf/sentinel/events` (fallback a `/sys/fs/bpf/cortex_events` para compatibilidad)

### 5. Verificación (`tests/test_integration_e2e.py`)

- Suite de tests Python creada.
- Validación de existencia de archivos.
- Verificación cruzada de definiciones de estructuras (C vs Rust).
- Simulación de lógica matemática S60 para asegurar consistencia.
- **Resultado:** 5/5 Tests PASADOS.

---

## ⚠️ Notas de Migración (2026-08-06)

| Documento Antiguo | Path Real Actual |
|---|---|
| `/sys/fs/bpf/ai_guardian/cortex_events` | **`/sys/fs/bpf/sentinel/events`** |
| `/sys/fs/bpf/cortex_events` | **`/sys/fs/bpf/sentinel/events`** (fallback) |
| LSM individual pins | `/sys/fs/bpf/guardian_alpha_lsm`, `/sys/fs/bpf/lsm_ai_guardian`, etc. |
| Gamma watchdog | `/sys/fs/bpf/sentinel/gamma` |

**Los docs que referencian `/sys/fs/bpf/ai_guardian/cortex_events` están DESACTUALIZADOS y deben actualizarse.**

---

## 🔧 Comandos de Carga Actuales

```bash
# Cargar LSMs individuales
sudo bpftool prog load guardian_alpha_lsm.o  /sys/fs/bpf/guardian_alpha_lsm  type lsm
sudo bpftool prog load lsm_ai_guardian.o     /sys/fs/bpf/lsm_ai_guardian     type lsm
sudo bpftool prog load ai_guardian.o         /sys/fs/bpf/ai_guardian         type lsm
sudo bpftool prog load guardian_cognitive.o  /sys/fs/bpf/guardian_cognitive  type lsm
sudo bpftool prog load float_detector.o      /sys/fs/bpf/float_detector      type lsm

# Cargar Gamma (autoattach + pinmaps en /sys/fs/bpf/sentinel)
sudo bpftool prog loadall guardian_gamma.o /sys/fs/bpf/sentinel/gamma autoattach pinmaps /sys/fs/bpf/sentinel

# Verificar estado
sudo bpftool prog show | grep -E "guardian|ai_guardian|float_detector|gamma"
ls -la /sys/fs/bpf/sentinel/
```

---

*Actualizado: 2026-08-06 — Paths corregidos tras verificación en código Rust (`pai_neural_daemon.rs`) y Makefile eBPF.*