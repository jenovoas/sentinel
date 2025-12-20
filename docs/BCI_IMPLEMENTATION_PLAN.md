# 🧠 Sentinel Cortex: BCI Implementation Plan

**Strategy**: "Experimental Research Module".
**Goal**: Build a functional BCI MVP using open datasets, a Rust ingestion engine, and n8n for orchestration, without waiting for hardware partnerships.

## 1. Data Acquisition (The "Senses")
We will use real-world neurophysiological data to simulate live streams.

- **Source A**: **Neuralink Compression Challenge** (Raw motor cortex recordings, WAV, 10-bit).
- **Source B**: **GigaScience / GigaDB** (Motor imagery: left/right hand movements).
- **Source C**: **OpenNeuro** (ECoG/iEEG data, BIDS format).

**Action**:
- [ ] Locate and download sample datasets (start with GigaScience for structured labeled data).
- [ ] Create a local `data/raw` directory to store these samples.

## 2. The Core Architecture

### Component A: Rust Ingestion Engine ("The Fast Brain")
A high-performance service responsible for reading raw bio-signals and detecting events in micro-real-time.

- **Stack**: Rust
- **Libraries**:
    - `rubato` (Resampling)
    - `ndarray` (Matrix manipulation)
    - `tokio` (Async runtime)
    - `reqwest` (HTTP client for Webhooks)
- **Functions**:
    1.  **Stream Simulation**: Read static file `.mat` or `.wav` chunk by chunk to simulate real-time feed (e.g., 30k samples/sec).
    2.  **Signal Processing**: Basic bandpass filter (10-100Hz) and Spike Detection (Threshold crossing).
    3.  **Event Trigger**: When a "spike" or specific pattern is detected, construct a JSON payload.
    4.  **Dispatch**: POST JSON to n8n Webhook.

### Component B: n8n Orchestrator ("The Logical Brain")
Handles the "aftermath" of a detected neural event.

- **Trigger**: Webhook node (listening on `localhost:5678`).
- **Logic**:
    - **Parse**: Extract `intent`, `confidence`, `timestamp`.
    - **Decision**: `Switch` node (e.g., If `confidence > 0.90`).
- **Action**:
    - **MVP**: Log to file / Google Sheet.
    - **Demo**: Send a verified notification, trigger a system command, or update a frontend UI element.

## 3. Simulated Integration (The "Trojan Horse")
Prepare for future hardware integration by mimicking industry standards.

- **CereStim Wrapper**: Create a Rust trait/interface that mimics the Blackrock CereStim API structure.
- **Benefit**: Allows swapping the "File Reader" backend for a "Hardware Driver" backend later without changing application logic.

## 4. Immediate Roadmap (Next 24h)
1.  **Environment**: Ensure Rust (`cargo`) and n8n (Docker) are running.
2.  **Data**: Download one valid `.mat` file from GigaScience.
3.  **Prototype**: Write `src/bci_reader.rs` to read the file and print spikes to stdout.
4.  **Connect**: Send one HTTP POST from Rust to n8n.

---

> "Zero Ego, 100% Physics."
