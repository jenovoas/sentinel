# 📦 Guía de Configuración: Sistema de Backups Mejorado
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


**Fecha**: 15 de Diciembre, 2025  
**Tiempo estimado**: 1-2 horas  
**Dificultad**: 🟢 Baja

---

## 🎯 Objetivo

Configurar el sistema de backups mejorado con:
- ✅ Verificación de integridad automática
- ✅ S3/MinIO sync para backups off-site
- ✅ Encriptación opcional (AES-256)
- ✅ Alertas por webhook (Slack/Discord)

---

## 📋 Paso 1: Testing Básico (Sin S3, sin encriptación)

### 1.1 Ejecutar backup manual

```bash
cd /home/jnovoas/sentinel

# Ejecutar script
./scripts/backup-postgres.sh
```

**Salida esperada**:
```
[2025-12-15 15:30:00] Starting PostgreSQL backup...
[2025-12-15 15:30:01] Creating unencrypted backup...
[2025-12-15 15:30:15] Backup completed: sentinel_backup_20251215_153000.sql.gz (45M)
[2025-12-15 15:30:15] Verifying backup integrity...
[2025-12-15 15:30:16] Backup integrity verified ✓
[2025-12-15 15:30:16] Cleaning up backups older than 7 days...
[2025-12-15 15:30:16] Deleted 0 old local backup(s)
[2025-12-15 15:30:16] Current local backups:
-rw-r--r-- 1 root root 45M Dec 15 15:30 sentinel_backup_20251215_153000.sql.gz
[2025-12-15 15:30:16] Summary: 1 backups, 45M total
[2025-12-15 15:30:16] Backup process completed ✓
```

### 1.2 Verificar backup creado

```bash
ls -lh /var/backups/sentinel/postgres/
```

---

## 📋 Paso 2: Configurar Webhook (Alertas Slack/Discord)

### 2.1 Crear Webhook en Slack

