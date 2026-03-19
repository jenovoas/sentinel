# Plan: Obsidian Publish/LiveSync en Subdominio

**Objetivo:** Configurar Obsidian Publish self-hosted o LiveSync para sincronizar notas entre dispositivos, accesible en `obsidian.pinguinoseguro.cl`.

**Opciones:**

1. **Obsidian Publish (oficial, pago)** — $8/mes/sitio
2. **Obsidian LiveSync (self-hosted, gratis)** — CouchDB
3. **Quartz (static site generator)** — Gratis, solo lectura

**Recomendación para agencia:** **LiveSync** (gratis, sincronización bidireccional)

---

## Opción A: Obsidian LiveSync (Self-Hosted con CouchDB)

### Arquitectura

```
Obsidian Desktop/Mobile → HTTPS → Traefik → CouchDB (5984)
                                              ↓
                                    Base de datos notas sincronizadas
```

**Ventajas:**
- ✅ Gratis
- ✅ Sincronización en tiempo real
- ✅ End-to-end encryption
- ✅ Multi-dispositivo (Windows, Mac, Linux, Android, iOS)

---

## Fase 1: Instalar CouchDB con Docker/Podman

### 1.1 Crear directorio de trabajo

```bash
mkdir -p ~/containers/obsidian-livesync/{data,config}
cd ~/containers/obsidian-livesync
```

### 1.2 Crear compose.yaml

```yaml
services:
  couchdb:
    image: couchdb:3.3
    container_name: obsidian-couchdb
    restart: unless-stopped
    networks:
      - proxy
    ports:
      - "5984:5984"  # Solo para debug local
    environment:
      - COUCHDB_USER=admin
      - COUCHDB_PASSWORD=CambiarEstaClaveSegura456!
    volumes:
      - ./data:/opt/couchdb/data
      - ./config:/opt/couchdb/etc/local.d
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.obsidian.rule=Host(`obsidian.pinguinoseguro.cl`)"
      - "traefik.http.routers.obsidian.entrypoints=websecure"
      - "traefik.http.routers.obsidian.tls.certresolver=powerdns"
      - "traefik.http.services.obsidian.loadbalancer.server.port=5984"

      # CORS headers (necesarios para Obsidian)
      - "traefik.http.middlewares.obsidian-cors.headers.accesscontrolallowmethods=GET,POST,PUT,DELETE,OPTIONS"
      - "traefik.http.middlewares.obsidian-cors.headers.accesscontrolalloworiginlist=app://obsidian.md,capacitor://localhost,http://localhost"
      - "traefik.http.middlewares.obsidian-cors.headers.accesscontrolallowcredentials=true"
      - "traefik.http.middlewares.obsidian-cors.headers.accesscontrolallowheaders=*"
      - "traefik.http.routers.obsidian.middlewares=obsidian-cors"

networks:
  proxy:
    external: true
```

### 1.3 Levantar contenedor

```bash
podman-compose up -d
podman logs -f obsidian-couchdb
```

### 1.4 Verificar acceso

```bash
curl -u admin:CambiarEstaClaveSegura456! https://obsidian.pinguinoseguro.cl
# Debe devolver: {"couchdb":"Welcome","version":"3.3.3",...}
```

---

## Fase 2: Configurar CouchDB para Obsidian LiveSync

### 2.1 Habilitar CORS manualmente (si no funciona vía Traefik)

```bash
podman exec -it obsidian-couchdb bash

# Dentro del contenedor:
curl -X PUT http://admin:CambiarEstaClaveSegura456!@localhost:5984/_node/_local/_config/httpd/enable_cors -d '"true"'
curl -X PUT http://admin:CambiarEstaClaveSegura456!@localhost:5984/_node/_local/_config/cors/origins -d '"app://obsidian.md, capacitor://localhost, http://localhost"'
curl -X PUT http://admin:CambiarEstaClaveSegura456!@localhost:5984/_node/_local/_config/cors/credentials -d '"true"'
curl -X PUT http://admin:CambiarEstaClaveSegura456!@localhost:5984/_node/_local/_config/cors/methods -d '"GET, PUT, POST, HEAD, DELETE"'
curl -X PUT http://admin:CouchDB456!@localhost:5984/_node/_local/_config/cors/headers -d '"accept, authorization, content-type, origin, referer"'

exit
```

