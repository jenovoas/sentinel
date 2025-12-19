#!/bin/bash
# Security Quick Fix Script for Sentinel Cortex
# Run this to fix the most critical security issues

set -e

echo "🔒 Sentinel Cortex - Security Quick Fix"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Generate strong SECRET_KEY
echo -e "${YELLOW}[1/6]${NC} Generating strong SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "✅ Generated: ${SECRET_KEY:0:20}..."

# 2. Generate strong N8N_ENCRYPTION_KEY
echo -e "${YELLOW}[2/6]${NC} Generating N8N encryption key..."
N8N_KEY=$(openssl rand -hex 32)
echo "✅ Generated: ${N8N_KEY:0:20}..."

# 3. Generate strong passwords
echo -e "${YELLOW}[3/6]${NC} Generating strong passwords..."
POSTGRES_PASS=$(openssl rand -base64 24)
GRAFANA_PASS=$(openssl rand -base64 24)
N8N_PASS=$(openssl rand -base64 24)
METRICS_PASS=$(openssl rand -base64 16)
LOGS_PASS=$(openssl rand -base64 16)
MINIO_ACCESS=$(openssl rand -base64 16)
MINIO_SECRET=$(openssl rand -base64 24)

echo "✅ Generated all passwords"

# 4. Backup existing .env if it exists
if [ -f .env ]; then
    echo -e "${YELLOW}[4/6]${NC} Backing up existing .env..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
else
    echo -e "${YELLOW}[4/6]${NC} No existing .env found, will create new one"
fi

# 5. Create secure .env file
echo -e "${YELLOW}[5/6]${NC} Creating secure .env file..."
cat > .env << EOF
# Sentinel Observability Stack - PRODUCTION Environment
# Generated: $(date)
# ⚠️ NEVER COMMIT THIS FILE TO VERSION CONTROL

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=${GRAFANA_PASS}

# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_USER=admin
N8N_PASSWORD=${N8N_PASS}
N8N_HOST=localhost
DB_SQLITE_POOL_SIZE=5
N8N_RUNNERS_ENABLED=true
N8N_BLOCK_ENV_ACCESS_IN_NODE=false
N8N_GIT_NODE_DISABLE_BARE_REPOS=true
N8N_ENCRYPTION_KEY=${N8N_KEY}

# n8n Integrations (configure with your actual values)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USER=your-user
SMTP_PASS=your-smtp-password-here
SMTP_FROM=alerts@your-domain.com
SMTP_TO=recipient@your-domain.com
SMTP_SECURE=false

# PostgreSQL Configuration
POSTGRES_USER=sentinel_user
POSTGRES_PASSWORD=${POSTGRES_PASS}
POSTGRES_DB=sentinel_db

# Backend Configuration
DATABASE_URL=postgresql+asyncpg://sentinel_user:${POSTGRES_PASS}@postgres:5432/sentinel_db
REDIS_URL=redis://redis:6379/0
FASTAPI_ENV=production
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=https://your-production-domain.com
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
LOG_LEVEL=INFO

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NODE_ENV=production

# Ollama AI Configuration
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=phi3:mini
AI_ENABLED=true
OLLAMA_TIMEOUT=8
OLLAMA_NUM_PREDICT=100
OLLAMA_TEMPERATURE=0.3

# Backup System Configuration
POSTGRES_CONTAINER=sentinel-postgres
BACKUP_DIR=/var/backups/sentinel/postgres
BACKUP_RETENTION_DAYS=7
BACKUP_COMPRESSION_LEVEL=9

# S3 Configuration (optional)
S3_ENABLED=false
S3_BUCKET=s3://sentinel-backups/postgres
S3_STORAGE_CLASS=STANDARD_IA
S3_REGION=us-east-1

# MinIO Configuration (optional)
MINIO_ENABLED=false
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET=sentinel-backups
MINIO_ACCESS_KEY=${MINIO_ACCESS}
MINIO_SECRET_KEY=${MINIO_SECRET}

