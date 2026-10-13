# Design Spec: Sentinel Repo Preparation for Funding Review
**Date:** 2026-03-18 | **Version:** 2.0 (post spec-review)
**Author:** Jaime Novoa / Claude Code | **Status:** Ready for implementation

---

## Context

Sentinel is a systems framework built on sexagesimal (base-60) arithmetic + eBPF + Rust.
Funding applications were submitted to Google, Perplexity, Azure, Amazon, and Anthropic.
The public GitHub repo (github.com/jenovoas/sentinel) is live and being reviewed now.

**Ask:** Research funding (papers, academic validation) + Infrastructure (MycNet hardware).

**Problem:** ~60 files in repo root/quantum/docs that are AI session artifacts, internal ops
docs, or speculative physics research — all of which undermine credibility for the legitimate
S60/eBPF/Rust benchmarks that ARE the funding case.

---

## Phase 1 — Clean Root (Complete list)

### AI session artifacts → internal/ + .gitignore
- SYSTEM_PROMPT
- GEMINI_TASK_*.md (5 files)
- GEMINI_REPORT.md, GEMINI_TASK.md, GEMINI_TASK_MONITORING.md
- QWEN_RESULT.md, QWEN_SESSION_RESULT.md
- OPENCODE_TASK_SENTINEL_REPAIR.md
- CONTEXTO_REINICIO.md
- ANTIGRAVITY.md, OPENCODE.md, QWEN.md, GEMINI.md
- AI_PRIME_DIRECTIVES.md
- INTERCEPTOR_RESULT.md, CHECKLIST.md
- PROMPT_GLOBAL_AGENTES.md
- Analiza_mi_visión_del_sistema_research.md

### Internal ops docs → internal/
- FENIX_DEPLOY_PLAN.md
- SERVICIOS_ACTIVOS.md
- DASHBOARD-MIGRATION.md, DASHBOARD_MAINTENANCE.md, Dashboard.md
- COGNITIVE_DESIGN.md
- docker-compose.fenix.yml.bak
- cortex_state.s60

### IDE/framework state → .gitignore (untrack from git)
- .claude/settings.json
- .sisyphus/ (entire directory)
- .soma/ (entire directory — keep SOMA architecture docs only)

### CLAUDE.md → rewrite as contributor guide
Current version exposes: internal server paths, personal name, outdated FastAPI stack.
New version: brief contributor orientation (how to build, test, contribute).

---

## Phase 2 — Speculative research → internal/exploratory/

These files coexist in quantum/ alongside the legitimate S60 benchmarks and will cause
a technical reviewer from Google/Anthropic to lose confidence in EXP-015/021/022:

### quantum/ files to move
- vimana_drone_sim.py, vimana_mission_sim.py, vimana_orbital_ascent_sim.py
- vimana_shield_validation.py, vimana_yatra_driver.py
- zpe_phase1_lab.py, zpe_simulation.py, zpe_power_circuit_sim.py
- consciousness_experiment.py, reality_interrogation.py, beyond_the_rift.py
- capture_mother_signature.py, foreign_energy_detector.py
- EXP_005_MERKABAH_G_ZERO.md/.py
- EXP_006_SUPERCONDUCTOR_TEST.md/.py (review: if content is S60 math → keep)
- EXP_017_VIMANA_LEVITATION.md/.py
- EXP_019_S60_SOUL_VALIDATION.py
- EXP_027_YHWH_PULSE_MONITOR.md/.py
- EXP_028_PENTA_RESONANCE.md/.py

### docs/ files to move
- docs/PLANETARY_ENERGY_SHIELD.md
- docs/quantum/VIMANA_*.md (all)
- docs/quantum/ZPE_*.md (all)
- docs/quantum/MHD_SHIELD_TECHNICAL_WHITE_PAPER.md

### tests/ files to move
- tests/test_levitation.py

Note: None of this is deleted. Lives in internal/exploratory/ — in git, accessible,
just not the first thing a reviewer sees.

---

## Phase 3 — New README.md (~300 lines)

Technical tone. No marketing. Leads with numbers.