### 2.2 Crear base de datos para Obsidian

```bash
curl -X PUT https://admin:CambiarEstaClaveSegura456!@obsidian.pinguinoseguro.cl/obsidian
# Respuesta: {"ok":true}
```

### 2.3 Verificar base de datos

```bash
curl -u admin:CambiarEstaClaveSegura456! https://obsidian.pinguinoseguro.cl/_all_dbs
# Debe mostrar: ["_replicator","_users","obsidian"]
```

---

## Fase 3: Configurar Plugin Obsidian LiveSync

### 3.1 Instalar plugin en Obsidian Desktop

1. Abrir Obsidian
2. Settings → Community Plugins → Browse
3. Buscar: **"Self-hosted LiveSync"**
4. Install + Enable

### 3.2 Configurar conexión

**Settings → Self-hosted LiveSync → Setup:**

```
Remote Database URL: https://obsidian.pinguinoseguro.cl/obsidian
Username: admin
Password: CambiarEstaClaveSegura456!
Database name: obsidian
```

**Click "Test Database Connection"** → Debe mostrar: ✅ Connected

### 3.3 Configurar sincronización

**Settings → Self-hosted LiveSync:**

- ✅ **LiveSync enabled**
- ✅ **Sync on Save**
- ✅ **Sync on File Open**
- ✅ **Periodic Sync** (cada 60 segundos)
- ✅ **Use dynamic iteration chunking** (mejor rendimiento)

**End-to-End Encryption (opcional pero recomendado):**
- ✅ Enable End-to-End Encryption
- Passphrase: `TuClaveSeguraParaEncriptar123!`

**Click "Replicate Now"** → Sincroniza todo el vault

### 3.4 Verificar sincronización

```bash
# Ver documentos sincronizados
curl -u admin:CambiarEstaClaveSegura456! https://obsidian.pinguinoseguro.cl/obsidian/_all_docs
```

---

## Fase 4: Configurar Obsidian Mobile (Android/iOS)

### 4.1 Instalar Obsidian Mobile

- Android: Google Play Store
- iOS: App Store

### 4.2 Crear vault o abrir existente

1. Abrir Obsidian Mobile
2. Crear nuevo vault o importar existente

### 4.3 Instalar plugin LiveSync

1. Settings → Community Plugins → Enable
2. Browse → "Self-hosted LiveSync" → Install + Enable

### 4.4 Configurar (misma config que desktop)

```
Remote Database URL: https://obsidian.pinguinoseguro.cl/obsidian
Username: admin
Password: CambiarEstaClaveSegura456!
Database name: obsidian
Passphrase: TuClaveSeguraParaEncriptar123! (si usas E2EE)
```

**Click "Fetch from Remote"** → Descarga todas las notas

---

## Fase 5: Traefik Configuration (si autodiscovery falla)

**Crear configuración manual:**

```bash
cat > ~/containers/traefik/config/dynamic/obsidian.yml <<'EOF'
http:
  routers:
    obsidian:
      rule: "Host(`obsidian.pinguinoseguro.cl`)"
      entryPoints:
        - "websecure"
      service: "obsidian"
      middlewares:
        - "obsidian-cors"
      tls:
        certResolver: "powerdns"

  services:
    obsidian:
      loadBalancer:
        servers:
          - url: "http://obsidian-couchdb:5984"

  middlewares:
    obsidian-cors:
      headers:
        accessControlAllowMethods:
          - "GET"
          - "POST"
          - "PUT"
          - "DELETE"
          - "OPTIONS"
        accessControlAllowOriginList:
          - "app://obsidian.md"
          - "capacitor://localhost"
          - "http://localhost"
        accessControlAllowCredentials: true
        accessControlAllowHeaders:
          - "*"
        accessControlMaxAge: 100
        addVaryHeader: true
EOF
```

**Traefik recarga automáticamente.**

