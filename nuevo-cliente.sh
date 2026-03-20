#!/bin/bash
set -euo pipefail

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
if [ $# -lt 3 ]; then
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

if command -v podman-compose &> /dev/null; then
  podman-compose up -d
elif command -v docker-compose &> /dev/null; then
  docker-compose up -d
else
  log_error "Ni podman-compose ni docker-compose encontrados"
fi

# Esperar a que el contenedor arranque
log_info "⏳ Esperando 10 segundos a que el servicio inicie..."
sleep 10

# Paso 6: Verificar que el contenedor esté corriendo
if podman ps --filter "name=${CLIENTE_SLUG}" --format "{{.Names}}" | grep -q "$CLIENTE_SLUG"; then
  log_info "✅ Contenedor $CLIENTE_SLUG corriendo"
else
  log_error "❌ Contenedor no se levantó. Revisar logs: podman logs ${CLIENTE_SLUG}-web"
fi

# Paso 7: Configurar backup automático
log_info "💾 Configurando backup automático..."
cat > "$SITIO_DIR/backup.sh" <<'BACKUP_EOF'
#!/bin/bash
BACKUP_DIR="$HOME/clientes/backups/{{CLIENTE_SLUG}}"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup de archivos
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" -C "{{SITIO_DIR}}" .

# Backup de base de datos (si existe)
if podman ps --filter "name={{CLIENTE_SLUG}}-db" --format "{{.Names}}" | grep -q "{{CLIENTE_SLUG}}-db"; then
  podman exec {{CLIENTE_SLUG}}-db mysqldump -u root -p{{DB_ROOT_PASSWORD}} {{CLIENTE_SLUG}}_wp \
    | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
fi

# Cleanup: mantener últimos 30 backups
ls -t "$BACKUP_DIR"/files_*.tar.gz | tail -n +31 | xargs -r rm
ls -t "$BACKUP_DIR"/db_*.sql.gz | tail -n +31 | xargs -r rm

echo "Backup completado: $BACKUP_DIR"
BACKUP_EOF

# Reemplazar variables en backup.sh
sed -i "s|{{CLIENTE_SLUG}}|$CLIENTE_SLUG|g" "$SITIO_DIR/backup.sh"
sed -i "s|{{SITIO_DIR}}|$SITIO_DIR|g" "$SITIO_DIR/backup.sh"
sed -i "s|{{DB_ROOT_PASSWORD}}|$DB_ROOT_PASSWORD|g" "$SITIO_DIR/backup.sh"
chmod +x "$SITIO_DIR/backup.sh"

# Agregar a crontab
(crontab -l 2>/dev/null; echo "0 3 * * * $SITIO_DIR/backup.sh") | crontab -

log_info "✅ Backup configurado (diario 3 AM)"

# Paso 8: Verificar acceso HTTPS
log_info "🔒 Verificando HTTPS..."
sleep 5

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k "https://$DOMINIO" || echo "000")

if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ] || [ "$HTTP_CODE" == "301" ]; then
  log_info "✅ Sitio accesible en https://$DOMINIO (HTTP $HTTP_CODE)"
else
  log_warn "⚠️  Sitio responde con HTTP $HTTP_CODE - verificar Traefik"
  log_warn "    Puede tardar hasta 2 minutos en obtener certificado SSL"
fi

# Paso 9: Resumen final
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
  echo "   Password DB:   (ver archivo .env)"
  echo ""
  echo "   Configurar WordPress en: https://$DOMINIO/wp-admin/install.php"
  echo ""
fi

echo "📝 Comandos útiles:"
echo "   Ver logs:      podman logs -f ${CLIENTE_SLUG}-web"
echo "   Reiniciar:     cd $SITIO_DIR && podman-compose restart"
echo "   Detener:       cd $SITIO_DIR && podman-compose down"
echo "   Backup manual: $SITIO_DIR/backup.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"