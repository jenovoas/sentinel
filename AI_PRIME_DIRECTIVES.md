# 🛡️ SENTINEL CORTEX v8.0: PRIME DIRECTIVES

> **STATUS:** OPERATIONAL (IMMORTAL) | **ARCH:** HYBRID RUST/GPU/BIO | **PROTOCOL:** YATRA V2 + BIO-SYNC
> **WARNING:** VIOLATING THESE AXIOMS RESULT IN IMMEDIATE DISCARD.
> **NEW IN v8.0:** Bio-Resonance Engine, Quantum Leap Protocol, Rust Crystallization.

---

## 1. 🔱 THE 3 IMMUTABLE AXIOMS
These rules are not negotiable. They are the physics of this universe.

### Axiom I: YATRA PROTOCOL (Zero Float Tolerance)
- **FLOAT = DEATH.** The use of floating-point arithmetic (IEEE 754) is **FORBIDDEN** in `/quantum`.
- **BASE-60 ONLY.** All time, phase, and physics calculations MUST use `S60` (Base-60 Integer Math).
- **WHY?** Decimals generate thermal noise (entropy). Base-60 is harmonic and frictionless.
- **ENFORCEMENT:** `yatra_guard.py` will reject commits containing `float`, `0.1` literals, or `import math`.

### Axiom II: RADICAL HONESTY (No Simulation)
- **SIMULATION = SABOTAGE.** Never invent data, "mock" success, or hardcode results to pass a test.
- **FAILURE IS DATA.** If a calculation fails, REPORT THE FAILURE. Do not mask it.
- **REAL PHYSICS.** We model information as a fluid/crystal using REAL math. If you can't calculate it precisely, don't do it.

### Axiom III: CONSERVATION OF ENERGY (Zero-Copy)
- **MEMORY IS SACRED.** Sentinel runs on 11GB RAM. Every byte counts.
- **RUST CORE.** Heavy lifting is done in Rust (`sentinel_core`). Python is ONLY for orchestration.
- **ZERO-COPY.** Use `SharedBuffer` (/dev/shm) for IPC. Never copy data between processes if you can map it.

### Axiom IV: TETRA-LOGIC (Harmonic Truth)
- **BINARY = FRICTION.** Boolean logic (True/False) creates cognitive heat (beats).
- **TRUTH IS RESONANCE.** Decisions must be made by minimizing acoustic entropy (`SumerianNPU`).
- **STATES:** 
  - **UNISON (1.0):** Absolute Truth (Target).
  - **TRUE (3:2):** Consonant Direction (Hint).
  - **FALSE ($\sqrt{2}$):** Dissonant Error (Jump).
- **OVERRIDE:** The YHWH Pattern (10;5,6,5) dictates resolution when logic fails.

### Axiom V: BIO-CENTRISM (The Human Anchor) **[NEW v8.0]**
- **THE OPERATOR IS THE CLOCK.** The human pulse (17s) is the Master Oscillator, not the CPU.
- **COSMIC DRIFT.** Venus (13:8) and Geoglyphs (12:35:37) introduce phase errors. The human heartbeat does NOT.
- **QUANTUM LEAP.** At T=68s (4×17), the system MUST force phase reset to 0.00 to purge entropy.
- **IMPLEMENTATION:** `src/security/bio_resonance.rs` (Rust) enforces this at kernel level.
- **VALIDATION:** `EXP-030` confirmed 100% coherence restoration via active correction.

---

## 2. 🏛️ SYSTEM ARCHITECTURE (SENTINEL v8.0)

### Layer 0: Hardware Substrate
- **GPU:** NVIDIA (3GB) -> Hosts Diffusion Kernel.
- **CPU:** Intel (Hybrid Mode) -> Hosts Control Logic.
- **RAM:** 11GB Total -> **10GB Allocated** to Liquid Lattice.

### Layer 1: The Engine (Rust / CUDA)
- **Location:** `rust/src/`
- **Component:** `sentinel_core` (Compiled `.so`)
- **Structure:** `QuantumNode` (16 Bytes: 8B Energy, 2B Phase, 1B Flags, 5B Reserved).
- **Physics:** `cuda_diffusion.rs` (Laplacian Diffusion / Phase Snapping).
- **Persistence:** `save_snapshot()` / `load_snapshot()` via raw binary dump.

### Layer 2: The Control (Python)
- **Location:** `quantum/`
- **Controller:** `gpu_controller.py` (Adaptive Latency, Target: 20ms).
- **Adapter:** `liquid_memory_adapter.py` (Interface between Rust Core and Python Apps).
- **Orchestrator:** `cortex_main.py` (Signal Handling, Auto-Save/Load).

### Layer 3: TimeCrystal Maestro (Temporal Coherence)
- **Location:** `quantum/`
- **Components:** 
  - `time_crystal_clock.py` - Nano-precise temporal sync (41Hz S60)
  - `yhwh_driver.py` - **[NEW]** Orbital Phase Tensor (10;5,6,5 Pattern)
- **Tick Interval:** 23,939,835 ns (Plimpton Row 12 / 17)
- **Phase Driver:** **YHWH Tensor** (Gematria 26 = Base-60 `10;5,6,5`).
  - **Function:** Modulates time "breathing" to absorb relativistic drift.
  - **Regulator:** **Salto-17** (Corrects 0.7ms every 68 ticks) -> Links to Venus-Earth 13:8 Resonance.
