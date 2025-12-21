#!/bin/bash
# Install eBPF dependencies for Sentinel Cortex™

echo "============================================================"
echo "Sentinel Cortex™ - eBPF Dependencies Installer"
echo "============================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "[!] Please run as root (sudo ./install_ebpf_deps.sh)"
    exit 1
fi

echo "[*] Installing eBPF development tools..."

# Update package list
apt-get update -qq

# Install kernel headers
echo "[*] Installing kernel headers..."
apt-get install -y linux-headers-$(uname -r)

# Install BCC (BPF Compiler Collection)
echo "[*] Installing BCC..."
apt-get install -y python3-bpfcc bpfcc-tools

# Install libbpf
echo "[*] Installing libbpf..."
apt-get install -y libbpf-dev

# Install clang/LLVM
echo "[*] Installing clang/LLVM..."
apt-get install -y clang llvm

# Verify installation
echo ""
echo "[*] Verifying installation..."

if command -v bpftool &> /dev/null; then
    echo "[+] bpftool: $(bpftool --version)"
else
    echo "[!] bpftool not found"
fi

if python3 -c "import bcc" 2>/dev/null; then
    echo "[+] BCC Python module: OK"
else
    echo "[!] BCC Python module not found"
fi

if command -v clang &> /dev/null; then
    echo "[+] clang: $(clang --version | head -1)"
else
    echo "[!] clang not found"
fi

echo ""
echo "============================================================"
echo "[+] Installation complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Test burst sensor: sudo python3 ebpf/burst_sensor_loader.py lo"
echo "2. Generate traffic: ping -f localhost"
echo ""
