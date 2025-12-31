#!/bin/bash
# Sentinel Forensics Deployment Script

set -e

echo "🚀 [Sentinel] Building Phase 4: Memory Forensics..."

# 1. Build C eBPF
echo "🛠️  Compiling C eBPF tracepoint..."
cd ebpf_c
make clean && make
cd ..

# 2. Build Rust Userspace
echo "🦀 Compiling Rust userspace scanner..."
cargo build --release

echo "✅ Build complete."

# 3. Run (requires sudo)
echo "🧬 Starting Memory Forensics Service (requires sudo)..."
# Usamos ruta absoluta porque el eBPF Guardian la requiere para el whitelist
sudo $(pwd)/target/release/forensics
