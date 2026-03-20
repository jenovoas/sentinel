#!/bin/bash
# ================================================================================
# Monitor de Sitios Críticos - Pinguino Seguro
# ================================================================================
# Propósito: Verificar disponibilidad de sitios web y enviar alertas si caen
# Ubicación: /usr/local/bin/monitor-sitios.sh
# Ejecución: Cada 1 minuto vía cron o systemd timer
# ================================================================================

set -euo pipefail

# --- Configuración ---
ALERT_EMAIL="admin@pinguinoseguro.cl"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
LOG_FILE="/var/log/pinguinoseguro-monitor.log"
STATE_FILE="/tmp/pinguinoseguro-monitor-state.json"

# Sitios críticos a monitorear
declare -A SITIOS=(
  ["www.pinguinoseguro.cl"]="Sitio Principal - Inversores"
  ["laespiguita.pinguinoseguro.cl"]="La Espiguita - Cliente"
  ["portfolio.pinguinoseguro.cl"]="Portfolio - Demo"
  ["grafana.pinguinoseguro.cl"]="Grafana - Monitoreo"
  ["cortex.pinguinoseguro.cl"]="Cortex - AI"
)

# --- Funciones de Logging ---
log() {
  local level="$1"
  local message="$2"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$1"; }
log_warn() { log "WARN" "$1"; }
log_error() { log "ERROR" "$1"; }

# --- Funciones de Alerta ---
send_email_alert() {
  local subject="$1"
  local body="$2"
  
  if command -v mail &> /dev/null; then
    echo "$body" | mail -s "$subject" "$ALERT_EMAIL"
    log_info "Alerta email enviada a $ALERT_EMAIL"
  else
    log_warn "mail no disponible, alerta no enviada: $subject"
  fi
}

send_telegram_alert() {
  local message="$1"
  
  if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${message}" \
      -d "parse_mode=Markdown" \
      -d "disable_web_page_preview=true" > /dev/null
    
    log_info "Alerta Telegram enviada"
  fi
}

send_alert() {
  local site="$1"
  local status="$2"
  local description="${SITIOS[$site]}"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  local subject="🚨 SITIO CAÍDO: $site"
  local body="
ALERTA DE MONITOREO - PINGUINO SEGURO
======================================

Sitio: $site
Descripción: $description
Estado HTTP: $status
Timestamp: $timestamp

Acción requerida:
1. Verificar contenedores: podman ps | grep ${site%%.*}
2. Verificar logs: podman logs ${site%%.*}-web
3. Verificar red: podman network inspect proxy
4. Reiniciar si es necesario: podman-compose restart

---
Este es un mensaje automático del sistema de monitoreo.
"
  
  local telegram_msg="🚨 *ALERTA DE MONITOREO* 🚨

*Sítio Caído:* \`${site}\`
*Descripción:* $description
*Estado HTTP:* \`$status\`
*Timestamp:* $timestamp

*Acción requerida:* Verificar contenedores y logs

#pinguinoseguro #alerta #monitoreo"
  
  # Enviar alertas
  send_email_alert "$subject" "$body"
  send_telegram_alert "$telegram_msg"
  
  # Log en archivo
  log_error "ALERTA: $site ($description) - HTTP $status"
}

send_recovery_alert() {
  local site="$1"
  local description="${SITIOS[$site]}"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  local subject="✅ SITIO RECUPERADO: $site"
  local body="
ALERTA DE RECUPERACIÓN - PINGUINO SEGURO
=========================================

Sitio: $site
Descripción: $description
Estado HTTP: 200 OK
Timestamp: $timestamp

El sitio se recuperó automáticamente o fue restaurado.
Verificar logs para determinar causa raíz.

---
Este es un mensaje automático del sistema de monitoreo.
"
  
  local telegram_msg="✅ *SITIO RECUPERADO* ✅

*Sítio:* \`${site}\`
*Descripción:* $description
*Estado:* \`200 OK\`
*Timestamp:* $timestamp

*Nota:* Verificar logs para causa raíz

#pinguinoseguro #recuperado #monitoreo"
  
  # Enviar alertas
  send_email_alert "$subject" "$body"
  send_telegram_alert "$telegram_msg"
  
  # Log en archivo
  log_info "RECUPERADO: $site ($description)"
}

# --- Funciones de Verificación ---
check_site() {
  local site="$1"
  local status
  
  status=$(curl -sI -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "https://$site")
  echo "$status"
}

check_container_health() {
  local container="$1"
  
  if podman ps --format "{{.Names}}" | grep -q "^${container}$"; then
    local status=$(podman inspect "$container" --format '{{.State.Health.Status}}' 2>/dev/null || echo "healthy")
    echo "$status"
  else
    echo "not_found"
  fi
}

check_proxy_network() {
  local container="$1"
  
  if podman network inspect proxy 2>/dev/null | grep -q "\"name\": \"$container\""; then
    echo "connected"
  else
    echo "disconnected"
  fi
}

# --- Funciones de Estado ---
load_state() {
  if [[ -f "$STATE_FILE" ]]; then
    cat "$STATE_FILE"
  else
    echo "{}"
  fi
}

save_state() {
  local state="$1"
  echo "$state" > "$STATE_FILE"
}

get_previous_status() {
  local site="$1"
  local state=$(load_state)
  echo "$state" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$site', 'unknown'))" 2>/dev/null || echo "unknown"
}

update_state() {
  local site="$1"
  local status="$2"
  local state=$(load_state)
  echo "$state" | python3 -c "import sys,json; d=json.load(sys.stdin); d['$site']='$status'; print(json.dumps(d))" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# --- Función de Auto-Reparación (Opcional) ---
auto_repair() {
  local site="$1"
  local container="${site%%.*}-web"
  
  log_warn "Intentando auto-reparación para $site (contenedor: $container)"
  
  # Verificar si el contenedor existe
  if ! podman ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
    log_error "Contenedor $container no existe, omitiendo auto-reparación"
    return 1
  fi
  
  # Verificar si está en la red proxy
  local network_status=$(check_proxy_network "$container")
  if [[ "$network_status" == "disconnected" ]]; then
    log_info "Conectando $container a red proxy..."
    if podman network connect proxy "$container" 2>/dev/null; then
      log_info "Conexión exitosa"
      sleep 5
      
      # Verificar conectividad desde Traefik
      if podman exec traefik wget -qO- "http://$container:3000" > /dev/null 2>&1; then
        log_info "Conectividad verificada desde Traefik"
        return 0
      else
        log_error "Conectividad fallida después de conectar red"
        return 1
      fi
    else
      log_error "Falló conexión a red proxy"
      return 1
    fi
  fi
  
  # Intentar restart
  log_info "Reiniciando contenedor $container..."
  if podman restart "$container" 2>/dev/null; then
    log_info "Restart exitoso, esperando inicio..."
    sleep 15
    
    # Verificar si está saludable
    local health=$(check_container_health "$container")
    if [[ "$health" == "healthy" || "$health" == "" ]]; then
      log_info "Contenedor saludable después de restart"
      return 0
    else
      log_error "Contenedor no saludable después de restart: $health"
      return 1
    fi
  else
    log_error "Falló restart del contenedor"
    return 1
  fi
}

# --- Función Principal ---
main() {
  log_info "=== Iniciando monitoreo de sitios ==="
  
  local alerts_sent=0
  local sites_checked=0
  local sites_down=0
  
  for site in "${!SITIOS[@]}"; do
    ((sites_checked++))
    
    local status=$(check_site "$site")
    local previous_status=$(get_previous_status "$site")
    
    log_info "Verificando $site: HTTP $status (anterior: $previous_status)"
    
    if [[ "$status" -ne 200 ]]; then
      ((sites_down++))
      
      # Verificar si es una caída nueva (no alertada antes)
      if [[ "$previous_status" == "200" || "$previous_status" == "unknown" ]]; then
        log_error "Sitio $site CAÍDO (HTTP $status)"
        
        # Intentar auto-reparación (opcional, comentar si no se desea)
        # if auto_repair "$site"; then
        #   log_info "Auto-reparación exitosa para $site"
        #   send_recovery_alert "$site"
        #   update_state "$site" "200"
        #   continue
        # fi
        
        # Enviar alerta
        send_alert "$site" "$status"
        update_state "$site" "$status"
        ((alerts_sent++))
      else
        log_warn "Sitio $site sigue caído (HTTP $status) - alerta ya enviada"
      fi
    else
      # Sitio está OK
      if [[ "$previous_status" != "200" && "$previous_status" != "unknown" ]]; then
        # El sitio se recuperó
        log_info "Sitio $site RECUPERADO (HTTP $status, anterior: $previous_status)"
        send_recovery_alert "$site"
      fi
      
      update_state "$site" "200"
    fi
  done
  
  # Resumen
  log_info "=== Monitoreo completado ==="
  log_info "Sitios verificados: $sites_checked"
  log_info "Sitios caídos: $sites_down"
  log_info "Alertas enviadas: $alerts_sent"
  
  # Si todos los sitios están bien, log silencioso
  if [[ $sites_down -eq 0 ]]; then
    log_info "✓ Todos los sitios operativos"
  else
    log_error "✗ $sites_down sitio(s) caídos - revisar alertas"
  fi
  
  # Exit code para systemd/cron
  if [[ $sites_down -gt 0 ]]; then
    exit 1
  else
    exit 0
  fi
}

# --- Ejecución ---
main "$@"
