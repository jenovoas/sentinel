#!/usr/bin/env bash
# minio_deploy.sh - Deploy MinIO distributed cluster
# Usage: ./minio_deploy.sh
# Run on ALL nodes simultaneously

set -euo pipefail

MINIO_VERSION="latest"
MINIO_USER="minioadmin"
MINIO_PASS="minioadmin"
DATA_DIR="/data"

echo "🗄️ MinIO Distributed Deployment"
echo "================================"

# Download MinIO binary
if [ ! -f /usr/local/bin/minio ]; then
    echo "📥 Downloading MinIO..."
    wget -q https://dl.min.io/server/minio/release/linux-arm64/minio -O /tmp/minio
    chmod +x /tmp/minio
    sudo mv /tmp/minio /usr/local/bin/
    echo "✅ MinIO installed"
else
    echo "✅ MinIO already installed"
fi

# Create data directory
echo "📁 Creating data directory: $DATA_DIR"
sudo mkdir -p $DATA_DIR
sudo chown $(whoami):$(whoami) $DATA_DIR

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/minio.service > /dev/null <<EOF
[Unit]
Description=MinIO Distributed Object Storage
After=network.target

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
Environment="MINIO_ROOT_USER=$MINIO_USER"
Environment="MINIO_ROOT_PASSWORD=$MINIO_PASS"
ExecStart=/usr/local/bin/minio server http://n{1...4}:9000/data{1...4}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting MinIO service..."
sudo systemctl daemon-reload
sudo systemctl enable minio
sudo systemctl start minio

# Wait for startup
echo "⏳ Waiting for MinIO to start..."
sleep 5

# Check status
echo ""
echo "📊 Service status:"
sudo systemctl status minio --no-pager | head -10

echo ""
echo "✅ MinIO deployment complete!"
echo ""
echo "🌐 Access:"
echo "   Console: http://$(hostname -I | awk '{print $1}'):9000"
echo "   User: $MINIO_USER"
echo "   Pass: $MINIO_PASS"
echo ""
echo "📝 Next steps:"
echo "   1. Install mc client: wget https://dl.min.io/client/mc/release/linux-arm64/mc"
echo "   2. Configure alias: mc alias set mycnet http://n1:9000 $MINIO_USER $MINIO_PASS"
echo "   3. Create bucket: mc mb mycnet/test"
echo "   4. Test upload: mc cp /tmp/file.bin mycnet/test/"
