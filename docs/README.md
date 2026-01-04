# SENTINEL CORTEX v2.0 - SOVEREIGN SYSTEM
**⚠️ PROPRIETARY & CONFIDENTIAL**
**COPYRIGHT (C) 2026 JAIME NOVOA. ALL RIGHTS RESERVED.**

> **WARNING:** This repository contains advanced quantum algorithms and cognitive architectures protected by Sovereign Family Law. Unauthorized copying, reverse engineering, or distribution is strictly prohibited.

## 🔒 SYSTEM STATUS: CLOSED / PRIVATE
This system is no longer public property. It is the intellectual core of the Novoa Family Sovereignty Project.

## 🌍 STRATEGIC ACCESS (Public Interface)
While the *Core* is locked, specific modules may be accessed via the **Strategic Release Protocol** (see `STRATEGIC_RELEASE_PROTOCOL.md`) for commercial or scientific partnership purposes.

---

### Documentation for Independent Validation

- **[FOR_RESEARCHERS.md](FOR_RESEARCHERS.md)** - Quick validation guide (2 min)
- **[VALIDATION_REPORT.md](VALIDATION_REPORT.md)** - Full technical validation (scientific)
- **[REPRODUCIBILITY_GUIDE.md](REPRODUCIBILITY_GUIDE.md)** - Step-by-step verification
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Deployment summary
- **validate_system.py** - Automated test suite (9 tests)
- **validation_results.json** - Machine-readable results

### Validated Claims

| Claim | Target | Actual | Evidence |
|-------|--------|--------|----------|
| TTE < 10 μs | < 10 μs | 8.12 μs | `bench_final_system.py` |
| CPU < 1% | < 1% | 0.9% | Process monitoring |
| RAM < 3 MB | < 3 MB | 2.14 MB | Process monitoring |
| Real-time Events | Yes | Yes | Live eBPF capture |
| AI Integration | Yes | Yes | Ollama operational |

---

## Quick Start

### Installation
```bash
git clone https://github.com/jnovoas/sentinel
cd sentinel
sudo ./deploy_semsh.sh
```

### Launch System
```bash
sudo sctl start      # Start all services
sctl status          # Verify health
sem                  # Enter semantic shell
```

---

## Core Documentation

### Architecture & Design
- **[DATASHEET.md](DATASHEET.md)** - Executive summary and system overview
- **[ARCHITECTURE_V2_LIVE_MAP.md](docs/ARCHITECTURE_V2_LIVE_MAP.md)** - System architecture diagram
- **[SYSTEM_ADMIN_PROTOCOL.md](docs/SYSTEM_ADMIN_PROTOCOL.md)** - AI-DevOps contract (SSAP)

### Performance & Optimization
- **[BENCHMARK_RESULTS_FINAL.md](docs/BENCHMARK_RESULTS_FINAL.md)** - Initial benchmark results
- **[X86_OPTIMIZATION_RESULTS.md](docs/X86_OPTIMIZATION_RESULTS.md)** - Post-tuning performance analysis
- **[BENCHMARKS_CONSOLIDATED.md](docs/BENCHMARKS_CONSOLIDATED.md)** - Historical benchmarks

### User Guides
- **[SEMSH_SSAP_GUIDE.md](docs/SEMSH_SSAP_GUIDE.md)** - SemSH v0.3 usage guide
- **[TOOLING_GUIDE.md](docs/TOOLING_GUIDE.md)** - System tools reference
- **[SECURE_PACKAGING_PROPOSAL.md](docs/SECURE_PACKAGING_PROPOSAL.md)** - SIP package manager

### Implementation Details
- **[PHASE_3_GUI_PROTOTYPE.md](docs/PHASE_3_GUI_PROTOTYPE.md)** - GUI development
- **[RINGBUF_MIGRATION.md](guardian-alpha/RINGBUF_MIGRATION.md)** - eBPF ringbuf implementation

---

## Component Reference

### System Control (`sctl`)
**Location**: `tools/sctl-rs/`  
**Language**: Rust  
**Purpose**: Unified system control and monitoring

```bash
sudo sctl start              # Launch Sentinel services
sudo sctl stop               # Stop all services
sudo sctl status             # Health dashboard
sudo sctl status --json      # Machine-readable output
sudo sctl tune               # Apply x86_64 optimizations
```

**Features**:
- eBPF LSM detection (via bpftool)
- Real-time semantic vector reading from SHM
- CPU/Memory monitoring
- x86_64 performance tuning (hugepages, governor, affinity)

---

### Semantic Shell (`sem`)
**Location**: `sem_shell.py`  
**Language**: Python + Ollama  
**Purpose**: AI-powered command interpretation

```bash
sem                          # Launch interactive shell
```

**Commands**:
- `health` - System health advisor
- `review <cmd>` - AI command risk analysis
- `run <playbook>` - Execute YAML playbook
- `dashboard` - Vector state visualization
- `<natural language>` - Convert to bash command

**Example**:
```bash
🧠 semsh> health
⚠️  [CRITICAL] eBPF LSM is INACTIVE
   → Suggested Action: sudo sctl start

🧠 semsh> review rm -rf /
🔴 CRITICAL WARNING: Destructive pattern detected!

🧠 semsh> run backup_db
📋 Executing Playbook: backup_critical_db
   Proceed? [y/N]:
```

