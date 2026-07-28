#!/bin/bash
set -euo pipefail

# --- Trap para limpieza en caso de error ---
cleanup() {
  log_warn "Ocurrió un error. Revirtiendo cambios..."
  if [ -d "$SITIO_DIR" ]; then
    log_warn "Eliminando directorio incompleto: $SITIO_DIR"
    rm -rf "$SITIO_DIR"
  fi
  # Limpieza de entrada de crontab si se agregó
  if [ -n "${CRON_ADDED:-}" ]; then
    log_warn "Removiendo entrada de crontab..."
    crontab -l | grep -v "$SITIO_DIR/backup.sh" | crontab -
  fi
  # Nota: La limpieza de DNS requeriría lógica adicional con pdnsutil
}
trap cleanup ERR

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Validar argumentos
if [[ $# -lt 3 ]]; then
  echo "Uso: $0 <nombre-cliente> <dominio> <tipo-stack>"
  echo ""
  echo "Ejemplo:"
  echo "  $0 laespiguita laespiguita.cl wordpress"
  echo ""
  echo "Tipos de stack disponibles:"
  echo "  - nextjs      (Next.js 16 + Node 20)"
  echo "  - wordpress   (WordPress 6 + MariaDB)"
  echo "  - static      (HTML estático + Nginx)"
  exit 1
fi

CLIENTE_SLUG="$1"
DOMINIO="$2"
STACK_TYPE="$3"

# --- Validaciones de Seguridad y Prerrequisitos ---

# 1. Prevenir Path Traversal (validación estricta)
if [[ "$CLIENTE_SLUG" =~ (\.\.|/|\\) ]]; then
  log_error "Nombre de cliente inválido. No puede contener '..', '/' o '\\'."
fi

# 2. Validar formato del slug (solo letras, números, guiones bajos y guiones)
if [[ ! "$CLIENTE_SLUG" =~ ^[a-z0-9_-]+$ ]]; then
  log_error "Nombre de cliente inválido. Solo se permiten letras minúsculas, números, guiones bajos y guiones."
fi

# 3. Validar formato de dominio (previene inyección de dominios maliciosos)
if [[ ! "$DOMINIO" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$ ]]; then
  log_error "Dominio inválido. Formato esperado: ejemplo.cl o sub.ejemplo.com"
fi

# 4. Validar que los comandos externos existan
for cmd in openssl sed curl crontab podman-compose; do
  if ! command -v "$cmd" &> /dev/null; then
    log_error "Comando requerido no encontrado: $cmd. Por favor, instálalo."
  fi
done

# 5. Validar que no se ejecuta como root (seguridad)
if [[ $EUID -eq 0 ]]; then
  log_error "No ejecutar como root. Este script debe ejecutarse como usuario normal."
fi

# Directorio base
CLIENTES_DIR="$HOME/clientes"
PLANTILLA_DIR="$CLIENTES_DIR/plantillas/$STACK_TYPE"
SITIO_DIR="$CLIENTES_DIR/sitios/$CLIENTE_SLUG"
TRAEFIK_CONFIG_DIR="$HOME/containers/traefik/config/dynamic"

# Validar que la plantilla exista
if [ ! -d "$PLANTILLA_DIR" ]; then
  log_error "Plantilla '$STACK_TYPE' no encontrada en $PLANTILLA_DIR"
fi

# Validar que el cliente no exista ya
if [ -d "$SITIO_DIR" ]; then
  log_error "El cliente '$CLIENTE_SLUG' ya existe en $SITIO_DIR"
fi

log_info "🚀 Creando nuevo sitio para cliente: $CLIENTE_SLUG"
log_info "📦 Stack: $STACK_TYPE"
log_info "🌐 Dominio: $DOMINIO"

# Paso 1: Crear estructura de directorios
log_info "📁 Creando directorios..."
mkdir -p "$SITIO_DIR"
cd "$SITIO_DIR"

# Paso 2: Generar credenciales aleatorias
DB_ROOT_PASSWORD=$(openssl rand -base64 24)
DB_PASSWORD=$(openssl rand -base64 24)
DOMINIO_ESCAPED=$(echo "$DOMINIO" | sed 's/\./\\\\./g')

# Paso 3: Copiar y procesar plantilla
log_info "📝 Procesando plantilla..."
cp -r "$PLANTILLA_DIR"/* "$SITIO_DIR/"

# Reemplazar variables en compose.yaml
sed -e "s/{{CLIENTE_SLUG}}/$CLIENTE_SLUG/g" \
    -e "s/{{DOMINIO}}/$DOMINIO/g" \
    -e "s/{{DOMINIO_ESCAPED}}/$DOMINIO_ESCAPED/g" \
    -e "s|{{DB_ROOT_PASSWORD}}|$DB_ROOT_PASSWORD|g" \
    -e "s|{{DB_PASSWORD}}|$DB_PASSWORD|g" \
    "$SITIO_DIR/compose.template.yaml" > "$SITIO_DIR/compose.yaml"

rm "$SITIO_DIR/compose.template.yaml"

# Guardar credenciales
cat > "$SITIO_DIR/.env" <<EOF
# Credenciales generadas automáticamente - NO COMPARTIR
CLIENTE_SLUG=$CLIENTE_SLUG
DOMINIO=$DOMINIO
DB_ROOT_PASSWORD=$DB_ROOT_PASSWORD
DB_PASSWORD=$DB_PASSWORD
DATABASE_URL=mysql://${CLIENTE_SLUG}_user:${DB_PASSWORD}@${CLIENTE_SLUG}-db:3306/${CLIENTE_SLUG}_wp
EOF

chmod 600 "$SITIO_DIR/.env"

log_info "✅ Credenciales guardadas en $SITIO_DIR/.env"

# Paso 4: Configurar DNS en PowerDNS
log_info "🌍 Configurando DNS..."

# Verificar si pdnsutil está disponible
if command -v pdnsutil &> /dev/null; then
  # Agregar record A apuntando a fenix
  pdnsutil add-record pinguinoseguro.cl "${CLIENTE_SLUG}.pinguinoseguro.cl" A 3600 34.28.226.63 || log_warn "DNS ya existe o error al agregar"

  # Si es dominio externo, mostrar instrucciones
  if [[ ! "$DOMINIO" =~ pinguinoseguro\.cl$ ]]; then
    log_warn "⚠️  Dominio externo detectado: $DOMINIO"
    log_warn "    Debes configurar en el DNS del cliente:"
    log_warn "    $DOMINIO.  IN A  34.28.226.63"
    log_warn "    www.$DOMINIO.  IN A  34.28.226.63"
  fi
else
  log_warn "pdnsutil no encontrado - configurar DNS manualmente"
fi

# Paso 5: Levantar contenedores
log_info "🐳 Levantando contenedores..."
cd "$SITIO_DIR"

podman-compose up -d

# Esperar a que el contenedor arranque
log_info "⏳ Esperando 10 segundos a que el servicio inicie..."
sleep 10

# Paso 6: Verificar que el contenedor esté corriendo
if podman ps --filter "name=${CLIENTE_SLUG}" --format "{{.Names}}" | grep -q "$CLIENTE_SLUG"; then
  log_info "✅ Contenedor $CLIENTE_SLUG corriendo"
else
  log_error "❌ El contenedor no se levantó. Revisa los logs con: podman logs ${CLIENTE_SLUG}-web"
fi

# Paso 7: Configurar backup automático (sin credenciales hardcoded)
log_info "💾 Configurando backup automático..."
cat > "$SITIO_DIR/backup.sh" <<'BACKUP_EOF'
#!/bin/bash
set -euo pipefail

# Cargar credenciales desde .env (NO están en el script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.env"

BACKUP_DIR="$HOME/clientes/backups/${CLIENTE_SLUG}"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup de archivos
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" -C "$SITIO_DIR" .

# Backup de base de datos (si existe)
if podman ps --filter "name=${CLIENTE_SLUG}-db" --format "{{.Names}}" | grep -q "${CLIENTE_SLUG}-db"; then
  # Leer credenciales desde variables de entorno
  podman exec ${CLIENTE_SLUG}-db mysqldump -u root -p"${DB_ROOT_PASSWORD}" ${CLIENTE_SLUG}_wp \
    | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
fi

# Cleanup: mantener últimos 30 backups
ls -t "$BACKUP_DIR"/files_*.tar.gz 2>/dev/null | tail -n +31 | xargs -r rm
ls -t "$BACKUP_DIR"/db_*.sql.gz 2>/dev/null | tail -n +31 | xargs -r rm

echo "Backup completado: $BACKUP_DIR"
BACKUP_EOF

# Hacer ejecutable el backup
chmod +x "$SITIO_DIR/backup.sh"
chmod 600 "$SITIO_DIR/backup.sh"

# Agregar a crontab (previniendo duplicación)
CRON_ENTRY="0 3 * * * $SITIO_DIR/backup.sh"
if ! crontab -l 2>/dev/null | grep -qF "$SITIO_DIR/backup.sh"; then
  (crontab -l 2>/dev/null | grep -v '^$'; echo "$CRON_ENTRY") | crontab -
  CRON_ADDED="true"
  log_info "✅ Backup configurado (diario 3 AM)"
else
  log_warn "⚠️  Entrada de backup ya existe en crontab (omitiendo)"
fi

# Paso 8: Verificar acceso HTTPS
log_info "🔒 Verificando HTTPS..."
sleep 5
# Usamos -k para ignorar errores de certificado temporalmente mientras se genera
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k "https://$DOMINIO" || echo "000")

if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ] || [ "$HTTP_CODE" == "301" ]; then
  log_info "✅ Sitio accesible en https://$DOMINIO (HTTP $HTTP_CODE)"
else
  log_warn "⚠️  Sitio responde con HTTP $HTTP_CODE - verificar Traefik"
  log_warn "    Puede tardar hasta 2 minutos en obtener certificado SSL"
fi

# Paso 9: Verificación de seguridad
log_info "🔐 Verificando configuración de seguridad..."

# Verificar permisos del archivo .env
ENV_PERMS=$(stat -c "%a" "$SITIO_DIR/.env" 2>/dev/null || echo "000")
if [ "$ENV_PERMS" == "600" ]; then
  log_info "✅ .env con permisos seguros (600)"
else
  log_warn "⚠️  .env tiene permisos inseguros ($ENV_PERMS). Corrigiendo..."
  chmod 600 "$SITIO_DIR/.env"
fi

# Verificar que backup.sh no tenga credenciales hardcoded
if grep -qE "(PASSWORD|SECRET|KEY)=" "$SITIO_DIR/backup.sh" 2>/dev/null; then
  log_error "❌ backup.sh contiene credenciales hardcoded. Esto es una vulnerabilidad crítica."
fi

# Paso 10: Resumen final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "🎉 ¡Sitio creado exitosamente!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Directorio:  $SITIO_DIR"
echo "🌐 URL:         https://$DOMINIO"
echo "🐳 Contenedor:  ${CLIENTE_SLUG}-web"
echo "💾 Backups:     ~/clientes/backups/$CLIENTE_SLUG/"
echo ""

if [ "$STACK_TYPE" == "wordpress" ]; then
  echo "🔑 Credenciales WordPress:"
  echo "   Base de datos: ${CLIENTE_SLUG}_wp"
  echo "   Usuario DB:    ${CLIENTE_SLUG}_user"
  echo "   Password DB:   (ver archivo .env con permisos 600)"
  echo ""
  echo "   ⚠️  IMPORTANTE: NUNCA compartas el archivo .env"
  echo "   Configurar WordPress en: https://$DOMINIO/wp-admin/install.php"
  echo ""
fi

echo "📝 Comandos útiles:"
echo "   Ver logs:      podman logs -f ${CLIENTE_SLUG}-web"
echo "   Reiniciar:     cd $SITIO_DIR && podman-compose restart"
echo "   Detener:       cd $SITIO_DIR && podman-compose down"
echo "   Backup manual: $SITIO_DIR/backup.sh"
echo ""
echo "🔒 Seguridad:"
echo "   - .env con permisos restrictivos (600)"
echo "   - backup.sh sin credenciales hardcoded"
echo "   - Crontab configurado sin duplicación"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Desactivar el trap si todo salió bien
trap - ERR