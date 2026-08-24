# Sentinel — Sexagesimal Systems Framework

**Framework de sistemas de bajo nivel que implementa aritmética base-60 exacta (S60) como fundamento matemático del runtime, eliminando los errores de redondeo IEEE 754 de la cadena de cálculo.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?logo=rust)](./sentinel-cortex/)
[![eBPF](https://img.shields.io/badge/eBPF-kernel--level-orange)](./ebpf/)

> [!NOTE]
> **Runtime 100% Rust.** La migración Py→Rust terminó. Los `.py` restantes en `quantum/` son material de estudio o puentes legacy (`LEGACY BRIDGE / MIGRADO / YATRA-protected`) — no forman parte del runtime activo.
> Producción real: servidor **Fan** (nodo único Fenix, Podman rootless).

---

## Fases del Proyecto

1. **PoC Inicial (legacy):**
   * `backend/` + `docker-compose.yml` — Python (FastAPI/Celery/Nginx).
   * Prueba de concepto original. **No se usa en producción.**

2. **Producción actual (Nodo Único Fenix):**
   * `docker-compose.fenix.yml` + workspace Cargo descrito abajo.
   * Stack: **Rust**, Podman, Traefik, eBPF Ring-0, systemd units por daemon.

3. **Visión Fase 2 (Cluster Multi-Nodo):**
   * Mesh S60 distribuido vía [MycNet](https://github.com/) (ver `docs/archive/` para el diseño histórico).

---

## Workspace Cargo (5 crates)

```
sentinel/
├── sentinel-cortex/     Crate principal: servidor Axum, drive continuo, ingesta eBPF,
│                        LiquidLattice 3x3, TruthSync, API REST (/api/v1/*, /metrics)
├── me-60os-core/        Núcleo numérico y físico: SPA/S60, PAI-60, ResonantMatrix,
│                        IsochronousOscillator, QHC, Guardian LSM, Dual-Lane (32 bins:
│                        experimentos EXP-XXX, benches, daemons nativos, TUI)
├── truthsync-core/      Motor de verificación de claims sobre energía del lattice
├── sentinel-verifier/   Verificador de invariantes runtime (systemd --watch 15 --json)
├── services/neural-guard/  Correlación de eventos + disparo de playbooks n8n
├── ebpf/                Programas kernel: guardian_alpha_lsm.c (ACTIVO),
│                        guardian_cognitive, float_detector, gamma_watchdog;
│                        ai_guardian.c DESACTIVADO — no usar file_open ni
│                        /sys/fs/bpf/ai_guardian
├── quantum/             LEGADO: .py con headers LEGACY BRIDGE / MIGRADO — estudio
└── constraints/         YATRA_SPEC.md — contrato inmutable de la aritmética
```

## El Problema: La Deriva del Punto Flotante

IEEE 754 convierte fracciones comunes en sistemas binarios (`1/3`, `1/6`, `1/12`, `1/60`) en periódicos que acumulan error de redondeo. La base-60 (sexagesimal babilónica) es divisible por 1, 2, 3, 4, 5, 6, 10, 12, 15, 20 y 30 — esas fracciones son **exactas**.

## Reglas de Oro de la Aritmética

Ver `constraints/YATRA_SPEC.md` y `AGENTS.md`. Resumen operativo:

1. **`SCALE_0 = 60⁴ = 12,960,000`** (NO 60⁶). `SPA::from_int(n)` ≠ `SPA::from_raw(n)`.
2. **Nunca doble-escalar**: `inject()`/`transduce_pulse()` esperan enteros-unidad y re-escalan internamente; pasarles un valor ya en raw (p.ej. `to_raw()` o `entropy_s60_raw` del kernel) corrompe el dato ×12,960,000. Para valores raw usar **`inject_spa(x, SPA::from_raw(v))`**.
3. **El lattice es disipativo**: `step()` solo disipa; el drive continuo (`sentinel-cortex/src/main.rs`, bloque 3b cada 500ms) mantiene la resonancia.
4. Reforzado por clippy: `float_arithmetic`, `float_cmp`, `cast_possible_truncation`, `cast_precision_loss` = **forbid** en los crates numéricos; e interceptado en kernel por `float_detector.c`.

## Resultados Medidos

| Métrica | Valor | Fuente |
|---|---|---|
| Memoria por nodo (EXP-015) | 16 B vs ~377 B Python (**23.6×**) | `me-60os-core/src/bin/fpu_vs_pai_bench.rs` |
| Throughput | ~120M nodos/s (**~3000×**) | ídem |
| Desviación PAI vs raw | 0.000 ppm | `bench_desvio_pai.rs` |
| Tests core | 89/89 (incl. familia anti-doble-escala 4/4) | `cargo test -p me60os --lib` |
| Recuperación memoria cristal P0.1 | 'Yo Soy' al 100% (doble malla convergida) | `bin/resonant_lattice_memory.rs` |

*Auditoría física↔código↔papers completa (2026-08-23): `personalvault/Sistemas/Auditoria_Fisica_Sentinel_2026-08-23.md`.*

## Quick Start

```bash
# Compilar todo el workspace
cargo build --release

# Suite de tests del núcleo numérico
cargo test -p me60os --lib

# Servidor principal (Axum :8000, drive continuo 500ms, ingesta eBPF)
cargo run -p sentinel-cortex --bin sentinel-cortex

# Experimentos destacados
cargo run -p me60os --bin resonant_lattice_memory   # memoria doble malla + SHM
cargo run -p me60os --bin exp028_penta              # portales emergentes (68s)

# Benchmarks
cargo run --release -p me60os --bin fpu_vs_pai_bench
cargo run --release -p me60os --bin bench_desvio_pai
```

Requisitos eBPF (kernel hooks): Linux ≥ 5.x con BTF, root o CAP_BPF+CAP_PERFMON. Ver `ebpf/` y sus loaders.

## Estado y Pendientes Conocidos

- ✅ Migración Py→Rust completa; TUI nativa en Rust; fix doble-escala ingesta eBPF (`bc3944ee`).
- 🔴 Abiertos (decisión de diseño pendiente): convención de `entropy_pressure` en loop térmico (P0.5), modo superconductor en ruta viva (P1.6), acoplamiento real del bombeo QHC (P1.7), wrap de fase módulo 360° (P1.8).
- Detalles: `Pendientes.md` del vault de investigación (`~/Proyectos/personalvault`).

## Licencia

Apache 2.0 — ver [LICENSE](./LICENSE).