---

### Secure Package Manager (`sip`)
**Location**: `tools/sip-rs/`  
**Language**: Rust  
**Purpose**: Cryptographically signed package management

```bash
sip keygen --out mykey           # Generate Ed25519 keypair
sip sign --source ./app \        # Sign package
         --key mykey.priv \
         --out app.sip
sip install --package app.sip \  # Install with verification
            --pubkey mykey.pub
```

**Security**:
- Ed25519 digital signatures
- Semantic intent validation (AI checks intent.json)
- Supply chain integrity

---

### Docker Wrapper (`sdocker`)
**Location**: `tools/sdocker`  
**Language**: Python  
**Purpose**: Safe Docker operations

```bash
sdocker status               # JSON container metrics
sdocker safe-restart <svc>   # Validated restart
sdocker logs <container>     # Safe log access
```

**Safety Features**:
- Service whitelist enforcement
- Dependency checking
- Impact analysis before restart

---

## Playbook System

**Location**: `playbooks/`  
**Format**: YAML  
**Execution**: `sem run <playbook_name>`

### Available Playbooks

**backup_db.yaml**
- Full PostgreSQL backup
- Disk space verification
- Integrity checking
- Automatic rollback on failure

**cleanup_logs.yaml**
- System log rotation
- Sentinel log cleanup
- Space verification

### Creating Playbooks

```yaml
name: my_playbook
description: "What this does"
risk_level: low|medium|high
steps:
  - name: step_name
    cmd: "bash command"
    failure_msg: "Error message"
rollback:
  - cmd: "undo command"
```

---

## Architecture Overview

### Three-Layer Security

```
┌─────────────────────────────────┐
│  AI Layer (Cognitive)           │
│  • Intent interpretation        │
│  • Self-censorship              │
│  • Context awareness            │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│  Validation Layer (Relay)       │
│  • Whitelist enforcement        │
│  • Signature verification       │
│  • Pre-execution checks         │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│  Kernel Layer (eBPF LSM)        │
│  • Syscall interception         │
│  • Immutable enforcement        │
│  • Fail-closed policy           │
└─────────────────────────────────┘
```

### Data Flow

```
User Command
    ↓
SemSH (AI Interpretation)
    ↓
Sentinel Relay (Validation)
    ↓
eBPF LSM (Kernel Enforcement)
    ↓
TruthSync SHM (Telemetry)
    ↓
GUI / sctl (Visualization)
```

---

## Performance Characteristics

### Latency (Post x86 Optimization)
- **TTE (Time-To-Enforcement)**: 8.71 μs average under load
- **Process Execution**: 0.57 ms average
- **P95 Latency**: 49.02 μs

### Resource Usage
- **CPU Overhead**: 0.0% (event-driven)
- **Memory (Relay)**: 2.08 MB
- **Disk (Base System)**: ~2 GB

### Optimization Features
- CPU Governor: performance mode
- Hugepages: 10 × 2MB reserved
- Core Affinity: Relay pinned to CPU 0
- Compilation: target-cpu=native, AES-NI enabled

---

## Development

### Build Requirements
- **Rust**: 1.70+
- **Python**: 3.10+
- **Clang**: 14+
- **Node.js**: 14+ (for GUI)

### Build Commands
```bash
# System tools
cd tools/sctl-rs && cargo build --release
cd tools/sip-rs && cargo build --release

# GUI
cd gui && npm install && npm run tauri build

# eBPF
cd guardian-alpha && make
```

### Testing
```bash
# System benchmark
python bench_final_system.py

# SHM latency
python bench_synapse.py

# Component tests
sudo sctl start
sctl status
sem
```

---

## Troubleshooting

### eBPF LSM shows INACTIVE
```bash
# Check if loaded (requires sudo)
sudo sctl status

# Reload if needed
sudo sctl stop
sudo sctl start
```

### SemSH connection errors
```bash
# Verify Ollama is running
ollama list

# Check PostgreSQL
docker ps | grep postgres

# Restart services
sudo sctl restart
```

### GUI not connecting to backend
```bash
# Ensure kernel_pulse is running
sctl status

# Check SHM permissions
ls -l /var/run/sentinel/truthsync_shm

# Restart pulse
sudo pkill -f kernel_pulse
sudo sctl start
```

---

## Contributing

### Code Style
- **Rust**: `cargo fmt`
- **Python**: PEP 8
- **Shell**: ShellCheck compliant

### Commit Messages
```
Feat: Add new feature
Fix: Bug fix
Docs: Documentation update
Perf: Performance improvement
Refactor: Code refactoring
```

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Update documentation
6. Submit PR

---

## License

[To be defined]

---

## Contact

**Author**: jnovoas  
**Repository**: https://github.com/jnovoas/sentinel  
**Issues**: GitHub Issues  

---

## Acknowledgments

Built upon research from:
- eBPF/BCC project
- Cilium security framework
- Linux kernel LSM subsystem
- Modern LLM-ops research

---

*Last Updated: 2026-01-01*
