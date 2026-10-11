# ⚠ Debian 13 "Trixie" - Critical Configuration Notes

## Why Debian 13 Trixie?

**Recommended for Sentinel Cortex** because:
- ✅ Kernel 6.12+ (native eBPF LSM support)
- ✅ Python 3.13 (latest features)
- ✅ Modern toolchain (Clang 19, Rust 1.70+)
- ✅ Up-to-date eBPF utilities

---

## 🚨 CRITICAL: /tmp on tmpfs Issue

### The Problem

Debian 13 Trixie mounts `/tmp` on **RAM (tmpfs)** by default. This causes issues when:
- Ollama downloads large models (3GB+) to `/tmp`
- Python creates temporary files during compilation
- Build processes use `/tmp` for intermediate artifacts

**Symptom**: Out of memory errors during `ollama pull` or package builds.

### The Solution

#### Option 1: Reconfigure /tmp to Use Disk (Recommended)

```bash
# Disable tmpfs for /tmp
sudo systemctl mask tmp.mount

# Reboot to apply
sudo reboot

# Verify after reboot
df -h /tmp
# Should show a disk partition, not tmpfs
```

#### Option 2: Configure Ollama to Use Persistent Storage

```bash
# Create persistent directory
sudo mkdir -p /var/lib/ollama
sudo chown -R $(whoami):$(whoami) /var/lib/ollama

# Set Ollama home
export OLLAMA_HOME=/var/lib/ollama
echo 'export OLLAMA_HOME=/var/lib/ollama' >> ~/.bashrc

# Start Ollama with custom path
OLLAMA_HOME=/var/lib/ollama ollama serve &
```

#### Option 3: Increase tmpfs Size (Quick Fix)

```bash
# Increase /tmp to 8GB (adjust based on RAM)
sudo mount -o remount,size=8G /tmp

# Make permanent
echo "tmpfs /tmp tmpfs defaults,size=8G 0 0" | sudo tee -a /etc/fstab
```

---

## VM Provisioning Specifications

### Minimum Requirements
- **OS**: Debian 13 "Trixie" (testing)
- **vCPU**: 4 cores
- **RAM**: 8GB (to handle Ollama + Sentinel stack)
- **Disk**: 20GB (10GB for OS, 5GB for Ollama models, 5GB for workspace)
- **Network**: Internet access for package installation

### Recommended for Production
- **vCPU**: 8 cores
- **RAM**: 16GB
- **Disk**: 40GB SSD
- **Network**: Low-latency connection

---

## Initial VM Setup

### 1. Update System

```bash
# Update package lists
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install base utilities
sudo apt install -y curl wget git vim htop
```

### 2. Verify Kernel Version

```bash
uname -r
# Expected: 6.12.x or higher

# Check eBPF LSM support
zcat /proc/config.gz | grep CONFIG_BPF_LSM
# Expected: CONFIG_BPF_LSM=y
```

### 3. Configure Persistent Storage

```bash
# Check current /tmp mount
df -h /tmp

# If tmpfs, apply Option 1 or 2 from above
# CRITICAL: Do this BEFORE installing Ollama
```

### 4. Install Dependencies

```bash
# Development tools
sudo apt install -y \
    build-essential \
    clang-19 \
    llvm-19 \
    python3.13 \
    python3.13-venv \
    python3-pip \
    bpftool \
    linux-headers-$(uname -r)

# Container runtime (for PostgreSQL)
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### 5. Install Rust

```bash
# Install rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Load environment
source ~/.cargo/env

# Verify
rustc --version
cargo --version
```

### 6. Install Ollama (with Persistent Storage)

```bash
# Set persistent home FIRST
export OLLAMA_HOME=/var/lib/ollama
echo 'export OLLAMA_HOME=/var/lib/ollama' >> ~/.bashrc

# Create directory
sudo mkdir -p /var/lib/ollama
sudo chown -R $USER:$USER /var/lib/ollama

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start service
OLLAMA_HOME=/var/lib/ollama ollama serve &

# Pull model (will download to /var/lib/ollama, not /tmp)
ollama pull llama3.2:3b

# Verify
ls -lh /var/lib/ollama/models/
```

---

## Verification Steps

### After Initial Setup

```bash
# 1. Check /tmp is NOT tmpfs (or is large enough)
df -h /tmp

# 2. Verify Ollama storage location
echo $OLLAMA_HOME
ls -lh $OLLAMA_HOME/models/

# 3. Check kernel features
sudo bpftool feature probe kernel | grep lsm

# 4. Verify Python version
python3 --version  # Should be 3.13.x

# 5. Check Rust
cargo --version  # Should be 1.70+
```

---

## Common Issues on Trixie

### Issue: "No space left on device" during ollama pull

**Cause**: /tmp is tmpfs and full  
**Fix**: Apply Option 1 or 2 from above

### Issue: Python venv creation fails

**Cause**: /tmp full or permission issues  
**Fix**: 
```bash
# Use custom temp directory
export TMPDIR=/var/tmp
python3 -m venv .venv
```

### Issue: Cargo build fails with "No space"

**Cause**: Cargo using /tmp for builds  
**Fix**:
```bash
# Set custom temp
export CARGO_TARGET_DIR=/var/tmp/cargo-target
cargo build --release
```

---

## Trixie-Specific Optimizations

### Kernel Parameters

```bash
# Add to /etc/sysctl.conf
sudo tee -a /etc/sysctl.conf << EOF
# eBPF optimizations
kernel.bpf_stats_enabled=1
kernel.unprivileged_bpf_disabled=0

# Performance
vm.swappiness=10
vm.vfs_cache_pressure=50
EOF

# Apply
sudo sysctl -p
```

### systemd Configuration

```bash
# Increase file limits for Sentinel services
sudo mkdir -p /etc/systemd/system.conf.d/
sudo tee /etc/systemd/system.conf.d/limits.conf << EOF
[Manager]
DefaultLimitNOFILE=65536
EOF

# Reload
sudo systemctl daemon-reload
```

---

## Deployment Checklist for Trixie

- [x] VM provisioned with Debian 13 Trixie ✅
- [x] Kernel 6.12+ verified (6.12.57+deb13-amd64) ✅
- [x] /tmp configured (not tmpfs OR increased size) ✅
- [x] OLLAMA_HOME set to /var/lib/ollama ✅
- [x] All dependencies installed ✅
- [x] Rust toolchain installed (1.92.0) ✅
- [x] Ollama model downloaded successfully (llama3.2:3b) ✅
- [x] Pre-flight check passes (16 passed, 0 failed) ✅
- [x] Sentinel deployed: `sudo sctl start` ✅
- [x] All components ACTIVE/RUNNING ✅
- [x] Validation complete (100% tests passed) ✅

**Deployment Date**: 2026-01-01  
**Status**: ✅ PRODUCTION READY

---

## Next Steps

After completing this setup:

1. Clone Sentinel repository
2. Run pre-flight check: `sudo ./tools/sentinel_preflight.sh`
3. Build components (if needed)
4. Deploy: `sudo sctl start`
5. Verify: `sudo sctl status`

---

*Critical configuration guide for Debian 13 Trixie deployment*  
*Last updated: 2026-01-01*
