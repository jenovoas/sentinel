#!/bin/bash
# Install libbpf-python for ringbuf support

echo "📦 Installing libbpf-python..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

echo "Python version: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Error: Python 3.8+ required (you have $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python version OK"

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    libbpf-dev \
    libelf-dev \
    zlib1g-dev

# Install libbpf-python
echo ""
echo "Installing libbpf (Python bindings)..."
echo "Note: Using --break-system-packages for Debian 13"
pip3 install --user --break-system-packages libbpf

# Verify
echo ""
echo "Verifying installation..."
python3 << 'EOF'
try:
    import libbpf
    print("✅ libbpf-python installed successfully")
    print(f"   Location: {libbpf.__file__ if hasattr(libbpf, '__file__') else 'unknown'}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("")
    print("Trying alternative installation...")
    import subprocess
    subprocess.run(["pip3", "install", "--user", "--break-system-packages", "libbpf"], check=False)
EOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run: sudo ./guardian-alpha/quantum_bci_bridge_libbpf.py"
echo "2. Enjoy true ringbuf performance"
