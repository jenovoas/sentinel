# Sentinel Backup System

Enterprise-grade PostgreSQL backup system with modular architecture, comprehensive validation, and multi-destination support.

## Features

- ✅ **Modular Architecture** - Clean separation of concerns (config, logging, validation, notifications)
- ✅ **Environment-Based Configuration** - No hardcoded credentials, all configuration via `.env`
- ✅ **Comprehensive Validation** - Integrity checks, checksums (SHA256), size validation
- ✅ **Multi-Destination Support** - Local, S3, and MinIO storage
- ✅ **Optional Encryption** - AES-256-CBC encryption for sensitive backups
- ✅ **Structured Logging** - Multiple log levels (DEBUG, INFO, WARN, ERROR) with file and stdout output
- ✅ **Webhook Notifications** - Slack/Discord integration for backup events
- ✅ **Automatic Cleanup** - Configurable retention policy for old backups
- ✅ **Detailed Documentation** - Comprehensive inline comments and external docs

## Quick Start

### 1. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env

# Minimum required settings:
POSTGRES_CONTAINER=sentinel-postgres
POSTGRES_USER=sentinel_user
POSTGRES_DB=sentinel_db
BACKUP_DIR=/var/backups/sentinel/postgres
```

### 2. Create Backup Directory

```bash
sudo mkdir -p /var/backups/sentinel/postgres
sudo chown -R $USER:$USER /var/backups/sentinel
```

### 3. Run Backup

```bash
cd /home/jnovoas/sentinel
./scripts/backup/backup.sh
```

## Configuration

All configuration is done via environment variables. See [`.env.example`](../../.env.example) for all available options.

### Required Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_CONTAINER` | PostgreSQL container name | `sentinel-postgres` |
| `POSTGRES_USER` | PostgreSQL user | `sentinel_user` |
| `POSTGRES_DB` | PostgreSQL database | `sentinel_db` |
| `BACKUP_DIR` | Backup directory path | `/var/backups/sentinel/postgres` |

### Optional Configuration

#### S3 Storage

```bash
S3_ENABLED=true
S3_BUCKET=s3://sentinel-backups/postgres
S3_STORAGE_CLASS=STANDARD_IA
S3_REGION=us-east-1
```

#### Encryption

```bash
# Generate encryption key
openssl rand -base64 32 > /etc/sentinel/backup.key
chmod 600 /etc/sentinel/backup.key

# Enable in .env
ENCRYPT_ENABLED=true
ENCRYPTION_KEY_PATH=/etc/sentinel/backup.key
```

#### Notifications

```bash
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
NOTIFICATION_LEVEL=all  # all, error, none
```

## Architecture

### Module Structure

```
scripts/backup/
├── backup.sh              # Main backup script
├── lib/
│   ├── config.sh         # Configuration management
│   ├── logging.sh        # Structured logging
│   ├── notifications.sh  # Webhook notifications
│   └── validation.sh     # Backup validation
├── tests/
│   ├── test-backup.sh    # Automated tests
│   └── test-restore.sh   # Restore tests
└── README.md             # This file
```

### Data Flow

```
┌─────────────────┐
│  Load Config    │ ← .env file
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Backup  │ ← PostgreSQL
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validate       │ ← Integrity + Checksum
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────┐  ┌─────────────┐
│  Upload S3  │  │ Upload MinIO│
└─────────────┘  └─────────────┘
         │              │
         └──────┬───────┘
                │
                ▼
         ┌─────────────┐
         │   Cleanup   │
         └─────────────┘
                │
                ▼
         ┌─────────────┐
         │   Notify    │ ← Webhook
         └─────────────┘
```

## Usage Examples

### Basic Backup

```bash
./scripts/backup/backup.sh
```

### Backup with Debug Logging

```bash
LOG_LEVEL=DEBUG ./scripts/backup/backup.sh
```

### Backup to S3

```bash
S3_ENABLED=true ./scripts/backup/backup.sh
```

