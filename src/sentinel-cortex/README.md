# 🧠 Sentinel Cortex - Decision Engine

## Multi-factor cognitive threat assessment system

## Overview

Sentinel Cortex is the cognitive decision engine for Sentinel's autonomous security system. It collects events from multiple sources, correlates them to detect attack patterns, and triggers automated response playbooks.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Sentinel Cortex (Rust Core)                    │
├─────────────────────────────────────────────────────────────┤
│  1. Ingest: Redis (ebpf_signals) + Prometheus (metrics)     │
│  2. Sanitize: AIOpsShield (Semantic Firewall)               │
│  3. Drip: FluidController (Laminar/Turbulent/FlashFlood)    │
│  4. Detect: Pattern Engine (Base-60 Confidence)             │
│  5. Action: N8N Trigger + Quantum Pulse Emission            │
└─────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  N8N Security (Playbooks)                        │
├─────────────────────────────────────────────────┤
│  • intrusion_lockdown                            │
│  • auto_remediation                              │
│  • backup_recovery                               │
└─────────────────────────────────────────────────┘
```

## Features

Currently implements 5 high-fidelity patterns:

1. **Credential Stuffing**: 50+ failed logins + IP anomaly.
2. **Resource Exhaustion**: Memory leak + CPU spike correlation.
3. **Database Attack**: Slow SQL + Auth failures burst.
4. **System Compromise**: Unauthorized root access or suspicious binaries.
5. **Data Exfiltration**: DNS Tunneling or massive data transfers.

### Confidence Scoring (Base-60)

Each pattern has a sexagesimal confidence score (n/60):
- **59/60 (~0.98)**: System Compromise (Critical)
- **57/60 (~0.95)**: Credential Stuffing
- **54/60 (~0.90)**: Database Attack
- **42/60 (~0.70)**: Threshold for triggering Playbooks

### Multi-Source Correlation

Correlates events across:
- Prometheus (metrics)
- Auditd (security events)
- Application logs (authentication)
- Network flows (data transfers)

## Quick Start

### Prerequisites

- Rust 1.75+
- Prometheus running
- N8N Security instance

### Build

```bash
cd sentinel-cortex
cargo build --release
```

### Run

```bash
# Copy environment file
cp .env.example .env

# Edit configuration
nano .env

# Run
cargo run
```

### Docker

```bash
docker build -t sentinel-cortex .
docker run --env-file .env sentinel-cortex
```

## Configuration

Environment variables (`.env`):

```bash
# Prometheus URL
PROMETHEUS_URL=http://prometheus:9090

# N8N Security URL
N8N_URL=http://n8n-security:5678

# Logging level
RUST_LOG=neural_guard=debug,info
```

## Development

### Project Structure

```
sentinel-cortex/
├── src/
│   ├── main.rs              # Adaptive Main Loop (Fluid Logic)
│   ├── models/              # Unified Event Models
│   │   └── event.rs
│   ├── collectors/          # Multi-Source Collectors
│   │   ├── prometheus.rs    # Periodic Metrics
│   │   └── redis_subscriber.rs # Real-time eBPF Signals
│   ├── engine/              # Decision Logic
│   │   ├── patterns.rs      # Pattern Correlation
│   │   ├── fluido.rs        # S60 Fluid Controller 
│   │   └── semantic_firewall.rs # AIOpsShield Middleware
│   └── actions/             # Response Layer
│       ├── n8n_client.rs    # Automation Trigger
│       └── quantum_pulse.rs # Bus Sync Emission
├── Cargo.toml
├── Dockerfile
└── .env.example
```

### Adding New Patterns

Edit `src/engine/patterns.rs`:

```rust
fn detect_your_pattern(&self, events: &[Event]) -> Option<DetectedPattern> {
    // Your detection logic
    if /* condition */ {
        return Some(DetectedPattern {
            name: "Your Pattern".to_string(),
            confidence: 0.90,
            severity: Severity::High,
            events: /* filtered events */,
            recommended_action: "What to do".to_string(),
            playbook: "playbook_name".to_string(),
        });
    }
    None
}
```

Then add to `detect()` method:

```rust
if let Some(pattern) = self.detect_your_pattern(events) {
    patterns.push(pattern);
}
```

### Testing

```bash
cargo test
```

## Roadmap

### Week 3-4 (Current)
- [x] Project setup
- [x] Data models
- [x] Prometheus collector
- [x] Pattern detector (2 patterns)
- [x] N8N client
- [x] Main loop
- [ ] Add 3 more patterns
- [ ] Integration tests
- [ ] Docker deployment

### Future
- [ ] PostgreSQL collector
- [ ] Loki collector
- [ ] Auditd collector
- [ ] Machine learning baseline
- [ ] Anomaly detection
- [ ] Auto-tuning confidence thresholds

## License

Part of Sentinel Sentinel Cortex (Patent Pending)

## Status

🚧 **In Development** - Week 3 of implementation