```
# Sentinel — Sexagesimal Systems Framework
[1-line tagline + badges: Rust, eBPF, MIT, Python]

## The Problem
Why IEEE 754 fails in precision-critical domains.
Concrete: 1/3 = 0.333... (float) vs exact in S60. Drift in control loops.

## The Approach
Base-60 arithmetic at the systems level: not a library, a foundation.
Each layer: Ring 0 (eBPF/LSM) → Rust Core (S60/U60) → PyO3 bridge → Agents

## Architecture
ASCII diagram — Ring 0 → Rust backend (sentinel-cortex) → Agents

## Benchmarks
Real numbers from EXP-015, EXP-021, EXP-022:
| Metric | Python | Rust | Factor |
| Memory/node | 377 B | 16 B | 23.6x |
| Throughput | 0.04M/s | 120M/s | 3000x |
| Float errors | n/a | 0 | by design |
| S60 vs f64 divergence (1000 signals) | — | Δ<0.0001 | — |

## Research → link to RESEARCH.md

## Academic Validation
Dr. Mansfield quote (repositioned from footer to body)

## Quick Start (3 commands)

## Roadmap
Phase 1 ✅ (Ring 0 complete). Phase 2: MycNet + publications.

## Contributing / License (MIT)
```

---

## Phase 4 — RESEARCH.md

Scientific narrative of the experimental program:

```
# Research: Sexagesimal Arithmetic as a Systems Foundation

## Motivation
Float drift in control systems, signal processing, critical infrastructure.
Historical precedent: Plimpton 322 — Babylonian exact sexagesimal fractions (1800 BCE).

## Methodology
S60 type: 5-component fixed-point integer (degrees/min/sec/centisec/millisec).
Dual-path validation: S60 results vs f64 across 1000+ real-entropy signals.
Rust core compiled via PyO3 — zero-copy interop, no GC overhead.

## Key Results

### Memory & Throughput (EXP-015)
| Metric | Python | Rust | Improvement |
|--------|--------|------|-------------|
| Memory/node | 377 B | 16 B | 23.6x |
| Throughput | 0.04M nodes/s | 120M nodes/s | 3000x |
| IPC (zero-copy vs serialized) | baseline | 6x | — |

### Numerical Equivalence (EXP-021, EXP-022)
1000 rPPG signals, 300 samples each, /dev/urandom entropy source.
- Lyapunov exponent: mean Δ < 0.0001 vs f64, 100% within threshold
- Shannon entropy: mean Δ < 0.0001 vs f64, 100% within threshold

### Kernel Integration
- eBPF LSM hooks: <100μs latency
- YATRA Protocol: formal constraint system preventing float use in core

## Open Problems (honest)
- ln() via Taylor series in S60 (current: float bridge in EXP-021/022)
- MycNet: distributed S60 computation across mesh nodes (hardware pending)
- Formal proof of S60 equivalence class relative to IEEE 754

## Serie Experimental
EXP-023 (Detección de Deriva Temporal), EXP-024 (Correlación Bio‑Sistema) y
EXP-025 (Penta‑Resonancia) son parte del registro de investigación que llevó al
descubrimiento del ancla humana de 17 segundos. La numeración refleja orden de
concepción.

## References
- Mansfield, D. (UNSW): Plimpton 322 decoding, exact sexagesimal fractions
- YATRA Protocol: constraints/YATRA_SPEC.md
```

---

## Implementation Order

0. Snapshot: `git ls-files | wc -l` before and after Phase 1
1. Phase 1: git rm --cached + move to internal/ + update .gitignore (~60 min)
2. Phase 2: Move speculative files to internal/exploratory/ (~30 min)
3. Phase 3: Rewrite CLAUDE.md as contributor guide (~10 min)
4. Phase 4: Write new README.md (~45 min)
5. Phase 5: Write RESEARCH.md (~30 min)
6. Commit + push (~5 min)

Total: ~3 hours

---

## Success Criteria

- Zero AI session artifacts at repo root or quantum/
- Speculative research in internal/exploratory/ — not deleted, just not first-visible
- README answers: what, why, how, proof (numbers), what's next
- RESEARCH.md has real methodology + honest open problems
- A technical reviewer from Google/Anthropic understands the project value in 5 min