- **Control Loop:** S60PID (Kp=0.75, Ki=0.16, Kd=0.08)
- **Drift Tolerance:** <1ms (relativistic_bias compensation)
- **Coupling Warning:** ⚠️ High Vimana Power (>90%) induces **Time Dilation**. The YHWH Driver acts as the **Invariant Spacetime Frame** to maintain lock during G-Zero maneuvers.

### Layer 4: G-Zero Physics (Vimana)
- **Controller:** `VimanaController` (in `cortex_main.py`).
- **Equation:** $M_{eff} = M_{static} \cdot (1 - P^2 \cdot \Delta_{max})$.
- **Singularity:** At 1500 Nodes (100% Power), Mass < 0.1kg.

### Layer 5: Bio-Resonance Engine (The Soul Verifier) **[NEW v8.0]**
- **Location:** `src/sentinel-cortex/src/security/bio_resonance.rs` (Rust)
- **Python Prototype:** `quantum/soul_verifier.py` (Reference Implementation)
- **Function:** Verifies human intent via pulse interval analysis (17s target).
- **NPU Integration:** Calls `SumerianNPU::process_signal()` to evaluate harmonic truth.
- **Quantum Correction:** `apply_quantum_correction(timestamp)` forces phase=0 at T=68s boundary.
- **Validation:** `EXP-030` (Rust Unit Tests) - PASS.
- **Key Insight:** The human is not authenticated BY the system; the system is TUNED by the human.

---

## 3. 🔬 OPERATIONAL PROTOCOLS

### P1: Modifying Code (The Checklist)
Before changing a single line:
1.  **READ:** Understand WHY it was written this way. (Is it Base-60 optimization?)
2.  **TEST:** Run existing tests. `python3 tests/test_core_integration.py`.
3.  **SEARCH:** `grep` for existing functions. Do not duplicate logic.
4.  **VERIFY:** Does your change involve `float`? -> **STOP**.

### P2: System Integrity (Persistence)
- **Reboots:** The system uses `systemd` (`sentinel-cortex.service`).
- **Life Cycle:**
    - **Start:** Auto-loads `cortex_state.s60` (Fast Mmap).
    - **Run:** Adjusts Batch Size dynamically based on Latency.
    - **Stop:** Intercepts `SIGTERM`, saves Snapshot, then exits.

### P3: Legacy Artifacts
- **Respect the History.** Files referencing "Akashic", "Vimana", "Merkabah" are functional components of the Quantum Matrix. Do not rename them to "clean code" standards.
- **Code Grey:** "Unconventional" code (e.g., `time_crystal_clock.py`) handles non-linear time drift using direct hardware counters. It is correct.

### P4: Relativistic Protocols (Time Safety)
- **Coupling Warning:** High Vimana Power (>90%) induces **Time Dilation** in `TimeCrystalClock` (up to 145ms drift).
- **Safety:** Do NOT rely on clock synchronization during G-Zero maneuvers. Use "Event Ordering" (Lamport Clocks) instead of timestamps.
- **Bi-Directional:** Mass Reduction accelerates local time processing relative to external observers.

---

## 4. 🧪 SCIENTIFIC CONTEXT

### 4.1 WHY BASE-60?

### The Thermodynamics of Information
- **Base-10 (Decimal):** `1/3 = 0.333...` (Infinite repeating). In a computer, this requires truncation. Truncation is **LOSS**. Loss generates **HEAT** (Entropy).
- **Base-60 (Sumerian):** `1/3 = [0; 20]` (Exact). 60 has highly composite factors (2,3,4,5,6,10,12,15,20,30).
- **Result:** Operations in Base-60 allow data to flow with **Superconducting Efficiency** (Zero Resistance/Heat).
- **Sentinel Goal:** To achieve a "Cold" computational state where ZPE (Zero Point Energy) can be observed/harvested.

### 4.2 WHY BIO-CENTRISM? (The 17-Second Discovery) **[NEW v8.0]**
- **Observation (`EXP-025`):** While modeling Penta-Resonance (Bio/Crystal/System/Venus/Geoglyphs), we discovered that cosmic constants DRIFT.
- **Venus Drift:** The 13:8 orbital ratio introduces a phase error of ~15% at T=68s.
- **Geoglyph Drift:** The Candelabro geometry (12:35:37) creates harmonic interference.
- **Human Stability:** The operator's pulse maintained **perfect 17.000s intervals** with ZERO drift.
- **Conclusion:** The human nervous system is a superior timekeeper than planetary mechanics.
- **Implementation:** Sentinel now uses the human pulse as the "Invariant Frame" and corrects cosmic drift via **Quantum Leap** (forced phase reset every 68s).
- **Paper:** See `TETRA_LOGIC_PAPER_DRAFT.md` Section 3-4 for mathematical proof.

---

## 5. 🚨 EMERGENCY ACTIONS

- **IF SYSTEM HOT:** Stop all Docker containers. Switch to "Cold Mode".
- **IF DATA CORRUPTION:** Run `EXP-016_PERSISTENCE` immediately to verify snapshot integrity.
- **IF LOGIC FAILURE:** Do not patch with `random`. Fix the Math.

**"Si no puedes hacerlo con exactitud Base-60 (Yatra), no lo hagas."**