#!/bin/bash
# Install eBPF dependencies for Debian Trixie

echo "🔧 Installing eBPF dependencies for Debian..."
sudo apt-get update
sudo apt-get install -y clang llvm libbpf-dev linux-headers-$(uname -r) bpftool

echo "✅ Dependencies installed."
