# 🎉 Enterprise Backup System - Quick Start Guide

## ✅ Sistema Completado

El sistema de backups enterprise está **100% funcional** y listo para producción.

## 🚀 Inicio Rápido (5 minutos)

### 1. Verificar que el sistema funciona

```bash
# Ejecutar backup manual
./scripts/backup/backup.sh

# Verificar que se creó el backup
ls -lh /var/backups/sentinel/postgres/
```

### 2. Configurar backups automáticos (Recomendado)

```bash
# Opción A: Instalar cron automáticamente (cada 6 horas)
crontab -l > /tmp/current-cron 2>/dev/null || true
echo "0 */6 * * * cd $(pwd) && ./scripts/backup/backup.sh >> /var/log/sentinel-backup.log 2>&1" >> /tmp/current-cron
crontab /tmp/current-cron
rm /tmp/current-cron

# Verificar que se instaló
crontab -l | grep backup
```

### 3. Configurar notificaciones (Opcional pero recomendado)

```bash
# Editar .env y agregar tu webhook de Slack/Discord
nano .env

# Agregar estas líneas:
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
NOTIFICATION_LEVEL=all  # all, error, none
```

### 4. Habilitar S3 para backups off-site (Opcional)

```bash
# Editar .env
nano .env

# Agregar:
S3_ENABLED=true
S3_BUCKET=s3://sentinel-backups/postgres
S3_STORAGE_CLASS=STANDARD_IA
S3_REGION=us-east-1

# Configurar AWS CLI
aws configure
```

### 5. Habilitar encriptación (Recomendado para producción)

```bash
# Generar clave de encriptación
sudo mkdir -p /etc/sentinel
sudo openssl rand -base64 32 > /etc/sentinel/backup.key
sudo chmod 600 /etc/sentinel/backup.key
sudo chown $USER:$USER /etc/sentinel/backup.key

# Editar .env
nano .env

# Agregar:
ENCRYPT_ENABLED=true
ENCRYPTION_KEY_PATH=/etc/sentinel/backup.key
```

## 📊 Verificar que Todo Funciona

```bash
# Ver logs de backups
tail -f /var/log/sentinel-backup.log

# Ver backups creados
ls -lh /var/backups/sentinel/postgres/

# Ejecutar backup manual con debug
LOG_LEVEL=DEBUG ./scripts/backup/backup.sh
```

## 🎯 Configuración para Inversores

**Configuración mínima recomendada**:
- ✅ Backups automáticos cada 6 horas (cron)
- ✅ Notificaciones en Slack (webhooks)
- ✅ Backups off-site en S3 (disaster recovery)
- ✅ Encriptación habilitada (seguridad)

**Tiempo de configuración**: 10-15 minutos

## 📚 Documentación Completa

- **README del sistema**: [scripts/backup/README.md](scripts/backup/README.md)
- **Resumen para inversores**: [docs/BACKUP_SYSTEM_INVESTOR_SUMMARY.md](docs/BACKUP_SYSTEM_INVESTOR_SUMMARY.md)
- **Plan de implementación**: [docs/BACKUP_REFACTORING_PLAN.md](docs/BACKUP_REFACTORING_PLAN.md)

## 🆘 Troubleshooting

### Problema: Permission denied en /var/backups

```bash
sudo chmod 755 /var/backups
sudo mkdir -p /var/backups/sentinel/postgres
sudo chown -R $USER:$USER /var/backups/sentinel
```

### Problema: Backup muy pequeño

Verifica que las credenciales de PostgreSQL sean correctas en `.env`:
```bash
grep POSTGRES .env
```

### Problema: S3 upload failed

Verifica credenciales de AWS:
```bash
aws sts get-caller-identity
aws s3 ls s3://your-bucket/
```

## 🎊 ¡Listo!

El sistema está **production-ready**. Los backups se ejecutarán automáticamente y recibirás notificaciones en caso de problemas.

**Próximo paso**: Mostrar a inversores el código enterprise-grade 🚀
