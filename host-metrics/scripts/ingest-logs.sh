#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
LOGS_CSV="$ROOT_DIR/data/system-logs.csv"
LOGS_SUMMARY="$ROOT_DIR/data/logs-summary.json"

mkdir -p "$ROOT_DIR/data"

# Create CSV header if file not exists
if [ ! -f "$LOGS_CSV" ]; then
  echo "timestamp,level,unit,message" > "$LOGS_CSV"
fi

# Timestamp
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# Capturar logs de las últimas 1 minuto con journalctl
# Filtrar por prioridades: 0=emerg, 1=alert, 2=crit, 3=err, 4=warning
since="1 minute ago"

# Capturar logs críticos y errores
critical_count=0
error_count=0
warning_count=0

if command -v journalctl &> /dev/null; then
  # Contar por severidad
  critical_count=$(journalctl --since="$since" -p 0..2 --no-pager -q 2>/dev/null | wc -l || echo 0)
  error_count=$(journalctl --since="$since" -p 3 --no-pager -q 2>/dev/null | wc -l || echo 0)
  warning_count=$(journalctl --since="$since" -p 4 --no-pager -q 2>/dev/null | wc -l || echo 0)
  
  # Capturar últimos 5 logs importantes (crit, err, warning)
  journalctl --since="$since" -p 0..4 --no-pager -o json 2>/dev/null | tail -5 | while read -r line; do
    if [ -n "$line" ]; then
      # Parsear JSON con jq si está disponible
      if command -v jq &> /dev/null; then
        log_time=$(echo "$line" | jq -r '.__REALTIME_TIMESTAMP // "0"' | awk '{print int($1/1000000)}')
        priority=$(echo "$line" | jq -r '.PRIORITY // "6"')
        unit=$(echo "$line" | jq -r '._SYSTEMD_UNIT // .SYSLOG_IDENTIFIER // "system"' | tr -d ',')
        message=$(echo "$line" | jq -r '.MESSAGE // "no message"' | tr -d '\n\r' | tr ',' ';' | head -c 200)
        
        # Mapear prioridad a nivel
        case $priority in
          0|1|2) level="CRITICAL" ;;
          3) level="ERROR" ;;
          4) level="WARNING" ;;
          *) level="INFO" ;;
        esac
        
        # Convertir timestamp a ISO
        log_iso=$(date -u -d "@$log_time" +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null || echo "$timestamp")
        
        # Agregar al CSV
        echo "$log_iso,$level,$unit,$message" >> "$LOGS_CSV"
      fi
    fi
  done
else
  # Fallback: leer de /var/log/syslog o /var/log/messages
  if [ -f /var/log/syslog ]; then
    tail -100 /var/log/syslog | grep -iE "error|critical|warning" | tail -5 | while read -r line; do
      echo "$timestamp,WARNING,syslog,${line:0:200}" >> "$LOGS_CSV"
    done
    warning_count=$(tail -1000 /var/log/syslog | grep -icE "warning" || echo 0)
    error_count=$(tail -1000 /var/log/syslog | grep -icE "error" || echo 0)
    critical_count=$(tail -1000 /var/log/syslog | grep -icE "critical" || echo 0)
  fi
fi

# Generar resumen JSON
cat > "$LOGS_SUMMARY" <<EOF
{
  "timestamp": "$timestamp",
  "critical_count": $critical_count,
  "error_count": $error_count,
  "warning_count": $warning_count,
  "total_issues": $((critical_count + error_count + warning_count))
}
EOF

echo "✓ System logs ingested: $critical_count critical, $error_count errors, $warning_count warnings"
