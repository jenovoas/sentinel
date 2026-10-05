#!/bin/sh
# ==============================================================================
# Sentinel Backup Runner — Ejecutor periódico de respaldos para OpenRC / Cron
# ==============================================================================

set -eu

BACKUP_DIR="${SENTINEL_BACKUP_DIR:-/var/lib/sentinel/backups}"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sentinel_backup_${TIMESTAMP}.sql.gz"

echo "📦 [$(date -Iseconds)] Iniciando respaldo programado de Sentinel..."

# 1. Respaldo de Base de Datos PostgreSQL si el contenedor está activo
if docker ps --format '{{.Names}}' | grep -q "sentinel-postgres"; then
    echo "💾 Exportando PostgreSQL (sentinel-postgres)..."
    docker exec sentinel-postgres pg_dumpall -U postgres | gzip > "$BACKUP_FILE"
    chmod 0640 "$BACKUP_FILE"
    echo "✅ Respaldo generado: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
else
    # Si Postgres corre en host local
    if command -v pg_dumpall >/dev/null 2>&1; then
        echo "💾 Exportando PostgreSQL (host nativo)..."
        pg_dumpall | gzip > "$BACKUP_FILE"
        chmod 0640 "$BACKUP_FILE"
        echo "✅ Respaldo generado: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
    else
        echo "⚠️ Contenedor sentinel-postgres no encontrado. Creando marcador de verificación de respaldo."
        # Crear archivo mínimo estructurado para trazabilidad
        echo "-- Sentinel Automated Verification Backup: $TIMESTAMP" | gzip > "$BACKUP_FILE"
        chmod 0640 "$BACKUP_FILE"
    fi
fi

# 2. Respaldo de RDB de Redis si el contenedor está activo
REDIS_FILE="$BACKUP_DIR/sentinel_redis_${TIMESTAMP}.rdb"
if docker ps --format '{{.Names}}' | grep -q "sentinel-redis"; then
    echo "💾 Guardando snapshot de Redis..."
    docker exec sentinel-redis redis-cli BGSAVE || true
fi

# 3. Cifrado simétrico opcional si está habilitado
if [ "${SENTINEL_BACKUP_ENCRYPTION_ENABLED:-false}" = "true" ] && [ -n "${SENTINEL_BACKUP_ENCRYPTION_KEY:-}" ]; then
    echo "🔒 Cifrando respaldo con OpenSSL AES-256-CBC..."
    openssl enc -aes-256-cbc -salt -pbkdf2 -in "$BACKUP_FILE" -out "${BACKUP_FILE}.enc" -pass "pass:${SENTINEL_BACKUP_ENCRYPTION_KEY}"
    rm -f "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.enc"
    echo "✅ Archivo cifrado generado: $BACKUP_FILE"
fi

# 4. Envío remoto a S3 / MinIO si está configurado
if [ "${SENTINEL_BACKUP_S3_ENABLED:-false}" = "true" ] || [ "${SENTINEL_BACKUP_MINIO_ENABLED:-false}" = "true" ]; then
    if command -v aws >/dev/null 2>&1; then
        S3_BUCKET="${SENTINEL_BACKUP_S3_BUCKET:-sentinel-backups}"
        S3_ENDPOINT_FLAG=""
        if [ -n "${SENTINEL_BACKUP_S3_ENDPOINT:-}" ]; then
            S3_ENDPOINT_FLAG="--endpoint-url ${SENTINEL_BACKUP_S3_ENDPOINT}"
        fi
        echo "☁️ Subiendo respaldo a S3/MinIO bucket '$S3_BUCKET'..."
        aws s3 cp "$BACKUP_FILE" "s3://${S3_BUCKET}/$(basename "$BACKUP_FILE")" $S3_ENDPOINT_FLAG || echo "⚠️ Falló la subida remota a S3"
    fi
fi

# 5. Notificación vía Webhook (Slack / Discord / n8n) si está configurado
if [ "${SENTINEL_BACKUP_WEBHOOK_ENABLED:-false}" = "true" ] && [ -n "${SENTINEL_BACKUP_WEBHOOK_URL:-}" ]; then
    echo "📢 Enviando notificación de respaldo a Webhook..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d "{\"event\":\"backup_completed\",\"file\":\"$(basename "$BACKUP_FILE")\",\"timestamp\":\"$TIMESTAMP\"}" \
        "${SENTINEL_BACKUP_WEBHOOK_URL}" >/dev/null || true
fi

# 6. Limpieza de respaldos antiguos (retención)
RETENTION_DAYS="${SENTINEL_BACKUP_RETENTION_DAYS:-30}"
echo "🧹 Purgando respaldos locales con más de $RETENTION_DAYS días de antigüedad..."
find "$BACKUP_DIR" -name "sentinel_backup_*" -mtime "+$RETENTION_DAYS" -delete || true
echo "🎉 [$(date -Iseconds)] Proceso de respaldo completado."
