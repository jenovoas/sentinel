# 📊 Technical Feasibility & Impact Report: Sentinel Cortex Pivot

**Date**: December 20, 2025
**Objective**: Assess feasibility of adding a **BCI Research Track** ("Sentinel Cortex") alongside the main "Vault" platform.

## 1. Feasibility Assessment

### A. Core Engine (Rust)
- **Status**: **High Feasibility**.
- **Transformation**: Converting `sentinel-wasm` to `bci-engine` is straightforward.
    - *Dependency Swap*: Replace `wasm-bindgen`/`js-sys` with `tokio` (runtime) and `rubato` (DSP).
    - *Logic Reuse*: The anomaly detection logic (`calculate_anomaly_score`) in `lib.rs` is math-pure and 100% portable to native Rust.
- **Hardware Requirement**: Low. A standard CPU (4 cores) can handle >50k samples/sec ingestion (simulated).

### B. Orchestration (n8n)
- **Status**: **Medium Feasibility** (Integration Gap).
- **Gap**: `n8n` folders exist, but it is **not** in the root `docker-compose.yml`.
- **Action**: Must add `n8n` service to `docker-compose.yml` to enable the "Logical Brain" workflow.
- **Connectivity**: Localhost networking between Rust Engine (Host/Docker) and n8n (Docker) needs simple port mapping (5678).

### C. Data Availability
- **Status**: **High Feasibility**.
- **Source**: GigaScience and Neuralink datasets are publicly accessible standard formats (`.mat`, `.wav`).
- **Parsing**: Rust crates `matfile` and `hound` (WAV) are mature and available.

---

## 2. Impact Analysis

### A. Architectural Impact
| Component | Impact | Description |
|-----------|--------|-------------|
| **Backend (FastAPI)** | **Low** | Remains as a passive logger/controller. No breaking changes needed. |
| **Frontend (Next.js)** | **High** | Current UI is irrelevant. Will need a new "Signal Viewer" page later. |
| **Infrastructure** | **Medium** | New container (`bci-engine`) + `n8n` integration increases RAM usage by ~1GB. |

### B. Operational Impact
- **Development Speed**: **Accelerated**. No longer fighting "Product" features (Billing, UI polish). Pure engineering focus.
- **Resource Usage**:
    - *Before*: ~1.5GB RAM (Vault).
    - *After*: ~2.5GB RAM (Vault + BCI + n8n). *Verified: User has sufficient capacity.*

### C. Risk Assessment
1.  **Complexity Risk**: Signal processing math (FFT, filtering) is harder than CRUD.
    - *Mitigation*: Start with "Spike Detection" (simple amplitude threshold) before FFT.
2.  **Simulation vs. Reality**: File playback doesn't equal hardware latency.
    - *Mitigation*: Enforce `tokio::time::sleep` in the ingestion loop to strictly mimic realtime sample rates.

---

## 3. Conclusion & Recommendation
The pivot is **Technically Feasible** with **Manageable Impact**.
The existing SaaS architecture allows us to "plug in" the Brain (BCI) without rewriting the Body (Auth/DB).

**Green Light for Phase 10.**
