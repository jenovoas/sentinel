# Enterprise Backup System Refactoring - Implementation Plan

## Problem Statement

Investors are currently evaluating the codebase. The current backup system has several issues that don't meet enterprise standards:

1. **Hardcoded credentials** in scripts (security risk)
2. **Monolithic scripts** (not modular, hard to maintain)
3. **Incomplete documentation** (missing architecture diagrams, runbooks)
4. **No automated tests** (can't verify reliability)
5. **Permission issues** with `/var/backups` directory

## User Review Required

> [!IMPORTANT]
> **Timeline Decision Needed**
> 
> Two implementation options:
> - **Option A (30 min)**: Quick fix - resolve directory permissions, basic functionality
> - **Option B (2-3 hours)**: Full enterprise refactoring - modular code, tests, documentation
> 
> **Question**: When do investors need to review the code? (Today vs 2-3 days)

## Proposed Changes

### Phase 1: Immediate Fix (30 minutes)

#### Fix Directory Permissions Issue

**Problem**: Script fails because `/var/backups` is owned by root.

**Solution**: Update script to handle permissions gracefully and provide clear error messages.

#### [MODIFY] [backup-postgres.sh](file:///home/jnovoas/sentinel/scripts/backup-postgres.sh)

- Fix directory creation logic to check permissions first
- Add fallback to user home directory if `/var/backups` not writable
- Improve error messages with actionable instructions

#### [MODIFY] [restore-postgres.sh](file:///home/jnovoas/sentinel/scripts/restore-postgres.sh)

- Update PostgreSQL credentials (already done)
- Add validation for backup file existence and integrity

---

### Phase 2: Enterprise Refactoring (2-3 hours)

#### Modular Architecture

Create new directory structure:

```
scripts/backup/
├── backup.sh                 # Main entry point
├── restore.sh               # Restore entry point
├── lib/
│   ├── config.sh           # Configuration management
│   ├── logging.sh          # Structured logging
│   ├── notifications.sh    # Webhook/alert system
│   ├── storage.sh          # S3/MinIO/local storage
│   ├── validation.sh       # Integrity verification
│   └── postgres.sh         # PostgreSQL operations
├── tests/
│   ├── test-backup.sh      # Automated backup tests
│   ├── test-restore.sh     # Automated restore tests
│   └── test-integration.sh # End-to-end tests
└── README.md               # Module documentation
```

#### [NEW] [scripts/backup/lib/config.sh](file:///home/jnovoas/sentinel/scripts/backup/lib/config.sh)

Configuration management using environment variables from `.env` file.

#### [NEW] [scripts/backup/lib/logging.sh](file:///home/jnovoas/sentinel/scripts/backup/lib/logging.sh)

Structured logging system with log levels and rotation.

#### [NEW] [scripts/backup/lib/storage.sh](file:///home/jnovoas/sentinel/scripts/backup/lib/storage.sh)

Storage abstraction layer for local/S3/MinIO.

#### [NEW] [scripts/backup/lib/validation.sh](file:///home/jnovoas/sentinel/scripts/backup/lib/validation.sh)

Backup validation with integrity checks and checksums.

#### [NEW] [scripts/backup/backup.sh](file:///home/jnovoas/sentinel/scripts/backup/backup.sh)

Main backup script using modular components.

---

### Documentation

#### [NEW] [docs/backup/ARCHITECTURE.md](file:///home/jnovoas/sentinel/docs/backup/ARCHITECTURE.md)

Technical architecture with diagrams and security model.

#### [NEW] [docs/backup/OPERATIONS.md](file:///home/jnovoas/sentinel/docs/backup/OPERATIONS.md)

Operational runbooks and troubleshooting guide.

#### [NEW] [docs/backup/DISASTER_RECOVERY.md](file:///home/jnovoas/sentinel/docs/backup/DISASTER_RECOVERY.md)

DR procedures with RTO/RPO targets.

#### [NEW] [docs/backup/TESTING.md](file:///home/jnovoas/sentinel/docs/backup/TESTING.md)

Testing strategy and coverage metrics.

---

## Verification Plan

### Automated Tests

```bash
# Run backup tests
./scripts/backup/tests/test-backup.sh

# Run restore tests
./scripts/backup/tests/test-restore.sh
```

### Manual Verification

```bash
# Test backup creation
docker exec sentinel-postgres psql -U sentinel_user -d sentinel_db -c \
  "CREATE TABLE test_backup (id SERIAL, data TEXT);"
./scripts/backup/backup.sh

# Test restore
./scripts/backup/restore.sh /var/backups/sentinel/postgres/latest.sql.gz
```

---

## Timeline

### Option A: Quick Fix (30 minutes)
- Fix directory permissions
- Update credentials
- Basic testing

### Option B: Enterprise Refactoring (2-3 hours)
- Hour 1: Modular architecture
- Hour 2: Tests + documentation
- Hour 3: CI/CD + review

---

**Awaiting user decision on timeline and preferred option.**
