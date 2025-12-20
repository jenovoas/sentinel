# BCI MVP Implementation Plan

## Goal
Implement the **Sentinel Cortex BCI MVP** ("Phase 10") by creating the Rust Ingestion Engine, integrating n8n, and simulating neural data flow.

## User Review Required
> [!NOTE]
> This plan involves creating a new Rust service (`bci-engine`) and modifying the `docker-compose.yml` to include `n8n`. It shifts focus away from the current frontend.

## Proposed Changes

### 1. Infrastructure Layer

#### [MODIFY] [docker-compose.yml](file:///home/jnovoas/sentinel/docker-compose.yml)
- **Add Service: `n8n`**
    - Image: `docker.n8n.io/n8nio/n8n`
    - Ports: `5678:5678`
    - Volumes: `./n8n_data:/home/node/.n8n`
    - Environment: `WEBHOOK_URL=http://localhost:5678/`

#### [MODIFY] [docker-compose.yml](file:///home/jnovoas/sentinel/docker-compose.yml)
- **Add Service: `bci-engine`**
    - Build Context: `./bci-engine`
    - Environment: `N8N_WEBHOOK_URL=http://n8n:5678/webhook/neural-event`
    - Depends On: `n8n`

### 2. BCI Engine (New Service)

#### [NEW] [bci-engine/Cargo.toml](file:///home/jnovoas/sentinel/bci-engine/Cargo.toml)
- Define Rust workspace members.
- Dependencies: `tokio`, `reqwest`, `serde`, `serde_json`, `rand` (for simulation), `rubato` (placeholder).

#### [NEW] [bci-engine/src/main.rs](file:///home/jnovoas/sentinel/bci-engine/src/main.rs)
- **Main Loop**: Async loop running at 30Hz (simulated chunk rate).
- **Simulated Data**: Generate synthetic "neural spikes" (random floats > threshold) for the MVP (until real files are downloaded).
- **Event Dispatch**: HTTP POST to n8n when a spike is generated.

#### [NEW] [bci-engine/Dockerfile](file:///home/jnovoas/sentinel/bci-engine/Dockerfile)
- Standard Rust build image.

## Verification Plan

### Automated Verification
- **Build Test**: Run `docker-compose build bci-engine` to ensure Rust compiles.
- **Connectivity Test**:
    1. Start stack: `docker-compose up -d n8n bci-engine`.
    2. Check logs: `docker logs -f sentinel-bci-engine`.
    3. Failure criteria: Connection refused errors to n8n.

### Manual Verification
- **n8n UI**:
    1. Open `http://localhost:5678`.
    2. Create a "Webhook" node (POST).
    3. Verify that "neural events" appear in the execution list.
