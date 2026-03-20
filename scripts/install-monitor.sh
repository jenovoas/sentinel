#!/bin/bash
# ================================================================================
# Script de Instalación - Monitor de Sitios Pinguino Seguro
# ================================================================================
# Ejecutar como root o con sudo
# ================================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="/usr/local/bin/monitor-sitios.sh"
SERVICE_FILE="/etc/systemd/system/pinguino-monitor.service"
TIMER_FILE="/etc/systemd/system/pinguino-monitor.timer"
LOG_FILE="/var/log/pinguinoseguro-monitor.log"

echo "🚀 Instalando Monitor de Sitios - Pinguino Seguro"
echo "=================================================="

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script debe ejecutarse como root (sudo)"
   exit 1
fi

# 1. Copiar script de monitoreo
echo "📋 Copiando script de monitoreo..."
cp "$SCRIPT_DIR/monitor-sitios.sh" "$MONITOR_SCRIPT"
chmod +x "$MONITOR_SCRIPT"
echo "   ✅ Script instalado en $MONITOR_SCRIPT"

# 2. Copiar archivos de systemd
echo "📋 Copiando unidades de systemd..."
cp "$SCRIPT_DIR/pinguino-monitor.service" "$SERVICE_FILE"
cp "$SCRIPT_DIR/pinguino-monitor.timer" "$TIMER_FILE"
echo "   ✅ Service instalado en $SERVICE_FILE"
echo "   ✅ Timer instalado en $TIMER_FILE"

# 3. Crear archivo de log
echo "📝 Creando archivo de log..."
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"
echo "   ✅ Log creado en $LOG_FILE"

# 4. Configurar variables de entorno (opcional)
echo ""
echo "⚙️  Configuración de alertas (opcional)"
echo "----------------------------------------"
read -p "¿Configurar alertas por Telegram? (y/N): " use_telegram

if [[ "$use_telegram" =~ ^[Yy]$ ]]; then
  read -p "Telegram Bot Token: " bot_token
  read -p "Telegram Chat ID: " chat_id
  
  # Actualizar service file con credenciales
  sed -i "s|Environment=TELEGRAM_BOT_TOKEN=|Environment=TELEGRAM_BOT_TOKEN=${bot_token}|" "$SERVICE_FILE"
  sed -i "s|Environment=TELEGRAM_CHAT_ID=|Environment=TELEGRAM_CHAT_ID=${chat_id}|" "$SERVICE_FILE"
  echo "   ✅ Telegram configurado"
else
  echo "   ℹ️  Telegram omitido (solo email)"
fi

echo ""
read -p "Email para alertas (default: admin@pinguinoseguro.cl): " alert_email
alert_email="${alert_email:-admin@pinguinoseguro.cl}"

# Actualizar script con email
sed -i "s|ALERT_EMAIL=\"admin@pinguinoseguro.cl\"|ALERT_EMAIL=\"${alert_email}\"|" "$MONITOR_SCRIPT"
echo "   ✅ Email configurado: $alert_email"

# 5. Recargar systemd
echo ""
echo "🔄 Recargando systemd..."
systemctl daemon-reload
echo "   ✅ systemd recargado"

# 6. Habilitar y iniciar timer
echo ""
echo "🎬 Habilitando timer..."
systemctl enable pinguino-monitor.timer
systemctl start pinguino-monitor.timer
echo "   ✅ Timer habilitado e iniciado"

# 7. Verificar estado
echo ""
echo "📊 Estado del servicio:"
systemctl status pinguino-monitor.timer --no-pager

# 8. Verificar logs
echo ""
echo "📋 Próximos logs:"
echo "   Ver con: journalctl -u pinguino-monitor.service -f"
echo "   O: tail -f $LOG_FILE"

# 9. Resumen
echo ""
echo "=================================================="
echo "✅ Instalación completada exitosamente"
echo "=================================================="
echo ""
echo "📍 Archivos instalados:"
echo "   - $MONITOR_SCRIPT"
echo "   - $SERVICE_FILE"
echo "   - $TIMER_FILE"
echo ""
echo "📊 Comandos útiles:"
echo "   - Ver estado: systemctl status pinguino-monitor.timer"
echo "   - Ver logs: journalctl -u pinguino-monitor.service -f"
echo "   - Logs archivo: tail -f $LOG_FILE"
echo "   - Forzar ejecución: systemctl start pinguino-monitor.service"
echo "   - Detener: systemctl stop pinguino-monitor.timer"
echo ""
echo "⏰ El monitor se ejecutará cada 1 minuto automáticamente"
echo ""
echo "🧪 Para probar manualmente:"
echo "   sudo $MONITOR_SCRIPT"
echo ""
