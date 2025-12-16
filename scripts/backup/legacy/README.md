# Legacy Backup Scripts

**⚠️ DEPRECATED - These scripts are no longer maintained**

The old backup scripts have been replaced with a new enterprise-grade modular system.

## Old Scripts

- `backup-postgres.sh` - Old backup script (monolithic)
- `restore-postgres.sh` - Old restore script

## Migration to New System

The new backup system is located in `/scripts/backup/` and provides:

- ✅ Modular architecture
- ✅ Environment-based configuration (no hardcoding)
- ✅ Comprehensive validation
- ✅ Multi-destination support (S3, MinIO)
- ✅ Optional encryption
- ✅ Webhook notifications
- ✅ Automated tests

### Quick Migration Steps

1. **Configure environment**:
   ```bash
   # Add to .env file
   POSTGRES_CONTAINER=sentinel-postgres
   POSTGRES_USER=sentinel_user
   POSTGRES_DB=sentinel_db
   BACKUP_DIR=/var/backups/sentinel/postgres
   ```

2. **Test new system**:
   ```bash
   ./scripts/backup/backup.sh
   ```

3. **Update cron jobs**:
   ```bash
   # Old:
   # 0 */6 * * * /path/to/scripts/backup-postgres.sh
   
   # New:
   0 */6 * * * /path/to/scripts/backup/backup.sh >> /var/log/sentinel-backup.log 2>&1
   ```

4. **Verify backups**:
   ```bash
   ls -lh /var/backups/sentinel/postgres/
   ```

## Why Migrate?

| Feature | Old System | New System |
|---------|------------|------------|
| Configuration | Hardcoded | Environment variables |
| Validation | Basic | Comprehensive (integrity + checksum) |
| Storage | Local only | Local + S3 + MinIO |
| Encryption | No | Yes (AES-256) |
| Notifications | No | Yes (Slack/Discord) |
| Logging | Basic | Structured (multiple levels) |
| Tests | No | Yes (automated) |
| Documentation | Minimal | Comprehensive |

## Support

For questions about migration, see:
- New system README: `/scripts/backup/README.md`
- Documentation: `/docs/backup/`
- Tests: `/scripts/backup/tests/`

## Removal Timeline

These legacy scripts will be removed in a future release. Please migrate as soon as possible.
