# 🛡️ SENTINEL CORTEX v7.0: DEPLOYMENT GUIDE (DEBIAN 13)

**Target System:** Debian 13 (Trixie) | **Arch:** x86_64
**Hardware:** NVIDIA GPU (3GB+) + Intel CPU (Hybrid)
**Features:** 10GB Data Capacity, Adaptative Control, Persistence.

---

## 1. NVIDIA Driver & CUDA 13 Setup
Ensure your Debian 13 has the latest proprietary drivers.

```bash
# Add contrib non-free-firmware
sudo apt update
sudo apt install nvidia-driver nvidia-smi nvidia-cuda-toolkit
```

Verify GPU visibility:
```bash
nvidia-smi
# Should show your 3GB GPU
```

---

## 2. Compile Sentinel Core (Rust + CUDA)
We need to build the optimized shared library.

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install Build Tools
sudo apt install python3-pip python3-venv maturin
cargo install maturin

# Build Sentinel Core
cd /home/jnovoas/dev/sentinel
cd rust
cargo build --release
cp target/release/libsentinel_core.so ../quantum/sentinel_core.so
cd ..
```

---

## 3. Install Python Dependencies
```bash
pip3 install numpy psutil
```

---

## 4. Install Systemd Service (Persistence)
Enable auto-restart and clean shutdown hooks.

```bash
# 1. Copy Service File
sudo cp sentinel-cortex.service /etc/systemd/system/

# 2. Update Paths (If needed)
# Edit the file if your User/Path differs from 'jnovoas'
# sudo nano /etc/systemd/system/sentinel-cortex.service

# 3. Enable & Start
sudo systemctl daemon-reload
sudo systemctl enable sentinel-cortex
sudo systemctl start sentinel-cortex
```

---

## 5. Verification
Check if the "Immortal Cortex" is breathing.

```bash
# Status
systemctl status sentinel-cortex.service

# Logs (Watch for "Startup" and "Snapshot" events)
journalctl -u sentinel-cortex -f
```

**Persistence Test:**
1. Let it run (it auto-loads `cortex_state.s60`).
2. `sudo reboot`.
3. Check logs: It should have saved on shutdown and loaded on startup.

---
*Protocol Yatra Secured.* 🛡️💎
