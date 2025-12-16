#!/bin/bash
#
# Test Enhanced Backup System
# Quick validation script
#

set -e

echo "========================================="
echo "Sentinel Backup System - Quick Test"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if backup script exists
echo -n "1. Checking backup script exists... "
if [ -f "/home/jnovoas/sentinel/scripts/backup-postgres.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "   Script not found!"
    exit 1
fi

# Test 2: Check if script is executable
echo -n "2. Checking script is executable... "
if [ -x "/home/jnovoas/sentinel/scripts/backup-postgres.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} Making executable..."
    chmod +x /home/jnovoas/sentinel/scripts/backup-postgres.sh
    echo -e "   ${GREEN}✓${NC} Fixed"
fi

# Test 3: Check if backup directory exists
echo -n "3. Checking backup directory... "
if [ -d "/var/backups/sentinel/postgres" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} Creating directory..."
    sudo mkdir -p /var/backups/sentinel/postgres
    echo -e "   ${GREEN}✓${NC} Created"
fi

# Test 4: Check if PostgreSQL container is running
echo -n "4. Checking PostgreSQL container... "
if docker ps | grep -q "sentinel-postgres"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "   PostgreSQL container not running!"
    echo "   Start with: docker-compose up -d postgres"
    exit 1
fi

# Test 5: Create test table
echo -n "5. Creating test data... "
docker exec sentinel-postgres psql -U sentinel -c \
    "CREATE TABLE IF NOT EXISTS test_backup (
        id SERIAL PRIMARY KEY,
        data TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );" > /dev/null 2>&1

docker exec sentinel-postgres psql -U sentinel -c \
    "INSERT INTO test_backup (data) VALUES ('test-$(date +%s)');" > /dev/null 2>&1

echo -e "${GREEN}✓${NC}"

# Test 6: Run backup
echo ""
echo "6. Running backup (this may take 10-30 seconds)..."
echo "   ----------------------------------------"
/home/jnovoas/sentinel/scripts/backup-postgres.sh
BACKUP_EXIT_CODE=$?
echo "   ----------------------------------------"

if [ $BACKUP_EXIT_CODE -eq 0 ]; then
    echo -e "   ${GREEN}✓${NC} Backup completed successfully"
else
    echo -e "   ${RED}✗${NC} Backup failed!"
    exit 1
fi

# Test 7: Verify backup file exists
echo -n "7. Verifying backup file created... "
LATEST_BACKUP=$(ls -t /var/backups/sentinel/postgres/sentinel_backup_*.sql.gz* 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
    echo -e "${GREEN}✓${NC} ($BACKUP_SIZE)"
    echo "   File: $(basename $LATEST_BACKUP)"
else
    echo -e "${RED}✗${NC}"
    echo "   No backup file found!"
    exit 1
fi

# Test 8: Verify backup integrity
echo -n "8. Verifying backup integrity... "
if gunzip -t "$LATEST_BACKUP" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "   Backup file is corrupted!"
    exit 1
fi

# Test 9: Check AWS CLI (optional)
echo -n "9. Checking AWS CLI (optional)... "
if command -v aws &> /dev/null; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${YELLOW}⚠${NC} Not installed (S3 backups disabled)"
fi

# Test 10: Check MinIO CLI (optional)
echo -n "10. Checking MinIO CLI (optional)... "
if command -v mc &> /dev/null; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${YELLOW}⚠${NC} Not installed (MinIO backups disabled)"
fi

# Summary
echo ""
echo "========================================="
echo "Summary"
echo "========================================="
echo "Backup directory: /var/backups/sentinel/postgres"
echo "Latest backup: $(basename $LATEST_BACKUP)"
echo "Backup size: $BACKUP_SIZE"
echo "Total backups: $(ls -1 /var/backups/sentinel/postgres/ 2>/dev/null | wc -l)"
echo ""
echo -e "${GREEN}✓ All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Configure S3/MinIO (optional): docs/BACKUP_SETUP_GUIDE.md"
echo "2. Configure webhook alerts (optional): docs/BACKUP_SETUP_GUIDE.md"
echo "3. Configure encryption (optional): docs/BACKUP_SETUP_GUIDE.md"
echo "4. Setup cron job: crontab -e"
echo "   Add: 0 */6 * * * /home/jnovoas/sentinel/scripts/backup-postgres.sh >> /var/log/sentinel-backup.log 2>&1"
echo ""
