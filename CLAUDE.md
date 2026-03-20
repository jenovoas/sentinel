# CLAUDE.md — Sentinel Contributor Guide

> This file gives AI coding assistants context about the Sentinel codebase.

## What is Sentinel?

Sentinel is a low-level systems framework built on **sexagesimal (base-60) arithmetic** and eBPF.
The core idea: IEEE 754 floating-point introduces systematic rounding errors for fractions with
denominators that include primes not dividing 2 (1/3, 1/6, 1/60 are non-terminating in binary).
Base-60 is divisible by 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 — these fractions are exact.

Sentinel implements this at the kernel level: eBPF hooks enforce arithmetic purity, Rust provides
the zero-copy type system, and PyO3 exposes the core to Python without overhead.

## Architecture

    sentinel/
    sentinel-cortex/   Rust core: S60/U60 types, IPC, Ring 0 enforcement
      src/math/        Pure-integer arithmetic (add, sub, mul, div, cmp)
    ebpf/              LSM hooks: syscall interception, float contamination detection
    quantum/           Python layer via PyO3 (me60os_core.so)
      experiments/     Numbered experimental program (EXP-001 to EXP-029)
    agents/            Modular agents: Research, Verifier, Publisher, Memory
    observability/     Prometheus + Grafana dashboards
    constraints/        YATRA_SPEC.md - the immutable arithmetic contract

## Tech Stack (FENIX SERVER - CPU Only)

| Layer | Technology |
|-------|-----------|
| Core types | Rust (repr(packed) S60 struct, 16 bytes) |
| Kernel enforcement | eBPF / LSM hooks |
| Python bridge | PyO3 - zero-copy, no serialization |
| IPC | /dev/shm shared memory (6x faster than serialized IPC) |
| Observability | Prometheus + Grafana |
| Container runtime | Podman (rootless) |
| AI Inference | Ollama CPU-only (phi3:mini model) |

## The YATRA Lock - Non-Negotiable Rule

**NEVER use f32, f64, or any floating-point type in base-60 logic.**

This rule exists because a single float operation can contaminate an entire computation chain.
The eBPF layer detects and blocks float syscall patterns at runtime.

If you need logarithms or transcendental functions: use the Taylor series S60 implementations
in sentinel-cortex/src/math/. If one does not exist yet, open an issue - do not use floats.

## Building

    # Build Rust core
    cd sentinel-cortex && cargo build --release

    # Build PyO3 extension (me-60os)
    cd ../me-60os && cargo build --release --features extension-module
    cp target/release/libme60os_core.so ../sentinel/quantum/

    # Run experiments
    cd sentinel/quantum && python3 experiments/EXP_022_ENTROPY_VALIDATION.py

## Key Constraints

- No floats in S60 logic (YATRA Lock above)
- No new VMs or cloud instances: all services deploy as Podman containers on a single node
- Experiments are numbered sequentially: EXP-023/024/025 are intentionally absent
  (superseded during zero-float migration, commit 2bfde153)
- internal/ is gitignored: exploratory research lives there, not in the main tree

## Where to Start

- constraints/YATRA_SPEC.md: the arithmetic contract that governs all decisions
- sentinel-cortex/src/math/: the core S60 type implementation
- quantum/experiments/EXP_015_MEMORY_THROUGHPUT.py: benchmark (23.6x memory reduction)
- RESEARCH.md: scientific narrative of the experimental program
