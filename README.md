# 🛡️ Sentinel — Sexagesimal Systems Framework

**A low-level systems framework built on sexagesimal (base-60) arithmetic and eBPF, designed for high-precision computation without floating-point errors.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?logo=rust)](./core/)
[![eBPF](https://img.shields.io/badge/eBPF-kernel--level-orange)](./ebpf/)

---

## 🎯 What is Sentinel?

Sentinel is an experimental systems framework that replaces standard binary/decimal arithmetic with **pure sexagesimal (base-60) computation**. The goal is to eliminate floating-point rounding errors at the mathematical foundation level — not through software patches, but through a fundamentally different numeric representation.

The system runs **offline-first**, with no cloud dependencies.

---

## ⚙️ Core Components

### `core/` — Rust Core Engine
- Cache-line aligned memory structures (64-byte alignment)
- Native `S60` and `U60` types: integers and fixed-point numbers in base-60
- Zero-copy IPC via `/dev/shm` (shared memory, no serialization overhead)

### `ebpf/` — Kernel-Level Translation Layer
- eBPF programs running at Ring 0 for real-time base-60 ↔ binary transcoding
- Low-latency data path between userspace agents and kernel

### `quantum/` — Sexagesimal Math Library (Python)
- `sovereign_math.py` — Core `S60` type: pure sexagesimal arithmetic
- `s60_pid.py` — PID controllers using S60 (no float drift)
- `complex_s60.py` — Complex numbers in base-60
- `qaoa_s60.py` — Quantum Approximate Optimization Algorithm (QAOA) in S60
- `vqe_s60.py` — Variational Quantum Eigensolver in S60
- `quantum_noise_s60.py` — Quantum noise modeling without floating point

### `agents/` — Modular Agent System
Autonomous agents that operate over the sexagesimal framework:
- **Research Agent** — document analysis and knowledge extraction
- **Verifier Agent** — hallucination detection and fact-checking
- **Publisher Agent** — content generation pipeline
- **Memory Agent** — vector-based memory with embeddings

### `observability/` — System Monitoring
- Prometheus metrics + Grafana dashboards
- Real-time entropy visualization (8×8 grid)
- Latency benchmarks demonstrating sub-100µs eBPF paths

---

## 🧮 Why Sexagesimal?

Base-60 arithmetic has properties that make it mathematically attractive for exact computation:

- **Divisibility**: 60 is divisible by 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 — far more than binary
- **No floating-point drift**: Fractions like 1/3 and 1/6 are exact in base-60
- **Precision-critical domains**: Useful for time, angular measurements, signal processing, and control systems

```python
from quantum.sovereign_math import S60

# Exact arithmetic — no rounding errors
result = S60(59) + S60(1)    # = S60(1, 0) — exact carry in base-60
phase  = S60(0, 30)          # = 0.5 in decimal — exactly representable
```

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/jenovoa/sentinel.git
cd sentinel

# Install Python dependencies
pip install -r requirements.txt

# Run the core validation suite
python3 master_truth_validation.py

# Start the observability stack (optional)
docker compose -f docker-compose.yml up -d
```

### Rust Core

```bash
cd core
cargo build --release
cargo test
```

---

## 📁 Directory Structure

```
sentinel/
├── core/              # Rust core engine (S60 types, memory structures)
├── ebpf/              # eBPF programs for kernel-level translation
├── quantum/           # Python sexagesimal math library
├── agents/            # Modular autonomous agent system
├── backend/           # API layer
├── frontend/          # Dashboard UI
├── observability/     # Prometheus + Grafana monitoring
├── docker/            # Container configurations
├── tests/             # Integration and unit tests
└── docs/              # Architecture documentation
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| eBPF bridge latency | < 100µs |
| IPC throughput (zero-copy) | ~6x vs serialized |
| Floating-point errors | **0** (exact arithmetic) |

---

## 🤝 Contributing

1. Fork the repository
2. Ensure code compiles without warnings: `cargo clippy -- -D warnings`
3. Run tests: `cargo test` and `python -m pytest tests/`
4. Open a Pull Request against `main`

CI runs on every PR via GitHub Actions (`rust-ci.yml` + `tests.yml`).

---

## 🎓 External Feedback

> *"Your direction of research sounds promising."*  
> — Dr. Daniel Mansfield, UNSW Sydney  
> *(Mathematician who decoded [Plimpton 322](https://en.wikipedia.org/wiki/Plimpton_322), December 2025)*

---

## 📄 License

MIT — see [LICENSE](./LICENSE)

---

## 🔗 Related Projects

- [ME-60OS](https://gitlab.com/jenovoa) — Debian-based OS built on sexagesimal logic
