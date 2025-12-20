# 🦅 Sentinel Project Context Analysis

**Date**: December 20, 2025
**Scope**: Full Codebase Review vs. Strategic BCI Pivot

## 1. Executive Summary
The project is currently structured as a **Commercial SaaS Platform** ("Sentinel Vault"), optimized for multi-tenancy. The strategic goal is to add a **Neural Interface Research Module** ("Sentinel Cortex") without disrupting the core product.

**Verdict**: The current architecture is "Over-Engineered" for the immediate BCI goal but provides a robust "Skeleton" for the future platform. We have a Ferrari (SaaS infrastructure) when we need a Rocket logic (Signal Processing).

## 2. Component Analysis

### A. Backend (`backend/app/main.py`)
- **Current State**: Robust FastAPI app with asyncpg, Prometheus instrumentation, and modular routers (`auth`, `tenants`, `incidents`).
- **BCI Relevance**: **Medium**.
    - *Keep*: Auth, Dashboard API, Health checks, and Database connections. These provide the "Control Plane" for your research.
    - *Ignore*: Tenant management, Billing, Backup systems. These are distractions for the MVP.
- **Action**: Use this as the "Logical Brain" API (Task 2 of implementation plan).

### B. Frontend (`frontend/src/app/page.tsx`)
- **Current State**: Next.js 14 app, currently redirecting to `/dashboard`.
- **BCI Relevance**: **Low (for now)**.
    - *Utility*: Good for visualizing the "Spikes" later.
    - *Action*: Deprioritize. The core innovation is in the backend/engine.

### C. WASM Engine (`sentinel-wasm/src/lib.rs`)
- **Current State**: Rust compiled to WASM for browser-side text pattern matching (`detect_aiopsdoom`) and basic Z-score anomaly detection (`calculate_anomaly_score`).
- **BCI Relevance**: **High (Conceptually)**.
    - *Reusable*: The `calculate_anomaly_score` function uses Mean/StdDev/Z-Score, which is nearly identical to basic "Threshold Spike Detection" in neuroscience.
    - *Gap*: It targets WASM (web). The new BCI Engine needs to target **Native Binary** (Linux) for performance and hardware I/O.
- **Action**: Clone this logic into the new `bci-engine` service but wrap it in `tokio` instead of `wasm-bindgen`.

## 3. The "Gap" (What's Missing)
1.  **Ingestion Layer**: No code exists to read `.mat`, `.wav`, or `.bids` files.
2.  **Signal Processing**: No FFT, Bandpass filters, or high-speed resampling (`rubato`).
3.  **Real-Time Loop**: The current system is Request-Response (HTTP), not Streaming (Event Loop).

## 4. Technical Debt & Cleanup
- The "Vault" features (Document encryption, etc.) are safe to keep as "modules" but should be mentally archived.
- **Do not delete them**; they are valuable IP. Just stop developing them.

## 5. Strategic Recommendation
**Don't burn the house down.** The SaaS scaffolding (`backend`, `docker-compose`) is excellent.

**The Pivot Plan**:
1.  **Freeze** the Frontend and core Backend features.
2.  **Create** a new directory `bci-engine/` (Rust).
3.  **Clone** `sentinel-wasm` logic into `bci-engine`.
4.  **Connect** `bci-engine` --> `n8n` (localhost) --> `Backend` (logging).

This transforms Sentinel from "A Vault that holds secrets" to "A Brain that processes signals", using the Vault as the memory bank.
