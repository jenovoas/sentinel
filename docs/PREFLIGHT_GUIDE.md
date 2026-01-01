# 🛫 Sentinel Pre-flight Check Guide

## Purpose

The **Sentinel Pre-flight Check** validates that a system meets all requirements before deploying Sentinel Cortex. It performs comprehensive checks of:
- Kernel version and eBPF support
- Required tools and compilers
- AI services (Ollama)
- Database (PostgreSQL)
- Sentinel components
- Hardware capabilities

## Usage

### Basic Check
```bash
sudo ./tools/sentinel_preflight.sh
```

### JSON Output
```bash
sudo ./tools/sentinel_preflight.sh --json
```

## What It Checks

### Critical Requirements (FAIL if missing)
1. **Root Privileges** - Must run as sudo
2. **Kernel Version** - Linux 6.1+ required for eBPF LSM
3. **bpftool** - eBPF management utility
4. **Clang Compiler** - For eBPF compilation
5. **Python 3** - For SemSH and scripts
6. **Sentinel Repository** - Must be cloned

### Recommended Components (WARN if missing)
1. **Rust/Cargo** - For rebuilding sctl/sip
2. **Ollama** - AI inference engine
3. **Llama 3.2 Model** - Specific model for SemSH
4. **PostgreSQL** - For SemSH history
5. **Sentinel Binaries** - Pre-compiled tools
6. **AES-NI/AVX2** - Hardware acceleration

### Runtime Checks
1. **TruthSync SHM** - Shared memory segment
2. **System Memory** - 4GB+ recommended
3. **eBPF LSM Support** - Kernel feature probe

## Example Output

```
🛡️  Sentinel Cortex Pre-flight Check
====================================

✅ Root Privileges: Running as root
✅ Kernel Version: 6.12.57+deb13-amd64 (>= 6.1 required)
✅ bpftool: Installed
⚠️  eBPF LSM Support: LSM support unclear, may need CONFIG_BPF_LSM=y
✅ Clang Compiler: Debian clang version 19.1.7
✅ Python 3: Python 3.13.5
✅ Rust/Cargo: cargo 1.70.0
✅ Ollama Service: Running
✅ Llama 3.2 Model: Installed
✅ PostgreSQL: Running (Docker)
✅ Sentinel Repository: Found at /home/jnovoas/sentinel
✅ Sentinel Relay Binary: Compiled
✅ sctl Command: Installed globally
✅ sip Command: Installed globally
✅ SHM Directory: /var/run/sentinel exists
✅ TruthSync SHM: Mounted (1048576 bytes)
✅ AES-NI Support: CPU supports hardware AES
✅ AVX2 Support: CPU supports SIMD instructions
✅ System Memory: 16GB (>= 4GB recommended)

====================================
Summary:
  Passed  : 18
  Failed  : 0
  Warnings: 1

✅ System is ready for Sentinel Cortex deployment
```

## JSON Output Format

```json
{
  "checks_passed": 18,
  "checks_failed": 0,
  "checks_warning": 1,
  "results": [
    {"check":"Root Privileges","status":"PASS","message":"Running as root"},
    {"check":"Kernel Version","status":"PASS","message":"6.12.57 (>= 6.1 required)"},
    ...
  ]
}
```

## Fixing Common Issues

### eBPF LSM Support Warning
```bash
# Check kernel config
zcat /proc/config.gz | grep CONFIG_BPF_LSM
# Should show: CONFIG_BPF_LSM=y

# If not, kernel needs to be recompiled with LSM support
```

### Ollama Not Running
```bash
# Start Ollama service
ollama serve &

# Pull required model
ollama pull llama3.2:3b
```

### Missing Sentinel Binaries
```bash
# Compile relay
cd guardian-alpha && make

# Build sctl
cd tools/sctl-rs && cargo build --release

# Build sip
cd tools/sip-rs && cargo build --release
```

### PostgreSQL Not Running
```bash
# Start Docker container
docker-compose up -d postgres

# Or install native
sudo apt install postgresql
```

## VM Deployment Workflow

1. **Clone Repository**
   ```bash
   git clone https://github.com/jnovoas/sentinel
   cd sentinel
   ```

2. **Run Pre-flight**
   ```bash
   sudo ./tools/sentinel_preflight.sh
   ```

3. **Fix Any Issues**
   - Address all FAIL status items
   - Optionally fix WARN items

4. **Deploy Sentinel**
   ```bash
   sudo sctl start
   sctl status
   ```

5. **Verify Operation**
   ```bash
   sem
   🧠 semsh> health
   ```

## Exit Codes

- **0**: All critical checks passed (ready for deployment)
- **1**: One or more critical checks failed (fix before deployment)

## Integration with CI/CD

```yaml
# Example GitHub Actions
- name: Pre-flight Check
  run: sudo ./tools/sentinel_preflight.sh --json > preflight.json
  
- name: Validate Results
  run: |
    FAILED=$(jq '.checks_failed' preflight.json)
    if [ "$FAILED" -gt 0 ]; then
      echo "Pre-flight failed"
      exit 1
    fi
```

## Notes

- **Always run as root** (sudo) for accurate system checks
- **JSON mode** is useful for automation and monitoring
- **Warnings are non-critical** but may impact performance
- **Re-run after fixes** to verify resolution

---

*Part of Sentinel Cortex v2.0 Tooling Suite*