1. Ve a https://api.slack.com/messaging/webhooks
2. Crea un nuevo webhook
3. Copia la URL (ejemplo: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX`)

### 2.2 Configurar variable de entorno

```bash
# Opción A: Variable de entorno global
echo 'export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"' >> ~/.bashrc
source ~/.bashrc

# Opción B: Variable en script (editar backup-postgres.sh línea 33)
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 2.3 Testing webhook

```bash
# Ejecutar backup nuevamente
./scripts/backup-postgres.sh
```

**Deberías recibir en Slack**:
```
✅ Sentinel backup completed: sentinel_backup_20251215_153000.sql.gz (45M)
```

---

## 📋 Paso 3: Configurar S3 (Backup Off-Site)

### 3.1 Instalar AWS CLI

```bash
# Instalar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar instalación
aws --version
```

### 3.2 Configurar credenciales AWS

```bash
aws configure

# Ingresar:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: us-east-1
# Default output format: json
```

### 3.3 Crear bucket S3

```bash
# Crear bucket
aws s3 mb s3://sentinel-backups

# Verificar
aws s3 ls
```

### 3.4 Habilitar S3 en script

Editar `/home/jnovoas/sentinel/scripts/backup-postgres.sh`:

```bash
# Cambiar línea 21:
S3_ENABLED=true  # Cambiar de false a true

# Cambiar línea 22 (opcional):
S3_BUCKET="s3://sentinel-backups/postgres"
```

### 3.5 Testing S3 sync

```bash
# Ejecutar backup
./scripts/backup-postgres.sh
```

**Salida esperada**:
```
[2025-12-15 15:35:00] Uploading to S3...
upload: /var/backups/sentinel/postgres/sentinel_backup_20251215_153500.sql.gz to s3://sentinel-backups/postgres/sentinel_backup_20251215_153500.sql.gz
[2025-12-15 15:35:05] S3 upload successful ✓
```

### 3.6 Verificar en S3

```bash
aws s3 ls s3://sentinel-backups/postgres/
```

---

## 📋 Paso 4: Configurar Encriptación (Opcional)

### 4.1 Generar clave de encriptación

```bash
# Crear directorio para claves
sudo mkdir -p /etc/sentinel
sudo chmod 700 /etc/sentinel

# Generar clave aleatoria
sudo openssl rand -base64 32 > /etc/sentinel/backup.key

# Proteger clave
sudo chmod 600 /etc/sentinel/backup.key
```

### 4.2 Habilitar encriptación en script

Editar `/home/jnovoas/sentinel/scripts/backup-postgres.sh`:

```bash
# Cambiar línea 30:
ENCRYPT_ENABLED=true  # Cambiar de false a true
```

### 4.3 Testing encriptación

```bash
# Ejecutar backup
./scripts/backup-postgres.sh
```

**Salida esperada**:
```
[2025-12-15 15:40:00] Creating encrypted backup...
[2025-12-15 15:40:15] Backup completed: sentinel_backup_20251215_154000.sql.gz.enc (45M)
[2025-12-15 15:40:15] Verifying backup integrity...
[2025-12-15 15:40:16] Backup integrity verified ✓
```

**Nota**: Archivo ahora tiene extensión `.enc`

### 4.4 Testing restore encriptado

```bash
# Decrypt y restore
BACKUP_FILE="/var/backups/sentinel/postgres/sentinel_backup_20251215_154000.sql.gz.enc"

# Decrypt
openssl enc -aes-256-cbc -d -pbkdf2 \
  -pass file:/etc/sentinel/backup.key \
  -in "$BACKUP_FILE" \
  | gunzip > /tmp/backup_decrypted.sql

# Restore (modificar restore-postgres.sh para soportar encriptación)
```

---

## 📋 Paso 5: Configurar Cron (Backups Automáticos)

### 5.1 Editar crontab

```bash
crontab -e
```

### 5.2 Agregar línea

```bash
# Backups cada 6 horas
0 */6 * * * /home/jnovoas/sentinel/scripts/backup-postgres.sh >> /var/log/sentinel-backup.log 2>&1

# O backups diarios a las 3 AM
0 3 * * * /home/jnovoas/sentinel/scripts/backup-postgres.sh >> /var/log/sentinel-backup.log 2>&1
```

### 5.3 Verificar cron configurado

```bash
crontab -l
```

### 5.4 Crear archivo de log

```bash
sudo touch /var/log/sentinel-backup.log
sudo chmod 644 /var/log/sentinel-backup.log
```

### 5.5 Monitorear logs

```bash
# Ver logs en tiempo real
tail -f /var/log/sentinel-backup.log

# Ver últimos backups
grep "Backup process completed" /var/log/sentinel-backup.log
```

---

## 📋 Paso 6: Testing Completo

### 6.1 Crear datos de prueba

```bash
docker exec sentinel-postgres psql -U sentinel -c \
  "CREATE TABLE IF NOT EXISTS test_backup (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
  );"

docker exec sentinel-postgres psql -U sentinel -c \
  "INSERT INTO test_backup (data) VALUES ('test-$(date +%s)');"
```

### 6.2 Ejecutar backup

```bash
./scripts/backup-postgres.sh
```

### 6.3 Simular pérdida de datos

```bash
docker exec sentinel-postgres psql -U sentinel -c \
  "DROP TABLE test_backup;"

# Verificar que tabla no existe
docker exec sentinel-postgres psql -U sentinel -c \
  "SELECT * FROM test_backup;"
# Error: relation "test_backup" does not exist
```

### 6.4 Restaurar desde backup

```bash
# Encontrar último backup
LATEST_BACKUP=$(ls -t /var/backups/sentinel/postgres/sentinel_backup_*.sql.gz* | head -1)

echo "Restaurando desde: $LATEST_BACKUP"

# Ejecutar restore
./scripts/restore-postgres.sh "$LATEST_BACKUP"
```

### 6.5 Verificar datos restaurados

```bash
docker exec sentinel-postgres psql -U sentinel -c \
  "SELECT * FROM test_backup;"

# Deberías ver los datos restaurados
```

---

## 📋 Paso 7: Configurar MinIO (Alternativa a S3)

### 7.1 Instalar MinIO Client

```bash
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/
```

### 7.2 Configurar MinIO

```bash
# Agregar servidor MinIO
mc alias set minio http://your-minio-server:9000 YOUR_ACCESS_KEY YOUR_SECRET_KEY

# Crear bucket
mc mb minio/sentinel-backups

# Verificar
mc ls minio/
```

### 7.3 Habilitar MinIO en script

Editar `/home/jnovoas/sentinel/scripts/backup-postgres.sh`:

```bash
# Cambiar línea 26:
MINIO_ENABLED=true  # Cambiar de false a true

# Cambiar línea 27-28 (opcional):
MINIO_ALIAS="minio"
MINIO_BUCKET="sentinel-backups/postgres"
```

### 7.4 Testing MinIO

```bash
./scripts/backup-postgres.sh
```

---

## ✅ Checklist de Verificación

### Configuración Básica
- [ ] Script ejecuta sin errores
- [ ] Backup se crea en `/var/backups/sentinel/postgres/`
- [ ] Verificación de integridad pasa
- [ ] Logs se escriben correctamente

### Webhook (Opcional)
- [ ] Webhook URL configurado
- [ ] Alertas llegan a Slack/Discord
- [ ] Alertas de éxito ✅
- [ ] Alertas de error 🚨

### S3 (Opcional)
- [ ] AWS CLI instalado y configurado
- [ ] Bucket S3 creado
- [ ] Backups se suben a S3
- [ ] Cleanup S3 funciona

### Encriptación (Opcional)
- [ ] Clave de encriptación generada
- [ ] Backups se encriptan (.enc)
- [ ] Verificación funciona con encriptación
- [ ] Restore funciona con decrypt

### Cron
- [ ] Cron job configurado
- [ ] Logs se escriben en `/var/log/sentinel-backup.log`
- [ ] Backups automáticos funcionan

### Testing
- [ ] Backup manual exitoso
- [ ] Restore manual exitoso
- [ ] Datos se recuperan correctamente

---

## 🔧 Troubleshooting

### Error: "Encryption key not found"
```bash
# Verificar que existe
ls -l /etc/sentinel/backup.key

# Si no existe, generar
sudo openssl rand -base64 32 > /etc/sentinel/backup.key
sudo chmod 600 /etc/sentinel/backup.key
```

### Error: "S3 upload failed"
```bash
# Verificar credenciales
aws sts get-caller-identity

# Verificar bucket existe
aws s3 ls s3://sentinel-backups/

# Verificar permisos
aws s3api get-bucket-acl --bucket sentinel-backups
```

### Error: "Backup corrupted"
```bash
# Verificar integridad manualmente
gunzip -t /var/backups/sentinel/postgres/sentinel_backup_*.sql.gz

# Si está corrupto, usar backup anterior
ls -lt /var/backups/sentinel/postgres/
```

### Webhook no funciona
```bash
# Testing manual
curl -X POST "$SLACK_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from Sentinel"}'

# Verificar variable de entorno
echo $SLACK_WEBHOOK_URL
```

---

## 📊 Monitoreo y Métricas

### Ver estadísticas de backups

```bash
# Tamaño total
du -sh /var/backups/sentinel/postgres/

# Número de backups
ls -1 /var/backups/sentinel/postgres/ | wc -l

# Último backup
ls -lt /var/backups/sentinel/postgres/ | head -2

# Backups en S3
aws s3 ls s3://sentinel-backups/postgres/ --recursive --human-readable --summarize
```

### Dashboard Grafana (Próximo paso)

Crear dashboard con:
- Último backup exitoso (timestamp)
- Tamaño de backups (tendencia)
- Tasa de éxito (%)
- Espacio en disco usado

---

## 🎯 Próximos Pasos

Una vez completado este paso:

1. ✅ **Backups mejorados** (COMPLETADO)
2. ⏭️ **Health check endpoints** (Próximo)
3. ⏭️ **Testing PostgreSQL HA**
4. ⏭️ **Redis HA**

---

## 📝 Resumen de Mejoras

| Feature | Antes | Después |
|---------|-------|---------|
| **Verificación** | ❌ No | ✅ Automática |
| **Off-site** | ❌ No | ✅ S3/MinIO |
| **Encriptación** | ❌ No | ✅ AES-256 |
| **Alertas** | ❌ No | ✅ Webhook |
| **Cleanup S3** | ❌ No | ✅ Automático |
| **Logs** | ❌ stdout | ✅ Archivo |

**Tiempo invertido**: 1-2 horas  
**Beneficio**: Sistema enterprise-grade  
**Costo**: $12/mes (S3) o $0 (MinIO self-hosted)