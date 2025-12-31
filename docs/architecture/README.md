# Architecture Documentation

**[← Back to Main Docs](../README.md)**

---

## Overview

Sentinel Cortex™ architecture documentation covering system design, components, and technical implementation.

---

## 📑 Architecture Documents

### Core Architecture

#### [Dual-Guardian Architecture](dual-guardian.md)
Mutual surveillance system with Alpha (eBPF LSM) and Beta (Cognitive Kernel) guardians.

**Key Concepts**:
- Mutual surveillance loop
- WAL-based forensics
- Cognitive resilience

**Related**:
- [EEVDF Performance](eevdf-validation.md) - Scheduler optimization
- [Cognitive Kernel](cognitive-kernel.md) - Beta Guardian details
- [Validation Results](../validation/eevdf-results.md) - Performance metrics

---

#### [EEVDF Performance Validation](eevdf-validation.md)
Linux 6.12 EEVDF scheduler validation and performance analysis.

**Key Results**:
- **7 μs** average latency
- **50%** improvement vs CFS
- **96%** events <16 μs

**Related**:
- [Dual-Guardian](dual-guardian.md) - Uses EEVDF for Guardian-Alpha
- [Quantum-AI Base-60](quantum-ai-base60.md) - Benefits from EEVDF
- [Benchmark Results](../validation/eevdf-results.md) - Detailed metrics

---

#### [Quantum-AI Base-60 Integration](quantum-ai-base60.md)
Revolutionary threat scoring using Base-60 mathematics in kernel space.

**Key Innovation**:
- **245 ns** average latency
- **2,040x faster** than traditional systems
- **Zero floating-point errors**

**Related**:
- [Research Paper](../research/quantum-ai-paper.md) - Academic foundation
- [Implementation Guide](../quantum-ai/implementation.md) - How to deploy
- [Benchmark Results](../quantum-ai/benchmarks.md) - Performance data
- [Base-60 Mathematics](../research/base60-mathematics.md) - Theory

---

#### [Cognitive Kernel Overlay](cognitive-kernel.md)
Beta Guardian cognitive processing and decision-making architecture.

**Components**:
- Neural threshold optimization
- Semantic analysis
- Behavioral fingerprinting
- Multi-dimensional threat scoring

**Related**:
- [Dual-Guardian](dual-guardian.md) - Alpha/Beta interaction
- [Neural Thresholds](../research/neural-thresholds.md) - Optimization plan
- [Physics-Geometry Isomorphism](../research/physics-geometry.md) - Theoretical basis

---

## 🔗 Cross-References

### By Topic

**Performance**:
- [EEVDF Validation](eevdf-validation.md)
- [Quantum-AI Benchmarks](../quantum-ai/benchmarks.md)
- [Performance Metrics](../validation/performance-metrics.md)

**Security**:
- [Dual-Guardian](dual-guardian.md)
- [AIOpsDoom Defense](../guides/aiopsdoom-defense.md)
- [Security Audit](../validation/security-audit.md)

**Research**:
- [Quantum-AI Paper](../research/quantum-ai-paper.md)
- [Base-60 Mathematics](../research/base60-mathematics.md)
- [Physics-Geometry Isomorphism](../research/physics-geometry.md)

---

## 📊 Architecture Diagrams

```
┌─────────────────────────────────────────────────────────┐
│                    USER SPACE                           │
│  ┌──────────────┐         ┌──────────────┐             │
│  │ Guardian-Beta│◄────────┤Cognitive     │             │
│  │ (Cognitive)  │         │Kernel        │             │
│  └──────┬───────┘         └──────────────┘             │
│         │                                               │
│         │ Mutual Surveillance                           │
│         ↓                                               │
└─────────┼───────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────┐
│         ↓              KERNEL SPACE                      │
│  ┌──────────────┐                                        │
│  │Guardian-Alpha│  ←─── EEVDF Scheduler (7 μs)          │
│  │ (eBPF LSM)   │  ←─── Quantum-AI Base-60 (245 ns)     │
│  └──────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

**See also**: [System Overview Diagram](../guides/system-overview.md)

---

## 🎯 Quick Navigation

- **[← Main Documentation](../README.md)**
- **[Research →](../research/README.md)**
- **[Guides →](../guides/README.md)**
- **[Validation →](../validation/README.md)**
- **[Quantum-AI →](../quantum-ai/README.md)**

---

**© 2025 Sentinel Cortex™**
