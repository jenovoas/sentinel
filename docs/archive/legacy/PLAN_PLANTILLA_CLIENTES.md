# Plan: Sistema de Plantillas para Sitios de Clientes
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


**Objetivo:** Crear un sistema estandarizado para agregar sitios de clientes en minutos, con CI/CD automatizado, SSL, backups y monitoreo incluidos.

**Stack:**

- **Traefik** (reverse proxy + SSL automático)
- **Podman/Docker** (contenedores)
- **GitLab CI** o **GitHub Actions** (opcional: CI/CD)
- **PowerDNS** (gestión DNS)
- **Restic** (backups automatizados)

---

## Arquitectura

```
Cliente solicita → Ejecutar script → Contenedor levantado → DNS configurado → SSL activado → Sitio online
                                                                                    ↓
                                                                        Backups + Monitoreo automáticos
```

**Tiempo objetivo:** < 15 minutos por cliente

---

## Fase 1: Estructura de Directorios

### 1.1 Crear jerarquía estándar

```bash
mkdir -p ~/clientes/{plantillas,sitios,backups,scripts}
cd ~/clientes

# Estructura:
# ~/clientes/
#   ├── plantillas/          # Templates de stack (Next.js, WordPress, Static, etc)
#   ├── sitios/              # Sitios activos de clientes
#   │   ├── laespiguita/
#   │   ├── clienteX/
#   │   └── clienteY/
#   ├── backups/             # Backups centralizados
#   └── scripts/             # Scripts de automatización
```

---

## Fase 2: Plantillas de Stack

### 2.1 Plantilla Next.js (SPA/SSR)

```bash
mkdir -p ~/clientes/plantillas/nextjs
cd ~/clientes/plantillas/nextjs
```

**Archivo: `compose.template.yaml`**

```yaml
services:
  {{CLIENTE_SLUG}}-web:
    image: node:20-alpine
    container_name: {{CLIENTE_SLUG}}-web
    restart: unless-stopped
    working_dir: /app
    volumes:
      - ./.next/standalone:/app:Z
      - ./.next/static:/app/.next/static:Z
      - ./public:/app/public:Z
    environment:
      - NODE_ENV=production
      - PORT=3000
      - HOSTNAME=0.0.0.0
      - DATABASE_URL={{DATABASE_URL}}
    command: ["node", "server.js"]
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.rule=Host(`{{DOMINIO}}`) || Host(`www.{{DOMINIO}}`)"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.entrypoints=websecure"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.tls.certresolver=powerdns"
      - "traefik.http.services.{{CLIENTE_SLUG}}.loadbalancer.server.port=3000"
      - "traefik.http.middlewares.{{CLIENTE_SLUG}}-redirect.redirectregex.regex=^https://www\\.{{DOMINIO_ESCAPED}}/(.*)"
      - "traefik.http.middlewares.{{CLIENTE_SLUG}}-redirect.redirectregex.replacement=https://{{DOMINIO}}/$${1}"
      - "traefik.http.middlewares.{{CLIENTE_SLUG}}-redirect.redirectregex.permanent=true"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.middlewares={{CLIENTE_SLUG}}-redirect"

networks:
  proxy:
    external: true
```

### 2.2 Plantilla WordPress

**Archivo: `~/clientes/plantillas/wordpress/compose.template.yaml`**

```yaml
services:
  {{CLIENTE_SLUG}}-db:
    image: mariadb:11
    container_name: {{CLIENTE_SLUG}}-db
    restart: unless-stopped
    networks:
      - {{CLIENTE_SLUG}}-internal
    environment:
      - MYSQL_ROOT_PASSWORD={{DB_ROOT_PASSWORD}}
      - MYSQL_DATABASE={{CLIENTE_SLUG}}_wp
      - MYSQL_USER={{CLIENTE_SLUG}}_user
      - MYSQL_PASSWORD={{DB_PASSWORD}}
    volumes:
      - ./db-data:/var/lib/mysql

  {{CLIENTE_SLUG}}-web:
    image: wordpress:6-php8.2-fpm-alpine
    container_name: {{CLIENTE_SLUG}}-web
    restart: unless-stopped
    depends_on:
      - {{CLIENTE_SLUG}}-db
    networks:
      - {{CLIENTE_SLUG}}-internal
      - proxy
    environment:
      - WORDPRESS_DB_HOST={{CLIENTE_SLUG}}-db
      - WORDPRESS_DB_NAME={{CLIENTE_SLUG}}_wp
      - WORDPRESS_DB_USER={{CLIENTE_SLUG}}_user
      - WORDPRESS_DB_PASSWORD={{DB_PASSWORD}}
      - WORDPRESS_CONFIG_EXTRA=define('WP_HOME', 'https://{{DOMINIO}}'); define('WP_SITEURL', 'https://{{DOMINIO}}');
    volumes:
      - ./wp-content:/var/www/html/wp-content
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.rule=Host(`{{DOMINIO}}`)"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.entrypoints=websecure"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.tls.certresolver=powerdns"
      - "traefik.http.services.{{CLIENTE_SLUG}}.loadbalancer.server.port=80"

networks:
  {{CLIENTE_SLUG}}-internal:
  proxy:
    external: true
```