---

## Opción B: Quartz (Static Site Generator) — Solo Lectura

**Caso de uso:** Publicar notas públicas como documentación/blog.

### Arquitectura

```
Obsidian Vault → Quartz Build → Static HTML → Nginx/Caddy → Traefik
```

### Instalación

```bash
# 1. Clonar Quartz
cd ~/Desarrollo
git clone https://github.com/jackyzha0/quartz.git obsidian-quartz
cd obsidian-quartz

# 2. Instalar dependencias
npm install

# 3. Configurar vault source
npx quartz create

# Seleccionar: "Link an existing folder"
# Path: /ruta/a/tu/obsidian/vault

# 4. Build
npx quartz build

# 5. El output estará en public/
```

### Servir con Nginx en contenedor

```yaml
# compose.yaml
services:
  quartz:
    image: nginx:alpine
    container_name: obsidian-quartz
    restart: unless-stopped
    networks:
      - proxy
    volumes:
      - ./public:/usr/share/nginx/html:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.quartz.rule=Host(`docs.pinguinoseguro.cl`)"
      - "traefik.http.routers.quartz.entrypoints=websecure"
      - "traefik.http.routers.quartz.tls.certresolver=powerdns"
      - "traefik.http.services.quartz.loadbalancer.server.port=80"

networks:
  proxy:
    external: true
```

```bash
podman-compose up -d
```

**Acceder:** https://docs.pinguinoseguro.cl

---

## Fase 6: Backups Automatizados

### 6.1 Backup de CouchDB

```bash
# Script: ~/containers/obsidian-livesync/backup.sh
#!/bin/bash
BACKUP_DIR="/home/jnovoas/backups/obsidian"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup database dump
curl -u admin:CambiarEstaClaveSegura456! \
  https://obsidian.pinguinoseguro.cl/obsidian/_all_docs?include_docs=true \
  > "$BACKUP_DIR/obsidian_backup_$DATE.json"

# Compress
gzip "$BACKUP_DIR/obsidian_backup_$DATE.json"

# Cleanup old backups (mantener últimos 30 días)
find "$BACKUP_DIR" -name "*.json.gz" -mtime +30 -delete

echo "Backup completado: $BACKUP_DIR/obsidian_backup_$DATE.json.gz"
```

```bash
chmod +x ~/containers/obsidian-livesync/backup.sh
```

### 6.2 Cron job

```bash
crontab -e

# Backup diario a las 3 AM
0 3 * * * /home/jnovoas/containers/obsidian-livesync/backup.sh
```

---

## Fase 7: Seguridad

### 7.1 Autenticación robusta

**Opción 1: Cambiar credenciales CouchDB admin**

```bash
podman exec -it obsidian-couchdb bash

# Crear nuevo admin
curl -X PUT http://admin:CambiarEstaClaveSegura456!@localhost:5984/_node/_local/_config/admins/jaime -d '"NuevaClaveSegura789!"'

# Eliminar admin default (opcional)
curl -X DELETE http://admin:CambiarEstaClaveSegura456!@localhost:5984/_node/_local/_config/admins/admin
```

**Opción 2: Crear usuario específico para Obsidian**

```bash
# Crear usuario "obsidian-user" en CouchDB
curl -X PUT http://admin:CambiarEstaClaveSegura456!@localhost:5984/_users/org.couchdb.user:obsidian-user \
  -H "Content-Type: application/json" \
  -d '{
    "name": "obsidian-user",
    "password": "ClaveUsuarioObsidian123!",
    "roles": [],
    "type": "user"
  }'

# Dar permisos a la base de datos
curl -X PUT http://admin:CambiarEstaClaveSegura456!@localhost:5984/obsidian/_security \
  -H "Content-Type: application/json" \
  -d '{
    "members": {
      "names": ["obsidian-user"],
      "roles": []
    }
  }'
```

Usar `obsidian-user` en la configuración del plugin.

### 7.2 Rate Limiting

