# Sentinel - Architecture & System Design

**Version**: 1.2.0 (S60-Unified / Fenix Native)
**Status**: 🚀 PRODUCTION READY (Node Fenix)

> [!CAUTION]
> This document consolidated both the **Production Environment (Fenix Native)** and the **Legacy PoC (Next.js/SOLID)**. 
> The core system operates on **S60 (Base-60) Arithmetic** and **Ring-0 eBPF Monitoring**. Standard IEEE-754 floats are prohibited in the decision engine.

---

## 🏗️ 1. Production Architecture (Fenix Node)

The production infrastructure resides on the **Fenix** host, orchestrated using Podman (rootless) and Traefik. The core backend has been migrated from Python to Rust (Axum/Tokio) for maximum performance and kernel-level integration.

### 1.1 component Diagram (Fenix)

```mermaid
graph TD
    subgraph "Public Internet"
        direction LR
        U[Authorized Operator]
    end

    subgraph "Fenix Host (Rocky Linux 9)"
        direction TB
        T[Traefik Edge Proxy]

        subgraph "Network: proxy (External)"
            direction LR
            C[sentinel-cortex (Rust)]
            F[sentinel-frontend (Next.js)]
            G[Grafana]
            P[Prometheus]
            N[n8n Automation]
        end

        subgraph "Network: sentinel_internal (Isolated)"
            direction LR
            DB[(PostgreSQL 16)]
            Cache[(Redis 7)]
            Loki[Loki Logs]
            Neural[Neural Guard]
        end

        U --> T
        T --> F
        T --> C
        T --> G
        T --> P
        T --> N

        C --> DB
        C --> Cache
        Neural --> Cache
        Neural --> Prometheus
        Neural --> Loki
    end
```

### 1.2 Key Service Definitions

*   **Traefik (Edge Proxy):** Handles SSL/TLS termination via PowerDNS/Let's Encrypt.
*   **Sentinel Cortex (Rust):** The high-performance core. Manages API requests and coordinates with the security engine.
*   **Neural Guard (Rust/eBPF):** The cognitive security layer. Monitors system health and kernel events (Ring-0) via eBPF hooks.
*   **Observability Stack:** Prometheus for time-series metrics, Loki for log aggregation, and Grafana for visualization.

---

## 🧿 2. Fundamental Principles (The YATRA Protocol)

### 2.1 S60 Sexagesimal Arithmetic
Sentinel rejects IEEE-754 floating-point numbers for critical security calculations due to precision drift.
- **Divisibility**: Base-60 is divisible by 2, 3, 4, 5, 6, 10, 12, 15, 20, and 30, minimizing truncation errors.
- **Implementation**: Handled by the `me-60os` Rust crate and Python `SPA` (Sexagesimal Pure Arithmetic) modules.

### 2.2 Octomechanical Thermal Coupling
The `Neural Guard` decision engine is thermally coupled. Security thresholds (e.g., login attempt lockouts) are dynamically adjusted based on the CPU's thermal baseline.
- **High Heat**: System enters "Resilient Mode" with higher tolerance for noise.
- **Low Heat**: System enters "Ultra-Sensitive Mode" with strict enforcement.

---

## 📜 3. Legacy / Normalized Architecture (PoC Stage)

*Note: This section describes the original Python/FastAPI PoC structure and the Next.js frontend organization used for training and simulation.*

### 3.1 SOLID Principles in Frontend
The Next.js frontend still adheres to standard SOLID principles for maintainability:
- **SRP**: Components like `StorageCard.tsx` have one job (rendering stats).
- **DIP**: The dashboard depends on custom hooks (`useAnalytics`) rather than direct API calls.

### 3.2 Legacy Python Backend
The original `sentinel-backend` (FastAPI) used Celery for background tasks and followed a standard multi-service Docker Compose pattern. It remains available for reference and legacy simulations.

---

## 🚀 4. Future Vision (Fase 2: Multi-Node Mesh)

- **MycNet**: A batman-adv based mesh network for decentralized node communication.
- **SOMA Orchestrator**: Transitioning from static Compose to an automated S60-aware resource manager.