### 2.3 Plantilla HTML Estático (Nginx)

**Archivo: `~/clientes/plantillas/static/compose.template.yaml`**

```yaml
services:
  {{CLIENTE_SLUG}}-web:
    image: nginx:alpine
    container_name: {{CLIENTE_SLUG}}-web
    restart: unless-stopped
    networks:
      - proxy
    volumes:
      - ./html:/usr/share/nginx/html:ro,Z
      - ./nginx.conf:/etc/nginx/nginx.conf:ro,Z
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.rule=Host(`{{DOMINIO}}`)"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.entrypoints=websecure"
      - "traefik.http.routers.{{CLIENTE_SLUG}}.tls.certresolver=powerdns"
      - "traefik.http.services.{{CLIENTE_SLUG}}.loadbalancer.server.port=80"

networks:
  proxy:
    external: true
```

---

## Fase 3: Script de Automatización

### 3.1 Script principal: `nuevo-cliente.sh`

**Archivo: `~/clientes/scripts/nuevo-cliente.sh`**

```bash
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
# docker-compose fallback removed - use podman-compose only on Fenix
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
```

**Hacer ejecutable:**

```bash
chmod +x ~/clientes/scripts/nuevo-cliente.sh
```

---

## Fase 4: Uso del Sistema

### 4.1 Crear nuevo cliente WordPress

```bash
~/clientes/scripts/nuevo-cliente.sh laespiguita laespiguita.cl wordpress
```

**Output esperado:**
```
[INFO] 🚀 Creando nuevo sitio para cliente: laespiguita
[INFO] 📦 Stack: wordpress
[INFO] 🌐 Dominio: laespiguita.cl
[INFO] 📁 Creando directorios...
[INFO] 📝 Procesando plantilla...
[INFO] ✅ Credenciales guardadas en /home/jnovoas/clientes/sitios/laespiguita/.env
[INFO] 🌍 Configurando DNS...
[INFO] 🐳 Levantando contenedores...
[INFO] ⏳ Esperando 10 segundos...
[INFO] ✅ Contenedor laespiguita-web corriendo
[INFO] 💾 Configurando backup automático...
[INFO] ✅ Backup configurado (diario 3 AM)
[INFO] 🔒 Verificando HTTPS...
[INFO] ✅ Sitio accesible en https://laespiguita.cl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[INFO] 🎉 ¡Sitio creado exitosamente!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Directorio:  /home/jnovoas/clientes/sitios/laespiguita
🌐 URL:         https://laespiguita.cl
🐳 Contenedor:  laespiguita-web
💾 Backups:     ~/clientes/backups/laespiguita/

🔑 Credenciales WordPress:
   Base de datos: laespiguita_wp
   Usuario DB:    laespiguita_user
   Password DB:   (ver archivo .env)

   Configurar WordPress en: https://laespiguita.cl/wp-admin/install.php
```

### 4.2 Crear cliente Next.js

```bash
# Primero copiar build de Next.js al directorio del cliente
~/clientes/scripts/nuevo-cliente.sh clienteX clientex.com nextjs

# Luego copiar los archivos del build
cp -r /ruta/al/build/.next/standalone ~/clientes/sitios/clienteX/.next/standalone
cp -r /ruta/al/build/.next/static ~/clientes/sitios/clienteX/.next/static
cp -r /ruta/al/build/public ~/clientes/sitios/clienteX/public

# Reiniciar contenedor
cd ~/clientes/sitios/clienteX && podman-compose restart
```

### 4.3 Crear sitio estático

```bash
~/clientes/scripts/nuevo-cliente.sh clienteY clientey.cl static

# Copiar archivos HTML
cp -r /ruta/html/* ~/clientes/sitios/clienteY/html/
```

---

## Fase 5: Gestión de Clientes

### 5.1 Listar todos los clientes

