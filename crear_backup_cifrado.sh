#!/bin/bash
# Script de Backup Cifrado - Sentinel Cortex™
# Fecha: 21 de Diciembre de 2025

echo "🔐 BACKUP CIFRADO - Sentinel Cortex™"
echo "======================================"
echo ""

# Configuración
BACKUP_DIR="/home/jnovoas"
PROJECT_DIR="/home/jnovoas/sentinel"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/sentinel_backup_${TIMESTAMP}.tar.gz"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

echo "📦 Paso 1: Creando archivo tar.gz..."
cd /home/jnovoas
tar czf "${BACKUP_FILE}" \
    --exclude='sentinel/backend/app/**/__pycache__' \
    --exclude='sentinel/backend/app/**/*.pyc' \
    --exclude='sentinel/node_modules' \
    --exclude='sentinel/.next' \
    --exclude='sentinel/frontend/node_modules' \
    --exclude='sentinel/frontend/.next' \
    sentinel

if [ $? -eq 0 ]; then
    echo "✅ Archivo tar.gz creado: ${BACKUP_FILE}"
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "   Tamaño: ${SIZE}"
else
    echo "❌ Error creando archivo tar.gz"
    exit 1
fi

echo ""
echo "🔒 Paso 2: Cifrando con GPG..."
echo "   (Se te pedirá una contraseña - úsala para descifrar después)"
echo ""

gpg --symmetric --cipher-algo AES256 "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ Archivo cifrado: ${ENCRYPTED_FILE}"
    SIZE_ENC=$(du -h "${ENCRYPTED_FILE}" | cut -f1)
    echo "   Tamaño cifrado: ${SIZE_ENC}"
    
    # Eliminar archivo sin cifrar
    rm "${BACKUP_FILE}"
    echo "   Archivo sin cifrar eliminado (seguridad)"
else
    echo "❌ Error cifrando archivo"
    exit 1
fi

echo ""
echo "📋 Paso 3: Generando hash SHA-256..."
HASH=$(sha256sum "${ENCRYPTED_FILE}" | cut -d' ' -f1)
echo "${HASH}  ${ENCRYPTED_FILE}" > "${ENCRYPTED_FILE}.sha256"
echo "✅ Hash: ${HASH}"

echo ""
echo "✅ BACKUP COMPLETADO"
echo "======================================"
echo "Archivo cifrado: ${ENCRYPTED_FILE}"
echo "Hash SHA-256: ${ENCRYPTED_FILE}.sha256"
echo ""
echo "⚠️  IMPORTANTE:"
echo "1. Guarda este archivo en múltiples ubicaciones:"
echo "   - USB externo"
echo "   - Google Drive (cifrado)"
echo "   - Dropbox (cifrado)"
echo "   - Servidor remoto"
echo ""
echo "2. Recuerda la contraseña que usaste para cifrar"
echo ""
echo "3. Para descifrar:"
echo "   gpg -d ${ENCRYPTED_FILE} | tar xzf -"
echo ""