# Encryption (optional)
ENCRYPT_ENABLED=false
ENCRYPTION_KEY_PATH=/etc/sentinel/backup.key
ENCRYPTION_ALGORITHM=aes-256-cbc

# Notifications (optional)
WEBHOOK_ENABLED=false
NOTIFICATION_LEVEL=error

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/sentinel-backup.log
LOG_TO_FILE=true
LOG_TO_STDOUT=true

# Observability Authentication
OBSERVABILITY_METRICS_PASSWORD=${METRICS_PASS}
OBSERVABILITY_LOGS_PASSWORD=${LOGS_PASS}

# Telemetry Sanitization
TELEMETRY_SANITIZATION_ENABLED=true
EOF

echo "✅ Secure .env created"

# 6. Fix docker-compose.n8n.yml
echo -e "${YELLOW}[6/6]${NC} Fixing docker-compose.n8n.yml..."
if [ -f docker-compose.n8n.yml ]; then
    # Backup
    cp docker-compose.n8n.yml docker-compose.n8n.yml.backup
    
    # Replace hardcoded values with env vars
    sed -i 's/N8N_BASIC_AUTH_PASSWORD=sentinel_n8n_2024/N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-changeme}/' docker-compose.n8n.yml
    sed -i 's/N8N_ENCRYPTION_KEY=sentinel_encryption_key_change_in_production/N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY:-changeme}/' docker-compose.n8n.yml
    
    echo "✅ Fixed docker-compose.n8n.yml"
else
    echo "⚠️  docker-compose.n8n.yml not found, skipping"
fi

# Summary
echo ""
echo "========================================"
echo -e "${GREEN}✅ Security fixes applied!${NC}"
echo "========================================"
echo ""
echo "📋 IMPORTANT NEXT STEPS:"
echo ""
echo "1. Review the generated .env file and update:"
echo "   - ALLOWED_ORIGINS with your production domain"
echo "   - SMTP settings with your actual email provider"
echo "   - NEXT_PUBLIC_API_URL with your API domain"
echo ""
echo "2. Store these credentials securely:"
echo "   - Use a password manager (1Password, LastPass, etc.)"
echo "   - Or use a secrets manager (HashiCorp Vault, AWS Secrets Manager)"
echo ""
echo "3. Update docker-compose.yml to bind ports to localhost:"
echo "   - Change '5432:5432' to '127.0.0.1:5432:5432'"
echo "   - Change '6379:6379' to '127.0.0.1:6379:6379'"
echo "   - Remove public port mappings for metrics (9090, 3100, etc.)"
echo ""
echo "4. Disable Prometheus admin API in docker-compose.yml:"
echo "   - Remove '--web.enable-admin-api' flag"
echo ""
echo "5. For production, disable Grafana anonymous access:"
echo "   - Set GF_AUTH_ANONYMOUS_ENABLED: \"false\""
echo ""
echo "6. Review full security report:"
echo "   - See SECURITY_AUDIT_REPORT.md for all details"
echo ""
echo "🔐 Generated Credentials (SAVE THESE SECURELY):"
echo "================================================"
echo "PostgreSQL Password: ${POSTGRES_PASS}"
echo "Grafana Password:    ${GRAFANA_PASS}"
echo "n8n Password:        ${N8N_PASS}"
echo "Metrics Password:    ${METRICS_PASS}"
echo "Logs Password:       ${LOGS_PASS}"
echo "MinIO Access Key:    ${MINIO_ACCESS}"
echo "MinIO Secret Key:    ${MINIO_SECRET}"
echo "SECRET_KEY:          ${SECRET_KEY}"
echo "N8N_ENCRYPTION_KEY:  ${N8N_KEY}"
echo ""
echo "⚠️  SAVE THESE CREDENTIALS NOW - They won't be shown again!"
echo ""