```bash
# Script: ~/clientes/scripts/listar-clientes.sh
#!/bin/bash
echo "Clientes activos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for cliente_dir in ~/clientes/sitios/*; do
  if [ -d "$cliente_dir" ]; then
    cliente=$(basename "$cliente_dir")
    compose_file="$cliente_dir/compose.yaml"

    if [ -f "$compose_file" ]; then
      dominio=$(grep "Host" "$compose_file" | head -1 | sed -E 's/.*Host\(`([^`]+)`\).*/\1/')
      status=$(podman ps --filter "name=$cliente" --format "{{.Status}}" | head -1 || echo "Detenido")

      printf "%-20s %-30s %s\n" "$cliente" "$dominio" "$status"
    fi
  fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

```bash
chmod +x ~/clientes/scripts/listar-clientes.sh
~/clientes/scripts/listar-clientes.sh
```

### 5.2 Eliminar cliente

```bash
# Script: ~/clientes/scripts/eliminar-cliente.sh
#!/bin/bash
if [ $# -lt 1 ]; then
  echo "Uso: $0 <nombre-cliente>"
  exit 1
fi

CLIENTE_SLUG="$1"
SITIO_DIR="$HOME/clientes/sitios/$CLIENTE_SLUG"

if [ ! -d "$SITIO_DIR" ]; then
  echo "Error: Cliente '$CLIENTE_SLUG' no encontrado"
  exit 1
fi

echo "⚠️  ADVERTENCIA: Esto eliminará el cliente '$CLIENTE_SLUG' y todos sus datos"
read -p "¿Estás seguro? (escribir 'eliminar' para confirmar): " confirmacion

if [ "$confirmacion" != "eliminar" ]; then
  echo "Cancelado"
  exit 0
fi

echo "🗑️  Deteniendo contenedores..."
cd "$SITIO_DIR" && podman-compose down -v

echo "💾 Creando backup final..."
BACKUP_DIR="$HOME/clientes/backups/$CLIENTE_SLUG/final"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/final_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$SITIO_DIR" .

echo "🗑️  Eliminando directorio..."
rm -rf "$SITIO_DIR"

echo "✅ Cliente '$CLIENTE_SLUG' eliminado"
echo "📦 Backup final en: $BACKUP_DIR"
```

```bash
chmod +x ~/clientes/scripts/eliminar-cliente.sh
```

---

## Fase 6: Monitoreo Centralizado

### 6.1 Dashboard Grafana para clientes

**Crear dashboard con métricas de todos los sitios:**

```json
{
  "dashboard": {
    "title": "Clientes - Monitoreo General",
    "panels": [
      {
        "title": "Contenedores Activos",
        "targets": [
          {
            "expr": "count(container_last_seen{name=~\".*-web\"})"
          }
        ]
      },
      {
        "title": "CPU por Cliente",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{name=~\".*-web\"}[5m])"
          }
        ]
      },
      {
        "title": "Memoria por Cliente",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{name=~\".*-web\"}"
          }
        ]
      },
      {
        "title": "Requests HTTP (últimas 24h)",
        "targets": [
          {
            "expr": "sum by (service) (rate(traefik_service_requests_total[24h]))"
          }
        ]
      }
    ]
  }
}
```

### 6.2 Alertas Prometheus

**Archivo: `~/containers/prometheus/alerts/clientes.yml`**

```yaml
groups:
  - name: clientes
    interval: 1m
    rules:
      - alert: SitioClienteDown
        expr: up{job="traefik"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Sitio de cliente caído"
          description: "El sitio {{ $labels.service }} no responde hace 5 minutos"

      - alert: AltaLatencia
        expr: traefik_service_request_duration_seconds_sum > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Alta latencia en {{ $labels.service }}"
```

---

## Fase 7: CI/CD Automatizado (Opcional)

### 7.1 GitHub Actions para deploy automático

**Archivo: `.github/workflows/deploy-cliente.yml`**

```yaml
name: Deploy Cliente

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Next.js
        run: |
          npm ci
          npm run build

      - name: Deploy a Fenix
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.FENIX_HOST }}
          username: ${{ secrets.FENIX_USER }}
          key: ${{ secrets.FENIX_SSH_KEY }}
          source: ".next/standalone,.next/static,public"
          target: "~/clientes/sitios/${{ secrets.CLIENTE_SLUG }}/"

      - name: Restart Container
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.FENIX_HOST }}
          username: ${{ secrets.FENIX_USER }}
          key: ${{ secrets.FENIX_SSH_KEY }}
          script: |
            cd ~/clientes/sitios/${{ secrets.CLIENTE_SLUG }}
            podman-compose restart
```

---

## Checklist de Implementación

- [ ] Estructura de directorios creada
- [ ] Plantillas nextjs/wordpress/static configuradas
- [ ] Script `nuevo-cliente.sh` ejecutable
- [ ] Script `listar-clientes.sh` ejecutable
- [ ] Script `eliminar-cliente.sh` ejecutable
- [ ] Red `proxy` de Podman existente
- [ ] Traefik configurado y corriendo
- [ ] PowerDNS accesible para agregar records
- [ ] Backups automatizados (crontab)
- [ ] Dashboard Grafana para monitoreo (opcional)
- [ ] Alertas Prometheus configuradas (opcional)

---

## Comandos de Referencia Rápida

```bash
# Crear nuevo cliente
~/clientes/scripts/nuevo-cliente.sh nombre-cliente dominio.com tipo-stack

# Listar clientes
~/clientes/scripts/listar-clientes.sh

# Ver logs de cliente
podman logs -f nombre-cliente-web

# Reiniciar cliente
cd ~/clientes/sitios/nombre-cliente && podman-compose restart

# Backup manual
~/clientes/sitios/nombre-cliente/backup.sh

# Eliminar cliente
~/clientes/scripts/eliminar-cliente.sh nombre-cliente
```

---

## Recursos

- [Traefik Docker Provider](https://doc.traefik.io/traefik/providers/docker/)
- [Podman Compose](https://github.com/containers/podman-compose)
- [WordPress Docker](https://hub.docker.com/_/wordpress)
- [Restic Backups](https://restic.net/)

---

**Tiempo estimado implementación completa:** 6-8 horas
**Tiempo creación cliente después:** < 15 minutos
**Costo adicional por cliente:** $0 (recursos compartidos en fenix)