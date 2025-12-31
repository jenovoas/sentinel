#!/bin/bash
# Sentinel Cortex - Debian 13 "Trixie" Trajectory (Phase 10 preparation)
# Objective: Upgrade to Trixie for Kernel 6.12 + ROP/JOP Hardening

echo "🚀 Starting Debian 13 Trixie Trajectory..."

# 1. Add Trixie sources
cat <<EOF | sudo tee /etc/apt/sources.list.d/trixie.list
deb http://deb.debian.org/debian trixie main contrib non-free
deb http://security.debian.org/debian-security trixie-security main
EOF

echo "✅ Trixie sources added."

# 2. Update and Upgrade (Optional: user should run manually to monitor)
echo "💡 To complete the upgrade, run:"
echo "   sudo apt update && sudo apt full-upgrade -y"
echo "   sudo apt install linux-image-6.12.0-1-amd64"
echo "   sudo update-grub"

# 3. Verify Hardware Mitigation context
echo "🔍 Kernel 6.12 ROP/JOP Mitigations will be active automatically."
echo "   Check with: cat /proc/cmdline | grep 'mitigations=auto,nosmt'"

echo "🎯 Trajectory Prepared."
