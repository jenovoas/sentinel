# 🚀 Sentinel Cortex - VM Deployment Guide

## Quick Start (5 Minutes)

### Prerequisites
- **VM**: Debian/Ubuntu 22.04+ or Fedora 38+
- **Resources**: 2+ vCPU, 4GB+ RAM, 10GB disk
- **Network**: Internet access for package installation
- **Access**: SSH with sudo privileges

---

## Step-by-Step Deployment

### 1. Prepare VM

```bash
# Update system
sudo apt update && sudo apt upgrade -y  # Debian/Ubuntu
# OR
sudo dnf update -y  # Fedora

# Install base dependencies
sudo apt install -y git curl build-essential clang llvm \
    python3 python3-pip python3-venv \
    postgresql-client docker.io jq

# Install Rust (if not present)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### 2. Install Ollama (AI Engine)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start service
ollama serve &

# Pull model (this will take a few minutes)
ollama pull llama3.2:3b
```

### 3. Setup PostgreSQL (Optional but Recommended)

```bash
# Using Docker (easiest)
docker run -d \
  --name sentinel-postgres \
  -e POSTGRES_DB=truth \
  -e POSTGRES_USER=truth \
  -e POSTGRES_PASSWORD=sentinel_secret_password \
  -p 5432:5432 \
  postgres:15

# Verify
docker ps | grep postgres
```

### 4. Clone Sentinel Repository

```bash
# Clone from GitHub
git clone https://github.com/jnovoas/sentinel
cd sentinel

# Verify structure
ls -la
```

### 5. Run Pre-flight Check

```bash
# Execute validation
sudo ./tools/sentinel_preflight.sh

# Expected output: 18+ checks passed
# Fix any FAIL items before proceeding
```

### 6. Build Components (if needed)

```bash
# eBPF Relay
cd guardian-alpha
make
cd ..

# System tools (sctl, sip)
cd tools/sctl-rs
RUSTFLAGS="-C target-cpu=native -C opt-level=3" cargo build --release
sudo cp target/release/sctl /usr/local/bin/
cd ../..

cd tools/sip-rs
RUSTFLAGS="-C target-cpu=native -C opt-level=3" cargo build --release
sudo cp target/release/sip /usr/local/bin/
cd ../..

# Python environment
python3 -m venv .venv
source .venv/bin/python
pip install ollama psycopg2-binary numpy pyyaml psutil
```

### 7. Deploy Sentinel

```bash
# Start all services
sudo sctl start

# Verify status
sudo sctl status

# Expected output:
# ✅ eBPF LSM: ACTIVE
# ✅ Sentinel Relay: RUNNING
# ✅ Kernel Pulse: RUNNING
# ✅ TruthSync SHM: MOUNTED
```

### 8. Apply x86 Optimizations

```bash
# Apply performance tuning
sudo sctl tune

# Verify
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# Should show: performance
```

### 9. Test System

```bash
# Launch semantic shell
sem

# Test commands
🧠 semsh> health
🧠 semsh> dashboard
🧠 semsh> review rm -rf /
🧠 semsh> exit
```

### 10. Run Benchmark

```bash
# Execute performance test
./.venv/bin/python bench_final_system.py

# Expected results:
# TTE (Load): < 10 μs
# CPU Overhead: 0%
# RAM: ~2 MB
```

---

## Verification Checklist

After deployment, verify:

- [ ] `sudo sctl status` shows all services ACTIVE/RUNNING
- [ ] `sem` launches without errors
- [ ] `sem > health` reports no critical issues
- [ ] Benchmark shows TTE < 10 μs
- [ ] GUI connects (if testing): `cd gui && npm run tauri dev`

---

## Troubleshooting

### eBPF LSM Not Loading

```bash
# Check kernel config
zcat /proc/config.gz | grep CONFIG_BPF_LSM
# Must show: CONFIG_BPF_LSM=y

# If not, kernel doesn't support LSM
# Solution: Use a kernel 6.1+ with LSM support
```

### Ollama Connection Failed

```bash
# Check if running
pgrep ollama

# Restart
pkill ollama
ollama serve &

# Test
ollama list
```

### PostgreSQL Connection Refused

```bash
# Check Docker container
docker ps -a | grep postgres

# Restart if needed
docker start sentinel-postgres

# Test connection
psql -h localhost -U truth -d truth
# Password: sentinel_secret_password
```

### SemSH Import Errors

```bash
# Reinstall dependencies
source .venv/bin/activate
pip install --upgrade ollama psycopg2-binary numpy pyyaml
```

---

## Performance Tuning (Optional)

### For Production Workloads

```bash
# Increase hugepages
echo 20 | sudo tee /proc/sys/vm/nr_hugepages

# Disable swap (if enough RAM)
sudo swapoff -a

# Set CPU governor permanently
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### For Development

```bash
# Keep defaults, just ensure services run
sudo sctl start
```

---

## Monitoring

### Real-time Status

```bash
# Watch system health
watch -n 1 'sctl status'

# Monitor logs
sudo sctl logs

# Check semantic vectors
sctl status --json | jq '.semantic_vectors'
```

### GUI Dashboard (Optional)

```bash
cd gui
npm install
npm run tauri dev
```

---

## Uninstall / Cleanup

```bash
# Stop services
sudo sctl stop

# Remove binaries
sudo rm /usr/local/bin/sctl
sudo rm /usr/local/bin/sip

# Clean SHM
sudo rm -rf /var/run/sentinel

# Remove repository
cd ..
rm -rf sentinel
```

---

## Next Steps After Deployment

1. **Load Testing**: Run HTTP server under Sentinel
2. **Custom Playbooks**: Create automation for your workflows
3. **SIP Packages**: Build and install signed packages
4. **GUI Customization**: Modify Tauri app for your needs

---

## Support

- **Documentation**: `/docs/` directory
- **Issues**: GitHub Issues
- **Pre-flight**: `sudo ./tools/sentinel_preflight.sh`

---

*Sentinel Cortex v2.0 - Production-Ready Alpha*  
*"An operating system that thinks before it acts."* 🛡️
