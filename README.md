# Sentinel — Sexagesimal Systems Framework

**Low-level systems framework implementing base-60 arithmetic at the kernel level, eliminating IEEE 754 rounding errors from the mathematical foundation.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?logo=rust)](./services/neural-guard/)
[![eBPF](https://img.shields.io/badge/eBPF-kernel--level-orange)](./ebpf/)
[![Fenix Status](https://img.shields.io/badge/Fenix_Node-ACTIVE-brightgreen?style=for-the-badge&logo=linux)](https://pinguinoseguro.cl)

> [!NOTE]
> **Nodo Fenix Operativo**: Sentinel ha transicionado a una arquitectura de **Nodo Único (Fenix)** bajo Podman Rootless, consolidando la orquestación Ring 0 y el monitoreo resiliente.

---

## The Problem

IEEE 754 floating-point is broken for a specific class of fractions.
In binary: `1/3`, `1/6`, `1/12`, `1/60` are all non-terminating — they accumulate drift across computation chains.

Base-60 (sexagesimal) is divisible by 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30.
These fractions are **exact**. Babylonian astronomers used this for 2,000 years of positional calculation without error accumulation.
**Plimpton 322** (1800 BCE), decoded by Dr. Daniel Mansfield (UNSW, 2021), proves exact sexagesimal computation
was understood and applied 4,000 years ago.

Sentinel asks: can this foundation be implemented in modern systems software?

---

## Benchmark Results

### Memory Efficiency (EXP-015)

| Implementation | Memory per node | Throughput | Capacity in 11 GB RAM |
|---|---|---|---|
| Python sparse lattice | ~377 bytes | ~0.04M nodes/s | ~0.4 GB payload |
| **Rust S60 native** | **16.00 bytes** | **~120M nodes/s** | **~10 GB payload** |
| **Factor** | **23.6x smaller** | **~3,000x faster** | **25x more** |

The 23.6x memory reduction is structural: Python object overhead (dict + refcounting + GC) accounts
for ~361 of the 377 bytes. Rust `#[repr(packed)]` eliminates all of it — 16 bytes is purely S60 payload.

### Numerical Equivalence (EXP-021/022)

S60 arithmetic vs f64 — 1,000 signals x 300 samples, entropy source: `/dev/urandom`

| Metric | Lyapunov Exponent | Shannon Entropy |
|---|---|---|
| Mean divergence (S60 vs f64) | **< 0.0001** | **< 0.0001** |
| Signals within Delta < 0.1 threshold | **100%** | **100%** |
| Failed signals | **0** | **0** |

S60 is numerically equivalent to f64 for signal processing while eliminating float representation.

---

## Architecture

```
sentinel/
├── services/
│   └── neural-guard/  Rust Cortex — 🛡️ Decision Engine, Prometheus/Loki/Redis
├── sentinel-cortex/   Rust core — S60/U60 types, Ring 0 enforcement
├── ebpf/              LSM hooks — syscall interception, float blocking
├── quantum/           Python layer via PyO3 (me60os_core.so, zero-copy)
├── agents/            Modular agents: Research, Verifier, N8N Integration
├── observability/     Prometheus + Grafana (thermal-aware metrics)
└── constraints/       YATRA_SPEC.md — the immutable arithmetic contract
```

### 🧠 Neural Guard & Octomechanical Coupling

Sentinel represents a leap in defensive systems by integrating **Octomechanical Coupling**:
- **Thermal Awareness**: Neural Guard queries CPU temperature in real-time.
- **Dynamic Thresholding**: Thresholds for security alerts (SSH, Redis, Nginx) scale based on the **Computational Mass** (`Effective Load`) of the system.
- **Resilience**: Hotter environments (high noise/entropy) automatically increase detection tolerance to prevent false positives, while cool, coherent states enable maximum sensitivity.

---

### Core Type

```rust
// S60: 5-component fixed-point, 16 bytes packed, no floats
#[repr(packed)]
pub struct S60 {
    degrees: i16,
    minutes: u8,
    seconds: u8,
    centiseconds: u8,
    milliseconds: u8,
    // padding: 10 bytes
}
```

Zero allocation on the heap. Cache-line friendly. Deterministic layout across architectures.

---

## Quick Start

```bash
# Build Rust core
cd sentinel-cortex && cargo build --release

# Build PyO3 extension (requires me-60os repo)
cd ../me-60os && cargo build --release --features extension-module
cp target/release/libme60os_core.so ../sentinel/quantum/

# Run memory benchmark
cd sentinel/quantum && python3 experiments/EXP_015_MEMORY_THROUGHPUT.py

# Run numerical equivalence validation
python3 experiments/EXP_022_ENTROPY_VALIDATION.py
```

---

## The YATRA Lock

**No `f32` or `f64` in base-60 logic — ever.**

The eBPF layer enforces this at the kernel level: LSM hooks detect float-contaminated syscall patterns
and can block them at runtime. This is not a style guide — it is a correctness invariant.

---

## Roadmap

- [x] **Fenix Sovereignty**: Transition to single-node Podman Rootless orchestrator.
- [x] **Neural Guard (Rust)**: Deployment of the new memory-safe Decision Engine.
- [x] **Octomechanical Coupling**: Real-time CPU thermal awareness for dynamic sensitivity.
- [x] Ring 0: eBPF LSM hooks, float contamination detection.
- [x] Rust S60/U60 core types with zero-copy IPC via `/dev/shm`.
- [x] PyO3 bridge — Python access with no serialization overhead.
- [x] Prometheus + Grafana observability stack.
- [ ] MycNet: distributed S60 computation across mesh nodes.
- [ ] Formal equivalence proof — S60 as equivalence class relative to IEEE 754.

---

## Research

See [RESEARCH.md](./RESEARCH.md) for the full experimental program narrative,
methodology, benchmark numbers, honest limitations, and open problems.

---

## License

Apache 2.0 — see [LICENSE](./LICENSE)

---

## Related

- [ME-60OS](https://gitlab.com/jenovoa) — Rust/PyO3 core library (me60os_core.so)
