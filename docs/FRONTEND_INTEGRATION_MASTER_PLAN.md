# Frontend Integration Master Plan: Sentinel Cortex v2.0

## 1. Executive Summary
The goal is to consolidate all Sentinel subsystems (AI, Security, Ops, Finance) into a **Single Pane of Glass** interface. This "Control Tower" approach ensures that the operator has immediate visibility and control over the entire verified ecosystem, leveraging the "Cyberpunk/Hacker Premium" aesthetic for maximum usability and impact.

## 2. Architecture Overview
*   **Frontend:** Next.js 14 (App Router) + Tailwind CSS + Lucide Icons + Framer Motion.
*   **Backend:** FastAPI (Python) exposing REST endpoints.
*   **Data Layer:** PostgreSQL (State), Redis (Cache/Queue).
*   **Observability:** Prometheus (Metrics), Loki (Logs), Grafana (Visualization), Node Exporter (Hardware).
*   **AI Engine:** Ollama (Phi-3/Llama-3) + Sentinel Cortex (Python Orchestrator).

## 3. Module Integration Strategy

### A. Landing / Command Deck (`/`)
*   **Status:** ✅ **DONE**
*   **Features:**
    *   Global KPI Grid (System Status, Threats, AI Latency, etc.).
    *   Real-time Alerts Panel.
    *   AI Intervention Log ("Processes Neutralized").
    *   TruthSync Consensus Monitor.
*   **Next Steps:** Connect "System Status" and "Active Threats" to real backend endpoints (`/api/v1/status`) instead of static props.

### B. Secure Workspace (`/dashboard`)
*   **Status:** ✅ **DONE**
*   **Features:**
    *   **Secure Browser:** Isolation mode, Tor routing (via proxy), Content sanitization.
    *   **Crypto Wallet:** Multi-chain (BTC, ETH, SOL), Cold storage integration logic.
*   **Next Steps:**
    *   Ensure `SecureBrowser` component correctly hits `/browser/browse` endpoint.
    *   Verify Wallet balance updates via `/finance/wallet/status`.

### C. Ops Center (`/dash-op`)
*   **Status:** 🚧 **PARTIAL**
*   **Features:** Real-time system health (CPU, RAM, Network).
*   **Integration Plan:**
    *   **Current:** Uses mock data or basic API.
    *   **Target:** Embed **Grafana Panels** (iframe mode) for CPU/Memory history, or query Prometheus directly via backend proxy to render Custom React Charts (Recharts).
    *   **Recommendation:** Use **Grafana Iframes** for complex historical graphs, use **Prometheus API** for "Current Value" stats (Speedometer style).

### D. Cortex AI (`/cortex`)
*   **Status:** ✅ **DONE** (Brain V1)
*   **Features:** Chat with Sentinel Core (Ollama).
*   **Integration Plan:**
    *   Identify context-aware capabilities (e.g., "Analyze this log file").
    *   Allow Cortex to execute safe commands (with human approval flows).

### E. Security Watchdog (`/security/watchdog`)
*   **Status:** 🚧 **NEEDS UPDATE**
*   **Features:** Auditd logs, Intrusion Detection.
*   **Integration Plan:**
    *   Replace custom log viewers with **Loki-backed Tables**.
    *   Filter logs by severity (Emergency, Alert, Critical).
    *   Visualize attacks on a world map (Use `react-simple-maps` + GeoIP from logs).

### F. Analytics & Reports (`/analytics`)
*   **Status:** 🚧 **PENDING**
*   **Features:** Historical reporting.
*   **Integration Plan:**
    *   This page should be a wrapper around full **Grafana Dashboards**.
    *   Embed `http://localhost:3000/monitoring` functionality here but with datepickers.

### G. Databases (`/db`)
*   **Status:** ✅ **DONE**
*   **Features:** PostgreSQL instance management, Query monitoring.
*   **Integration Plan:**
    *   Ensure `pg_stat_activity` queries are live.
    *   Add "Kill Query" button (Admin only).

### H. Documentation (`/docs` - renamed from `/reports`)
*   **Status:** ✅ **DONE**
*   **Features:** Markdown renderer for `docs/` folder.
*   **Integration Plan:**
    *   Add search functionality (Client-side fuse.js or server-side grep).
    *   Auto-generate Table of Contents.

## 4. Implementation Roadmap (Immediate Priority)

1.  **Refine Landing KPIs:** Create `useSentinelStatus()` hook to fetch real data from Backend + Prometheus.
2.  **Ops Center Upgrade:** Replace static graphs with Grafana Iframes (CPU/Mem/Net).
3.  **Security Watchdog:** Wire up to Loki via Backend Proxy (`/api/v1/logs/query`).
4.  **Global Polish:** Ensure "Glassmorphism" consistent across all pages.

## 5. Technical Requirements
*   **Backend:** Ensure `/api/v1/metrics` and `/api/v1/logs` endpoints proxy to Prometheus/Loki if direct frontend access is restricted (CORS).
*   **Docker:** Verify `grafana`, `loki`, `prometheus` are always up.