```yaml
# traefik/config/dynamic/obsidian.yml
http:
  middlewares:
    obsidian-ratelimit:
      rateLimit:
        average: 100
        burst: 50
        period: 1m

  routers:
    obsidian:
      middlewares:
        - "obsidian-cors"
        - "obsidian-ratelimit"
```

### 7.3 Firewall (opcional)

**Si solo tú usas LiveSync, restringir por IP:**

```yaml
# Traefik middleware: solo IPs permitidas
http:
  middlewares:
    obsidian-ipwhitelist:
      ipWhiteList:
        sourceRange:
          - "34.28.226.63/32"  # IP fenix
          - "TU_IP_CASA/32"    # Tu IP estática
          - "TU_IP_MOVIL/32"
```

---

## Fase 8: Monitoreo

### 8.1 Health check

```bash
# Script: ~/containers/obsidian-livesync/healthcheck.sh
#!/bin/bash
RESPONSE=$(curl -s -u admin:CambiarEstaClaveSegura456! https://obsidian.pinguinoseguro.cl)

if echo "$RESPONSE" | grep -q "couchdb"; then
  echo "✅ CouchDB OK"
  exit 0
else
  echo "❌ CouchDB DOWN"
  # Opcional: enviar alerta por email/Telegram
  exit 1
fi
```

### 8.2 Cron health check

```bash
crontab -e

# Health check cada 15 minutos
*/15 * * * * /home/jnovoas/containers/obsidian-livesync/healthcheck.sh
```

### 8.3 Métricas en Prometheus (opcional)

CouchDB expone métricas en `/_node/_local/_prometheus`:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'couchdb'
    static_configs:
      - targets: ['obsidian-couchdb:5984']
    metrics_path: '/_node/_local/_prometheus'
    basic_auth:
      username: admin
      password: CambiarEstaClaveSegura456!
```

---

## Troubleshooting

### Problema 1: CORS errors en Obsidian

**Síntoma:** Plugin dice "Connection failed: CORS error"

**Solución:**

1. Verificar headers CORS en Traefik
2. Verificar CORS en CouchDB:
   ```bash
   curl http://admin:pass@localhost:5984/_node/_local/_config/cors
   ```
3. Si no muestra configuración, ejecutar paso 2.1 de nuevo

### Problema 2: No sincroniza en mobile

**Síntoma:** Desktop sincroniza, mobile no

**Solución:**

1. Verificar que mobile tenga internet (no solo WiFi)
2. Verificar configuración E2EE (passphrase exacta)
3. Borrar y recrear configuración en mobile
4. Verificar logs en Settings → Self-hosted LiveSync → Show Logs

### Problema 3: Database muy grande

**Síntoma:** CouchDB ocupa demasiado espacio

**Solución: Compactar base de datos**

```bash
curl -X POST http://admin:pass@localhost:5984/obsidian/_compact \
  -H "Content-Type: application/json"

# Esperar a que termine (puede tomar minutos)
curl http://admin:pass@localhost:5984/obsidian | jq '.compact_running'
# Debe devolver: false
```

---

## Checklist Final

- [ ] CouchDB levantado en https://obsidian.pinguinoseguro.cl
- [ ] CORS configurado correctamente
- [ ] Base de datos "obsidian" creada
- [ ] Plugin instalado en Obsidian Desktop
- [ ] Sincronización funcionando Desktop ↔ Server
- [ ] E2EE configurado (si se usa)
- [ ] Plugin instalado en Obsidian Mobile
- [ ] Sincronización funcionando Mobile ↔ Server
- [ ] Backups automatizados configurados
- [ ] Health checks activos
- [ ] Rate limiting habilitado

---

## Recursos

- [Obsidian LiveSync Plugin](https://github.com/vrtmrz/obsidian-livesync)
- [CouchDB Documentation](https://docs.couchdb.org/)
- [Quartz Documentation](https://quartz.jzhao.xyz/)
- [Obsidian Forum - Self-Hosting](https://forum.obsidian.md/tag/self-hosting)

---

**Tiempo estimado:** 2-3 horas
**Costo mensual:** $0 (self-hosted)
**Alternativa pago:** Obsidian Sync oficial ($8/mes) — más simple pero menos control
