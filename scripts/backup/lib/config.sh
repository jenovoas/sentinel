#!/bin/bash
#
# Sentinel Backup System - Configuration Module
# 
# This module handles all configuration management for the backup system.
# It loads configuration from environment variables and .env files,
# validates required settings, and provides sensible defaults.
#
# Usage:
#   source "$(dirname "$0")/lib/config.sh"
#   load_config
#
# Environment Variables:
#   See .env.example for full list of configuration options
#

set -euo pipefail

# ============================================================================
# CONSTANTS
# ============================================================================

# Use SCRIPT_DIR if already set (from parent script), otherwise calculate it
if [[ -z "${SCRIPT_DIR:-}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly PROJECT_ROOT
readonly DEFAULT_BACKUP_DIR="/var/backups/sentinel/postgres"
readonly DEFAULT_RETENTION_DAYS=7

# ============================================================================
# CONFIGURATION VARIABLES
# ============================================================================

# PostgreSQL Configuration
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-}"
POSTGRES_USER="${POSTGRES_USER:-}"
POSTGRES_DB="${POSTGRES_DB:-}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

# Backup Configuration
BACKUP_DIR="${BACKUP_DIR:-}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-}"
BACKUP_COMPRESSION_LEVEL="${BACKUP_COMPRESSION_LEVEL:-9}"

# S3 Configuration
S3_ENABLED="${S3_ENABLED:-false}"
S3_BUCKET="${S3_BUCKET:-}"
S3_STORAGE_CLASS="${S3_STORAGE_CLASS:-STANDARD_IA}"
S3_REGION="${S3_REGION:-us-east-1}"

# MinIO Configuration
MINIO_ENABLED="${MINIO_ENABLED:-false}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-}"
MINIO_BUCKET="${MINIO_BUCKET:-}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-}"

# Encryption Configuration
ENCRYPT_ENABLED="${ENCRYPT_ENABLED:-false}"
ENCRYPTION_KEY_PATH="${ENCRYPTION_KEY_PATH:-/etc/sentinel/backup.key}"
ENCRYPTION_ALGORITHM="${ENCRYPTION_ALGORITHM:-aes-256-cbc}"

# Notification Configuration
WEBHOOK_URL="${WEBHOOK_URL:-}"
WEBHOOK_ENABLED="${WEBHOOK_ENABLED:-false}"
NOTIFICATION_LEVEL="${NOTIFICATION_LEVEL:-error}"  # all, error, none

# Logging Configuration
LOG_LEVEL="${LOG_LEVEL:-INFO}"  # DEBUG, INFO, WARN, ERROR
LOG_FILE="${LOG_FILE:-/var/log/sentinel-backup.log}"
LOG_TO_FILE="${LOG_TO_FILE:-true}"
LOG_TO_STDOUT="${LOG_TO_STDOUT:-true}"

# ============================================================================
# FUNCTIONS
# ============================================================================

#
# Load configuration from .env file
#
# Searches for .env file in project root and loads all variables.
# Does not override existing environment variables.
#
load_env_file() {
    local env_file="$PROJECT_ROOT/.env"
    
    if [[ -f "$env_file" ]]; then
        # Load .env file, ignoring comments and empty lines
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ "$key" =~ ^#.*$ ]] && continue
            [[ -z "$key" ]] && continue
            
            # Remove quotes from value
            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"
            
            # Export variable if not already set
            if [[ -z "${!key:-}" ]]; then
                export "$key=$value"
            fi
        done < <(grep -v '^#' "$env_file" | grep -v '^$')
    fi
}

#
# Validate required configuration
#
# Checks that all required configuration variables are set.
# Exits with error if any required variable is missing.
#
validate_config() {
    local errors=0
    
    # Required PostgreSQL configuration
    if [[ -z "$POSTGRES_CONTAINER" ]]; then
        echo "ERROR: POSTGRES_CONTAINER is not set" >&2
        ((errors++))
    fi
    
    if [[ -z "$POSTGRES_USER" ]]; then
        echo "ERROR: POSTGRES_USER is not set" >&2
        ((errors++))
    fi
    
    if [[ -z "$POSTGRES_DB" ]]; then
        echo "ERROR: POSTGRES_DB is not set" >&2
        ((errors++))
    fi
    
    # Validate backup directory
    if [[ -z "$BACKUP_DIR" ]]; then
        echo "ERROR: BACKUP_DIR is not set" >&2
        ((errors++))
    fi
    
    # Validate S3 configuration if enabled
    if [[ "$S3_ENABLED" == "true" ]]; then
        if [[ -z "$S3_BUCKET" ]]; then
            echo "ERROR: S3_ENABLED is true but S3_BUCKET is not set" >&2
            ((errors++))
        fi
    fi
    
    # Validate MinIO configuration if enabled
    if [[ "$MINIO_ENABLED" == "true" ]]; then
        if [[ -z "$MINIO_ENDPOINT" ]] || [[ -z "$MINIO_BUCKET" ]]; then
            echo "ERROR: MINIO_ENABLED is true but MINIO_ENDPOINT or MINIO_BUCKET is not set" >&2
            ((errors++))
        fi
    fi
    
    # Validate encryption configuration if enabled
    if [[ "$ENCRYPT_ENABLED" == "true" ]]; then
        if [[ ! -f "$ENCRYPTION_KEY_PATH" ]]; then
            echo "ERROR: ENCRYPT_ENABLED is true but encryption key not found at $ENCRYPTION_KEY_PATH" >&2
            echo "Generate key with: openssl rand -base64 32 > $ENCRYPTION_KEY_PATH" >&2
            ((errors++))
        fi
    fi
    
    if [[ $errors -gt 0 ]]; then
        echo "ERROR: Configuration validation failed with $errors error(s)" >&2
        return 1
    fi
    
    return 0
}

#
# Set default values for optional configuration
#
set_defaults() {
    # Set backup directory default
    if [[ -z "$BACKUP_DIR" ]]; then
        BACKUP_DIR="$DEFAULT_BACKUP_DIR"
    fi
    
    # Set retention days default
    if [[ -z "$BACKUP_RETENTION_DAYS" ]]; then
        BACKUP_RETENTION_DAYS="$DEFAULT_RETENTION_DAYS"
    fi
    
    # Enable webhook if URL is set
    if [[ -n "$WEBHOOK_URL" ]] && [[ "$WEBHOOK_ENABLED" != "true" ]]; then
        WEBHOOK_ENABLED="true"
    fi
}

#
# Main configuration loading function
#
# Call this function to load and validate all configuration.
# This is the main entry point for the config module.
#
load_config() {
    # Load .env file
    load_env_file
    
    # Set defaults
    set_defaults
    
    # Validate configuration
    if ! validate_config; then
        echo "ERROR: Configuration validation failed" >&2
        echo "Please check your .env file or environment variables" >&2
        return 1
    fi
    
    return 0
}

# ============================================================================
# EXPORTS
# ============================================================================

# Export all configuration variables
export POSTGRES_CONTAINER POSTGRES_USER POSTGRES_DB POSTGRES_HOST POSTGRES_PORT
export BACKUP_DIR BACKUP_RETENTION_DAYS BACKUP_COMPRESSION_LEVEL
export S3_ENABLED S3_BUCKET S3_STORAGE_CLASS S3_REGION
export MINIO_ENABLED MINIO_ENDPOINT MINIO_BUCKET MINIO_ACCESS_KEY MINIO_SECRET_KEY
export ENCRYPT_ENABLED ENCRYPTION_KEY_PATH ENCRYPTION_ALGORITHM
export WEBHOOK_URL WEBHOOK_ENABLED NOTIFICATION_LEVEL
export LOG_LEVEL LOG_FILE LOG_TO_FILE LOG_TO_STDOUT

# Export functions
export -f load_env_file
export -f validate_config
export -f set_defaults
export -f load_config