### Encrypted Backup

```bash
ENCRYPT_ENABLED=true ./scripts/backup/backup.sh
```

### Automated Backups (Cron)

```bash
# Edit crontab
crontab -e

# Add line for backups every 6 hours
0 */6 * * * /home/jnovoas/sentinel/scripts/backup/backup.sh >> /var/log/sentinel-backup.log 2>&1

# Or daily at 3 AM
0 3 * * * /home/jnovoas/sentinel/scripts/backup/backup.sh >> /var/log/sentinel-backup.log 2>&1
```

## Validation

All backups are automatically validated with:

1. **Integrity Check** - Verifies gzip/encryption integrity
2. **Checksum** - Generates SHA256 checksum for verification
3. **Size Validation** - Ensures backup is not suspiciously small

Validation results are logged and included in notifications.

## Monitoring

### Log Files

```bash
# View backup logs
tail -f /var/log/sentinel-backup.log

# View recent backups
grep "Backup process completed" /var/log/sentinel-backup.log

# View errors
grep "ERROR" /var/log/sentinel-backup.log
```

### Backup Status

```bash
# List backups
ls -lh /var/backups/sentinel/postgres/

# Check latest backup
ls -lt /var/backups/sentinel/postgres/ | head -2

# Verify backup integrity
gunzip -t /var/backups/sentinel/postgres/sentinel_backup_*.sql.gz
```

## Troubleshooting

### Permission Denied

```bash
# Fix backup directory permissions
sudo chown -R $USER:$USER /var/backups/sentinel
sudo chmod -R 755 /var/backups/sentinel
```

### Encryption Key Not Found

```bash
# Generate encryption key
sudo mkdir -p /etc/sentinel
sudo openssl rand -base64 32 > /etc/sentinel/backup.key
sudo chmod 600 /etc/sentinel/backup.key
```

### S3 Upload Failed

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://sentinel-backups/

# Check bucket permissions
aws s3api get-bucket-acl --bucket sentinel-backups
```

### Webhook Not Working

```bash
# Test webhook manually
curl -X POST "$WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from Sentinel"}'
```

## Testing

```bash
# Run automated tests
./scripts/backup/tests/test-backup.sh

# Run restore tests
./scripts/backup/tests/test-restore.sh
```

## Security Best Practices

1. **Encryption** - Always enable encryption for production backups
2. **Key Management** - Store encryption keys securely (not in git)
3. **Access Control** - Restrict backup directory permissions (700 or 750)
4. **Off-Site Storage** - Use S3/MinIO for disaster recovery
5. **Monitoring** - Enable webhook notifications for failures
6. **Testing** - Regularly test restore procedures

## Performance

### Backup Size

Typical backup sizes (compressed):
- Small database (<1GB): 50-100MB
- Medium database (1-10GB): 100MB-1GB
- Large database (>10GB): 1GB+

### Backup Duration

Typical backup times:
- Small database: 10-30 seconds
- Medium database: 1-5 minutes
- Large database: 5-30 minutes

### Optimization Tips

1. **Compression Level** - Default is 9 (maximum), reduce to 6 for faster backups
2. **Parallel Backups** - Use `pg_dump --jobs=N` for large databases
3. **Incremental Backups** - Consider WAL archiving for very large databases

## Migration from Old System

If you have the old backup system:

```bash
# Old scripts are still in scripts/ directory
# New system is in scripts/backup/

# To migrate:
1. Configure .env with backup settings
2. Test new system: ./scripts/backup/backup.sh
3. Verify backups work
4. Update cron jobs to use new script
5. Archive old scripts: mv scripts/backup-postgres.sh scripts/backup-postgres.sh.old
```

## Support

For issues or questions:
1. Check logs: `/var/log/sentinel-backup.log`
2. Review documentation: `docs/backup/`
3. Run tests: `./scripts/backup/tests/test-backup.sh`
4. Contact: [Your support channel]

## License

Part of the Sentinel project. See main LICENSE file.
