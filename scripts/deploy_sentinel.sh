#!/bin/bash
# scripts/deploy_sentinel.sh
# Master Deployment Script for Sentinel OS Foundation (Ironclad v3.0.0)

set -e

PROJECT_ROOT=$(pwd)
STAGE=${1:-staging}
BRIDGE_SOCAT=${2:-false}

echo "🛡️ Starting Sentinel IRONCLAD Deployment (Stage: $STAGE)..."

# 1. Compile Core Init System
echo "🦀 Compiling Rust Init System (musl target)..."
cd "$PROJECT_ROOT/sentinel_core/init"
cargo build --release --target x86_64-unknown-linux-musl

# 2. Package Initramfs
echo "📦 Packaging Initramfs..."
cd "$PROJECT_ROOT"
./scripts/build_initramfs.sh

# 3. Handle Socat Bridge (Legacy Link)
if [ "$BRIDGE_SOCAT" = "true" ] || [ "$BRIDGE_SOCAT" = "--socket-bridge" ]; then
    echo "🌉 Launching Socat Bridge (Host:5678 <-> /tmp/sentinel_cortex.sock)..."
    # Ensure n8n port is mapped or use internal docker networking
    # For now, we simulate the redirection
    socat UNIX-LISTEN:/tmp/sentinel_cortex.sock,fork,reuseaddr,mode=666 TCP:localhost:5678 &
    BRIDGE_PID=$!
    echo "[info] Socat Bridge active (PID: $BRIDGE_PID)"
fi

# 4. Deploy Observability & Brain Stack
echo "🚀 Orchestrating Docker Containers..."
if [ "$STAGE" = "production" ]; then
    docker-compose -f docker-compose.soc.yml up -d
else
    docker-compose -f docker-compose.staging.yml up -d
fi

echo "✅ Sentinel IRONCLAD Deployment Complete."
if [ -n "$BRIDGE_PID" ]; then
    echo "[warning] Remember to kill socat (PID: $BRIDGE_PID) when finished."
fi

echo "
Status Check:
- Initramfs: $PROJECT_ROOT/initramfs.cpio.gz
- Dashboards: http://localhost:3000
- SOC Portal: http://localhost:5678 (n8n)
"
