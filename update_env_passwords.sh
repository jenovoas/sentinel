#!/bin/bash
# Script para actualizar contraseñas en .env con valores seguros
# Generado automáticamente - Ejecutar una sola vez

set -e

ENV_FILE="/home/jnovoas/sentinel/.env"

echo "🔐 Actualizando contraseñas en .env con valores seguros..."

# Backup del archivo original
cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup creado"

# Actualizar contraseñas usando sed
sed -i 's/^GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=z5cObVO0qTY_gg2H1m_-vQ  # Auto-generated secure password/' "$ENV_FILE"
sed -i 's/^N8N_PASSWORD=.*/N8N_PASSWORD=HDREZfGCyant6DlUNHz_pA  # Auto-generated secure password/' "$ENV_FILE"
sed -i 's/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=2wA4KgRinuKNgcOrA839ZRC2R1ycNtC4/' "$ENV_FILE"
sed -i 's|^DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://sentinel_user:2wA4KgRinuKNgcOrA839ZRC2R1ycNtC4@postgres:5432/sentinel_db|' "$ENV_FILE"
sed -i 's/^SECRET_KEY=.*/SECRET_KEY=WLCZYVD3BU831rdCEHTyHtAN08QNKLds8Y28JdVnHhs/' "$ENV_FILE"
sed -i 's/^OBSERVABILITY_METRICS_PASSWORD=.*/OBSERVABILITY_METRICS_PASSWORD=_3edtNFy9VkfOXt8XL_Oxw  # Auto-generated secure password/' "$ENV_FILE"
sed -i 's/^OBSERVABILITY_LOGS_PASSWORD=.*/OBSERVABILITY_LOGS_PASSWORD=0YSjYHI9jR4jleBEk7_HSA  # Auto-generated secure password/' "$ENV_FILE"

echo "✅ Contraseñas actualizadas exitosamente"
echo ""
echo "📋 Contraseñas generadas:"
echo "  - POSTGRES_PASSWORD: 2wA4KgRinuKNgcOrA839ZRC2R1ycNtC4"
echo "  - SECRET_KEY: WLCZYVD3BU831rdCEHTyHtAN08QNKLds8Y28JdVnHhs"
echo "  - GRAFANA_PASSWORD: z5cObVO0qTY_gg2H1m_-vQ"
echo "  - N8N_PASSWORD: HDREZfGCyant6DlUNHz_pA"
echo "  - OBSERVABILITY_METRICS_PASSWORD: _3edtNFy9VkfOXt8XL_Oxw"
echo "  - OBSERVABILITY_LOGS_PASSWORD: 0YSjYHI9jR4jleBEk7_HSA"
echo ""
echo "⚠️  IMPORTANTE: Guarda estas contraseñas en un lugar seguro (password manager)"
echo "⚠️  El backup está en: $ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
