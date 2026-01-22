#!/usr/bin/env bash
# mesh_setup.sh - Setup batman-adv mesh interface
# Usage: ./mesh_setup.sh <node_number>
# Example: ./mesh_setup.sh 1  (configures n1 with IP 10.10.0.11)

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <node_number>"
    echo "Example: $0 1  (for node n1)"
    exit 1
fi

NODE_NUM=$1
NODE_IP="10.10.0.1$NODE_NUM"
IFACE="eth1"  # Physical interface (adjust if needed)

echo "🔧 Setting up batman-adv mesh for node n$NODE_NUM"
echo "   IP: $NODE_IP/24"
echo "   Interface: $IFACE"

# Load batman-adv module
echo "📦 Loading batman-adv kernel module..."
sudo modprobe batman-adv

# Bring up physical interface
echo "🔌 Bringing up $IFACE..."
sudo ip link set up dev $IFACE

# Add interface to batman-adv
echo "🦇 Adding $IFACE to batman-adv..."
sudo batctl if add $IFACE

# Bring up bat0
echo "🌐 Bringing up bat0..."
sudo ip link set up dev bat0

# Assign IP to bat0
echo "📍 Assigning IP $NODE_IP to bat0..."
sudo ip addr flush dev bat0
sudo ip addr add $NODE_IP/24 dev bat0

# Verify
echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Status:"
batctl if
echo ""
echo "👥 Neighbors (wait a few seconds for discovery):"
batctl n

echo ""
echo "🧪 Test connectivity:"
echo "   ping 10.10.0.11  # n1"
echo "   ping 10.10.0.12  # n2"
echo "   ..."
