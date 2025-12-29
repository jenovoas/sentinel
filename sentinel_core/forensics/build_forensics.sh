#!/bin/bash
# build_forensics.sh - Sentinel Forensics Build Automation

set -e

# 1. Build eBPF program
echo "🦀 Building eBPF tracepoint..."
cd forensics-ebpf
cargo build --target bpfel-unknown-none -Z build-std=core --release
cd ..

# 2. Extract or copy the eBPF object to where the userspace expects it
# (Already handled by include_bytes_aligned! looking into target/...)

# 3. Build Userspace Service
echo "🚀 Building userspace scanner..."
cargo build --release

echo "✅ Build complete! Run with: sudo ./target/release/forensics"
