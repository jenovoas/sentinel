# Research: Sexagesimal Arithmetic as a Systems Foundation

**Status:** Active experimental program | **Experiments:** EXP-001 through EXP-029

---

## Motivation

Floating-point arithmetic (IEEE 754) introduces systematic rounding errors in fractions
whose denominators include factors of 3, 7, or any prime not dividing the base (2 or 10).
In binary: 1/3, 1/6, 1/12, 1/60 are all non-terminating — they accumulate drift.

Base-60 (sexagesimal) is divisible by 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 — far more
than binary or decimal. Fractions critical to time, angular measurement, signal processing,
and control systems are **exact** in base-60. This is why Babylonian astronomers used it
for 2,000 years of positional calculation without error accumulation.

**Plimpton 322** (1800 BCE), decoded by Dr. Daniel Mansfield (UNSW, 2021), demonstrates
that exact sexagesimal computation was understood and applied 4,000 years ago.
Sentinel asks: can this foundation be implemented in modern systems software?

---

## S60 Type

The core type is a 5-component fixed-point integer:

    S60(degrees, minutes, seconds, centiseconds, milliseconds)

Stored as a packed 16-byte Rust struct (`#[repr(packed)]`). No floats. No GC.
Arithmetic operations (add, sub, mul, div, comparison) are implemented in pure Rust
in `sentinel-cortex/src/math/`.

Python access via PyO3: `import me60os_core as s60` — zero-copy, no serialization overhead.

---

## Experimental Program

Experiments are numbered in order of conception. EXP-023/024/025 were superseded during
the zero-float migration (commit `2bfde153`) and are not present — this is intentional,
not a gap in the series.

### Memory and Throughput — EXP-015

**Hypothesis:** A packed Rust struct storing S60 nodes will use significantly less memory
and process significantly faster than an equivalent Python sparse lattice implementation.

**Method:** Inject 1,000,000 nodes via Rust (`RustLattice.inject()`) and 10,000 nodes
via Python (`LiquidLatticeStorage`). Measure memory via `active_memory_usage()` and wall time.

**Results:**

| Metric | Python (Sparse) | Rust (Native) | Factor |
|---|---|---|---|
| Memory per node | ~377 bytes | **16.00 bytes** | **23.6x** |
| Throughput | ~0.04M nodes/s | **~120M nodes/s** | **~3,000x** |
| Capacity in 11GB RAM | ~0.4 GB payload | **~10 GB payload** | **25x** |

**Explanation:** Python object overhead (dict + refcounting + GC) accounts for ~361 bytes
of the 377-byte figure. Rust `#[repr(packed)]` eliminates all of this — 16 bytes is
purely S60 payload. The 3,000x throughput delta reflects both allocator overhead elimination
and cache-line alignment.

---

### Numerical Equivalence — EXP-021 and EXP-022

**Hypothesis:** S60 arithmetic produces numerically equivalent results to f64 for
signal processing algorithms, within an acceptable divergence threshold (Delta < 0.1).

**Method:** Generate rPPG cardiac signals using real entropy (`/dev/urandom`).
Calculate Lyapunov exponent and Shannon entropy using both S60 and f64 implementations.
Measure divergence per signal. EXP-021: single signal validation. EXP-022: 1,000 signals,
full statistical analysis (mean, std, percentiles, edge case detection).

**Signal parameters:**
- 1,000 signals x 300 samples each
- Entropy source: `/dev/urandom` (hardware entropy)
- BPM range: [60, 100] — physiological human range

**Results:**

| Metric | Lyapunov Exponent | Shannon Entropy |
|---|---|---|
| Mean divergence (S60 vs f64) | **< 0.0001** | **< 0.0001** |
| Std deviation | **< 0.005** | **< 0.005** |
| Signals within Delta < 0.1 threshold | **100%** | **100%** |
| Failed signals | **0** | **0** |

**Honest limitation:** The current S60 implementation bridges to `math.log()` (float)
for the natural logarithm in Lyapunov and entropy calculations. A pure S60 `ln()` via
Taylor series is in development. The near-zero divergence demonstrates that S60 arithmetic
containers are numerically equivalent to f64 even with this bridge — the full Taylor
series implementation will close the remaining float dependency.

---

### Kernel Integration

**eBPF / Ring 0:** LSM hooks intercept syscalls at < 100us latency. The YATRA Protocol
runs as an eBPF program that can block float-contaminated operations at the kernel level.

**Zero-copy IPC:** `/dev/shm` shared memory between agents and kernel. 6x throughput
vs serialized IPC (measured across sentinel-cortex buffer system benchmarks).

---

## Open Problems

1. **Pure S60 `ln()`** — Taylor series implementation to close the float bridge in EXP-021/022
2. **MycNet** — Distributed S60 computation across 6+ mesh nodes (batman-adv layer);
   hardware acquisition pending
3. **Formal equivalence proof** — Mathematical proof of S60 as an equivalence class
   relative to IEEE 754 for the precision domains tested

---

## References

- Mansfield, D. F. & Wildberger, N. J. (2017). *Plimpton 322 is Babylonian exact sexagesimal trigonometry.* Historia Mathematica. https://doi.org/10.1016/j.hm.2017.08.001
- YATRA Protocol specification: `constraints/YATRA_SPEC.md`
- Experimental source code: `quantum/experiments/`
