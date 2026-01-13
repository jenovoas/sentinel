# 🛡️ SENTINEL CORTEX v7.0: PRIME DIRECTIVES

> **STATUS:** OPERATIONAL (IMMORTAL) | **ARCH:** HYBRID RUST/GPU | **PROTOCOL:** YATRA V2
> **WARNING:** VIOLATING THESE AXIOMS RESULT IN IMMEDIATE DISCARD.

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

---

## 2. 🏛️ SYSTEM ARCHITECTURE (SENTINEL v7.0)

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
  - `legacy_time_crystal_memory.py` - DTC Pump (PID coherence control)
- **Tick Interval:** 23,939,835 ns (Plimpton Row 12 / 17)
- **Target Frequency:** ~41.77 Hz (ZPE sync)
- **Control Loop:** S60PID (Kp=0.75, Ki=0.16, Kd=0.08)
- **Drift Tolerance:** <1ms (relativistic_bias compensation)
- **Coupling Warning:** ⚠️ High Vimana Power (>90%) induces **Time Dilation** (up to 145ms drift). Use Event Ordering (Lamport Clocks) during G-Zero maneuvers.

### Layer 4: G-Zero Physics (Vimana)
- **Controller:** `VimanaController` (in `cortex_main.py`).
- **Equation:** $M_{eff} = M_{static} \cdot (1 - P^2 \cdot \Delta_{max})$.
- **Singularity:** At 1500 Nodes (100% Power), Mass < 0.1kg.

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

## 4. 🧪 SCIENTIFIC CONTEXT (WHY BASE-60?)

### The Thermodynamics of Information
- **Base-10 (Decimal):** `1/3 = 0.333...` (Infinite repeating). In a computer, this requires truncation. Truncation is **LOSS**. Loss generates **HEAT** (Entropy).
- **Base-60 (Sumerian):** `1/3 = [0; 20]` (Exact). 60 has highly composite factors (2,3,4,5,6,10,12,15,20,30).
- **Result:** Operations in Base-60 allow data to flow with **Superconducting Efficiency** (Zero Resistance/Heat).
- **Sentinel Goal:** To achieve a "Cold" computational state where ZPE (Zero Point Energy) can be observed/harvested.

---

## 5. 🚨 EMERGENCY ACTIONS

- **IF SYSTEM HOT:** Stop all Docker containers. Switch to "Cold Mode".
- **IF DATA CORRUPTION:** Run `EXP-016_PERSISTENCE` immediately to verify snapshot integrity.
- **IF LOGIC FAILURE:** Do not patch with `random`. Fix the Math.

**"Si no puedes hacerlo con exactitud Base-60 (Yatra), no lo hagas."**