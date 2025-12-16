# 🧠 Sentinel Cortex - Decision Engine

**Patent Claim 2**: Multi-factor cognitive threat assessment system

## Overview

Sentinel Cortex is the cognitive decision engine for Sentinel's autonomous security system. It collects events from multiple sources, correlates them to detect attack patterns, and triggers automated response playbooks.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Data Sources                                    │
├─────────────────────────────────────────────────┤
│  • Prometheus (metrics)                          │
│  • PostgreSQL (events)                           │
│  • Loki (logs)                                   │
│  • Auditd (security)                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Sentinel Cortex (Rust)                             │
├─────────────────────────────────────────────────┤
│  1. Collect events (every 30s)                   │
│  2. Detect patterns (multi-factor)               │
│  3. Calculate confidence (0.0-1.0)               │
│  4. Trigger playbooks (if confidence > 0.7)      │
└────────────────┬────────────────────────────────┘
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

### Pattern Detection

Currently implements 2 patterns (more coming):

1. **Credential Stuffing**: 50+ failed logins + successful login from new IP
2. **Resource Exhaustion**: Memory leak + CPU spike

### Confidence Scoring

Each pattern has a confidence score (0.0-1.0):
- **0.95**: Credential stuffing (very high confidence)
- **0.85**: Resource exhaustion (high confidence)
- **0.70**: Threshold for triggering playbooks

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
│   ├── main.rs              # Main loop
│   ├── models/              # Data structures
│   │   └── event.rs
│   ├── collectors/          # Data collectors
│   │   └── prometheus.rs
│   ├── engine/              # Pattern detection
│   │   └── patterns.rs
│   └── actions/             # N8N integration
│       └── n8n_client.rs
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
