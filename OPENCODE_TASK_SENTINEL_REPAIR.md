# TAREA OPENCODE: Reparar sentinel post-accidente chown

## Contexto del problema

En el nodo `sentinel` (IP: 10.10.10.2, SSH puerto 4222) ocurrió un `chown -R 100999:100999 /`
accidental que cambió el ownership de TODO el filesystem. El uid 100999 es el subuid de Podman
rootless (no root). Esto rompió permisos de servicios del sistema.

**Acceso SSH**: `ssh -p 4222 -i ~/.ssh/google_compute_engine jnovoas@10.10.10.2`

---

## TAREA 1: Levantar servicios Podman (docker-compose.yml)

### Diagnóstico previo (ya realizado)
- `podman ps -a` retorna vacío — todos los contenedores caídos post-reboot
- El compose está en: `~/Dev/sentinel/docker-compose.yml`
- Servicios esperados: sentinel-backend, sentinel-frontend, sentinel-postgres,
  sentinel-redis, sentinel-n8n, sentinel-grafana, sentinel-prometheus, sentinel-loki,
  sentinel-promtail, sentinel-node-exporter, sentinel-guacd, sentinel-guacamole

### Pasos a ejecutar

```bash
# 1. Ir al directorio del proyecto
cd /home/jnovoas/Dev/sentinel

# 2. Verificar volúmenes existentes
podman volume ls

# 3. Levantar todos los servicios
podman-compose up -d

# 4. Verificar que arrancaron
podman ps --format 'table {{.Names}}\t{{.Status}}'

# 5. Para servicios que fallen, ver logs específicos:
podman logs <nombre_contenedor> --tail 20
```

### Errores esperados y cómo resolverlos

**Si Loki falla con "enforce_metric_name"**:
- Ya fue corregido anteriormente. Si persiste, verificar:
  `cat ~/Dev/sentinel/observability/loki/loki-config.yml | grep enforce`

**Si algún contenedor falla por permisos en volúmenes**:
- Identificar el volumen: `podman volume inspect sentinel_<nombre>_data`
- Verificar ownership del mountpoint
- Corregir con: `sudo chown -R <uid_correcto>:<gid_correcto> <mountpoint>`
- Para contenedores que corren como uid=1000 internamente: host uid = 100999
  (Podman rootless mapping: container uid 1000 → host uid 100999)

**NUNCA ejecutar chown sin validar la ruta primero**:
```bash
RUTA=$(podman volume inspect sentinel_nombre_data --format '{{.Mountpoint}}')
echo "Ruta a modificar: $RUTA"  # VERIFICAR antes de continuar
[ -n "$RUTA" ] || { echo "ERROR: ruta vacia, abortando"; exit 1; }
sudo chown -R 100999:100999 "$RUTA"
```

---

## TAREA 2: Reparar pdns.service

### Diagnóstico previo (ya realizado)

Error actual:
```
PDNSException: Unable to launch gsqlite3 connection:
Could not connect to the SQLite database '/var/lib/powerdns/pdns-secondary.db'
```

Causa: `/var/lib/powerdns/` tiene ownership 100999 en vez de pdns:pdns

### Pasos a ejecutar

```bash
# 1. Verificar estado actual de /var/lib/powerdns/
ls -la /var/lib/powerdns/

# 2. Verificar usuario pdns
id pdns

# 3. Corregir ownership del directorio y la BD
sudo chown -R pdns:pdns /var/lib/powerdns/
sudo chmod 750 /var/lib/powerdns/

# 4. Verificar que la BD existe y tiene datos
sudo -u pdns sqlite3 /var/lib/powerdns/pdns-secondary.db ".tables" 2>/dev/null \
  || echo "BD no existe o está vacía"

# 5. Si la BD no existe, crearla vacía (sentinel es slave, no necesita datos propios)
sudo -u pdns touch /var/lib/powerdns/pdns-secondary.db
sudo chmod 640 /var/lib/powerdns/pdns-secondary.db

# 6. Reiniciar pdns
sudo systemctl restart pdns
sleep 3
sudo systemctl status pdns --no-pager | head -15

# 7. Verificar que arrancó como slave
sudo journalctl -u pdns -n 10 --no-pager
```

### Si pdns aún falla tras corregir permisos

Verificar que pdns.conf es correcto:
```bash
sudo cat /etc/powerdns/pdns.conf
```

El pdns en sentinel es **slave** de centurion (10.10.10.6). Debe tener algo como:
```ini
launch=gsqlite3
gsqlite3-database=/var/lib/powerdns/pdns-secondary.db
slave=yes
superslave=yes
```

Si el archivo está corrupto o vacío, reconstruir desde centurion:
```bash
# En centurion (como referencia) — no tocar, solo leer
ssh -p 4222 jnovoas@10.10.10.6 "cat /etc/powerdns/pdns.conf"
```

---

## TAREA 3 (BONUS): Reparar /etc/ ownership sistémico

El `chown -R 100999:100999 /` afectó casi todo `/etc/`. Esto causa fallos en:
- `samba-ad-dc.service` (falla)
- `exim4.service` (falla)
- `audit-rules.service` (falla)
- Posibles otros servicios

### Fix sistémico para /etc/

```bash
# Restaurar ownership root para todo /etc/ de forma segura
# EXCEPTO archivos que legítimamente pertenecen a otros usuarios

# Ver qué está mal en /etc/
sudo find /etc/ -uid 100999 | head -20

# Contar cuántos archivos afectados
sudo find /etc/ -uid 100999 | wc -l

# Si son muchos (>100), restaurar en bloque con exclusiones
sudo find /etc/ -uid 100999 \
  ! -path "/etc/powerdns/pdns.conf" \
  -exec chown root:root {} \;

# Para archivos que necesitan usuarios específicos:
sudo chown pdns:pdns /etc/powerdns/pdns.conf
sudo chown pdns:pdns /etc/powerdns/pdns.d/ 2>/dev/null || true
```

### Fix para /var/lib/

```bash
# Ver qué servicios tienen directorios con ownership incorrecto
sudo find /var/lib/ -maxdepth 2 -uid 100999 2>/dev/null | head -20

# Los directorios críticos a revisar:
# - /var/lib/powerdns/ → pdns:pdns
# - /var/lib/postgresql/ → postgres:postgres (si existe)
# - /var/lib/samba/ → root:root
# - /var/log/ → root:root o usuario específico por servicio
```

---

## ENTREGABLE ESPERADO

Reporte en formato:
```
RESULTADO [OPENCODE] [SENTINEL-REPAIR]:
- Estado: COMPLETADO | PARCIAL | FALLIDO
- Podman servicios activos: <lista de contenedores UP>
- pdns.service: ACTIVO | FALLIDO | <error>
- /etc/ ownership reparado: SI | PARCIAL | NO
- Issues encontrados: <lista>
- Recomendación: <siguiente paso>
```

---

## RESTRICCIONES CRÍTICAS

- NO docker — solo `podman` y `podman-compose`
- NUNCA `chown -R` con variable sin validar antes
- NUNCA `chown -R` sobre `/`, `/etc`, `/proc`, `/sys`, `/boot`
- Antes de cualquier chown: imprimir la ruta y verificar que no está vacía
- Si un comando falla, reportar el error — no reintentar en bucle
