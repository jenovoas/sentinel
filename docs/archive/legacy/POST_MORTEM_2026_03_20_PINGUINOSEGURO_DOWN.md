# 🚨 Post-Mortem: Incidente www.pinguinoseguro.cl
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.

## 20 de Marzo 2026 - Sitio Principal Caído Durante Revisión de Inversores

**Fecha del incidente:** 2026-03-20  
**Duración estimada:** Desconocida (sitio cayó en build anterior)  
**Impacto:** Revisión de inversores comprometida - sitio principal inaccesible  
**Severidad:** 🔴 CRÍTICO

---

## 📊 Resumen Ejecutivo

El sitio principal **www.pinguinoseguro.cl** estuvo inaccesible durante una revisión de inversores programada. El problema fue causado por:

1. **Build de Next.js incompleto** - El contenedor no se levantó correctamente
2. **Red proxy desconectada** - El contenedor `pinguinoseguro-web` no estaba en la red `proxy` de Traefik
3. **Falta de monitoreo** - No hay alertas configuradas para el sitio principal
4. **IA alucinando en bucle** - Gemini realizó cambios sin verificar el resultado real

**Tiempo de resolución:** ~45 minutos desde diagnóstico hasta solución

---

## 🔍 Cronología del Incidente

### Antes del Incidente

- **Estado desconocido:** No hay registro de cuándo cayó el sitio exactamente
- **Builds previos:** Posiblemente fallidos o incompletos
- **Monitoreo:** Inexistente para el sitio principal

### Detección

```
Usuario reporta: "perdí una revisión de inversores.... fueron a mirar y el sitio estaba abajo"
```

- **Síntoma:** HTTP 502 Bad Gateway en https://www.pinguinoseguro.cl
- **DNS:** Correctamente configurado (34.28.226.63)
- **Traefik:** Configuración correcta apuntando a `pinguinoseguro-web:3000`
- **Contenedor:** Inexistente o no conectado a la red

### Diagnóstico

```bash
# 1. Verificar estado del sitio
curl -sI https://www.pinguinoseguro.cl
# Resultado: HTTP/2 502

# 2. Verificar contenedores
podman ps | grep pinguinoseguro
# Resultado: Solo pinguinoseguro_db (la web NO estaba)

# 3. Verificar config de Traefik
cat /home/jnovoas/containers/traefik/config/dynamic/sentinel.yml
# Resultado: Config correcta, apunta a pinguinoseguro-web:3000

# 4. Verificar proyecto
ls -la /home/jnovoas/Desarrollo/pinguinoseguro_web/
# Resultado: Proyecto existe, tiene build (.next/)
```

### Causa Raíz

**Problema 1: Contenedor no levantado**
- El compose.yaml existe pero el contenedor no estaba corriendo
- Posible causa: Build anterior falló o contenedor crashó sin restart

**Problema 2: Red proxy desconectada**
```bash
# Después de levantar el contenedor:
podman network inspect proxy | grep pinguinoseguro-web
# Resultado: NO ESTABA en la red proxy

# Traefik NO puede conectar al backend
podman exec traefik wget -qO- http://pinguinoseguro-web:3000
# Resultado: wget: bad address 'pinguinoseguro-web:3000'
```

**Problema 3: IA alucinando en bucle**
- Gemini realizó múltiples cambios sin verificar el estado real
- No hubo validación empírica después de cada cambio
- El agente no siguió el principio YATRA de "Verificación Antes de Finalizar"

---

## 🛠️ Proceso de Resolución

### Paso 1: Levantar el contenedor

```bash
cd /home/jnovoas/Desarrollo/pinguinoseguro_web
podman-compose up -d --build
```

**Output esperado:**
```
[4/4] STEP 14/14: CMD ["node", "server.js"]
Successfully tagged localhost/pinguinoseguro_web:latest
pinguinoseguro-web
pinguinoseguro_db
```

### Paso 2: Verificar que Next.js esté corriendo

```bash
podman logs pinguinoseguro-web
# Debe mostrar:
# ✓ Starting...
# ✓ Ready in XXXms
```

### Paso 3: Conectar a la red proxy

```bash
# Verificar que NO está en la red
podman network inspect proxy | grep pinguinoseguro-web
# (vacío = no está conectado)

# Conectar manualmente
podman network connect proxy pinguinoseguro-web
```

### Paso 4: Verificar conectividad desde Traefik

```bash
podman exec traefik wget -qO- http://pinguinoseguro-web:3000 | head -5
# Debe retornar HTML de la página
```

### Paso 5: Verificar acceso público

```bash
curl -sI https://www.pinguinoseguro.cl
# Debe retornar: HTTP/2 200
```

---

## ✅ Verificación Post-Resolución

### Estado Actual

```bash
# Sitio principal
curl -sI https://www.pinguinoseguro.cl
# HTTP/2 200 ✅

# Redirección desde non-www
curl -sI https://pinguinoseguro.cl
# HTTP/2 308 → https://www.pinguinoseguro.cl/ ✅

# Todos los sitios activos
curl -sI https://laespiguita.pinguinoseguro.cl     # 200 ✅
curl -sI https://portfolio.pinguinoseguro.cl       # 200 ✅
curl -sI https://grafana.pinguinoseguro.cl         # 200 ✅
curl -sI https://cortex.pinguinoseguro.cl          # 200 ✅
```

### Contenedores Operativos

```bash
podman ps --format "table {{.Names}}\t{{.Status}}"
# pinguinoseguro-web    Up XX minutes
# pinguinoseguro_db     Up X hours (healthy)
```

---

## 📋 Lecciones Aprendidas

### 1. **NUNCA confiar en IA sin verificación empírica**

**Lo que pasó:**
- Gemini realizó cambios asumiendo que funcionaban
- No verificó el estado real del sitio después de cada cambio
- Entró en bucle de "alucinación" (cambios sin efecto real)

**Prevención:**
```markdown
## Regla de Oro YATRA para IA:

DESPUÉS DE CUALQUIER CAMBIO:
1. Ejecutar comando de verificación REAL
2. Capturar output REAL
3. Comparar con estado esperado
4. Si no coincide → PARAR y replantear

NUNCA asumir que un cambio funcionó sin evidencia empírica.
```

### 2. **Falta de Monitoreo del Sitio Principal**

**Lo que pasó:**
- No hay alertas para www.pinguinoseguro.cl
- Nadie notificó que el sitio estaba caído
- Solo se descubrió cuando los inversores fueron a visitar

**Prevención:**
```bash
# Agregar a /etc/cron.minutely o systemd timer
#!/bin/bash
# /usr/local/bin/check-pinguinoseguro.sh

STATUS=$(curl -sI -o /dev/null -w "%{http_code}" https://www.pinguinoseguro.cl)

if [ "$STATUS" -ne 200 ]; then
  # Enviar alerta por email/telegram/slack
  echo "ALERTA: www.pinguinoseguro.cl retornó HTTP $STATUS" | \
    mail -s "🚨 SITIO PRINCIPAL CAÍDO" admin@pinguinoseguro.cl
  
  # Intentar restart automático (opcional, con cuidado)
  # cd /home/jnovoas/Desarrollo/pinguinoseguro_web && podman-compose restart
fi
```

### 3. **Red Proxy Desconectada Sin Detección**

**Lo que pasó:**
- El contenedor se levantó pero no se conectó a la red `proxy`
- Traefik no podía resolver el hostname
- HTTP 502 porque el backend era inalcanzable

**Prevención:**
```bash
# Script de verificación post-deploy
#!/bin/bash
# verify-network-connection.sh

CONTAINER=$1
NETWORK="proxy"

if ! podman network inspect $NETWORK | grep -q "$CONTAINER"; then
  echo "❌ $CONTAINER NO está en red $NETWORK"
  echo "Conectando..."
  podman network connect $NETWORK $CONTAINER
  
  # Verificar conectividad desde Traefik
  if podman exec traefik wget -qO- http://$CONTAINER:3000 > /dev/null 2>&1; then
    echo "✅ Conectividad verificada"
  else
    echo "❌ Conectividad FALLIDA - investigar"
    exit 1
  fi
fi
```

### 4. **Build de Next.js Sin Validación**

**Lo que pasó:**
- El compose.yaml usa volúmenes mounteados desde `.next/standalone`
- Si el build falla o está incompleto, el contenedor arranca pero sin la app
- Next.js puede iniciar pero servir contenido vacío o error

**Prevención:**
```bash
# Agregar healthcheck al compose.yaml
services:
  pinguinoseguro-web:
    # ... config existente ...
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 🛡️ Acciones Correctivas Implementadas

### Inmediatas (Completadas)

- [x] Sitio principal restaurado
- [x] Contenedor conectado a red proxy
- [x] Verificación de todos los sitios activos
- [x] Documentación del incidente creada

### Corto Plazo (1-7 días)

- [ ] Agregar healthcheck al compose.yaml de pinguinoseguro_web
- [ ] Script de monitoreo con alertas (cron + email/telegram)
- [ ] Dashboard de estado en Grafana para sitios críticos
- [ ] Documentar procedimiento de deploy válido

### Medio Plazo (1-4 semanas)

- [ ] CI/CD automatizado con verificación post-deploy
- [ ] Rollback automático si healthcheck falla
- [ ] Página de status pública (status.pinguinoseguro.cl)
- [ ] Runbook de incidentes para todo el equipo

### Largo Plazo (1-3 meses)

- [ ] Multi-región o failover automático
- [ ] Monitoreo de experiencia de usuario real (RUM)
- [ ] Alertas proactivas (latencia, errores 5xx, etc.)
- [ ] Revisión trimestral de post-mortems

---

## 📝 Procedimiento de Deploy Seguro (Nuevo)

### Pre-Deploy

```bash
# 1. Verificar estado actual
curl -sI https://www.pinguinoseguro.cl | grep HTTP
# Debe ser 200 antes de empezar

# 2. Backup del estado actual
podman inspect pinguinoseguro-web > /tmp/web-inspect-backup.json
```

### Deploy

```bash
cd /home/jnovoas/Desarrollo/pinguinoseguro_web

# 3. Build
podman-compose build

# 4. Levantar
podman-compose up -d

# 5. Esperar inicio
sleep 15
```

### Post-Deploy Verification

```bash
# 6. Verificar logs
podman logs pinguinoseguro-web | tail -5
# Debe mostrar: ✓ Ready in XXXms

# 7. Verificar red
podman network inspect proxy | grep pinguinoseguro-web
# Debe mostrar el contenedor

# 8. Verificar conectividad desde Traefik
podman exec traefik wget -qO- http://pinguinoseguro-web:3000 | head -1
# Debe retornar HTML

# 9. Verificar acceso público
STATUS=$(curl -sI -o /dev/null -w "%{http_code}" https://www.pinguinoseguro.cl)
if [ "$STATUS" -eq 200 ]; then
  echo "✅ Deploy exitoso"
else
  echo "❌ Deploy FALLIDO - HTTP $STATUS"
  echo "Iniciando rollback..."
  podman-compose down
  # Restaurar backup
fi
```

---

## 🎯 Checklist de Prevención de Incidentes

### Diario

- [ ] Verificar HTTP 200 en www.pinguinoseguro.cl
- [ ] Revisar logs de errores de Traefik
- [ ] Verificar salud de contenedores críticos

### Semanal

- [ ] Revisar métricas de rendimiento (latencia, errores)
- [ ] Verificar backups de bases de datos
- [ ] Actualizar dependencias de seguridad

### Mensual

- [ ] Simular failover de contenedores
- [ ] Revisar y actualizar runbooks
- [ ] Auditoría de accesos y permisos

### Por Incidente

- [ ] Documentar post-mortem dentro de 24h
- [ ] Implementar al menos 1 acción correctiva
- [ ] Actualizar procedimientos según lecciones aprendidas

---

## 📞 Contactos de Emergencia

| Rol | Contacto | Método |
|-----|----------|--------|
| Admin Sistema | jnovoas | Email/Telegram |
| Backup Admin | [pendiente] | [pendiente] |
| Inversores | [pendiente] | Email |

---

## 📎 Apéndice: Comandos de Referencia

### Verificar Estado de Sitios

```bash
# Todos los sitios
for site in www.pinguinoseguro.cl laespiguita.pinguinoseguro.cl portfolio.pinguinoseguro.cl grafana.pinguinoseguro.cl; do
  STATUS=$(curl -sI -o /dev/null -w "%{http_code}" https://$site)
  echo "$site: HTTP $STATUS"
done
```

### Verificar Contenedores Críticos

```bash
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | \
  grep -E "pinguinoseguro|traefik|cortex"
```

### Verificar Red Proxy

```bash
podman network inspect proxy | \
  python3 -c "import sys,json; data=json.load(sys.stdin); \
  print('Containers en red proxy:'); \
  [print(f'  - {v.get(\"name\", \"unknown\")}') for v in data[0].get('containers', {}).values()]"
```

### Logs Recientes de Errores

```bash
# Traefik (últimos 50 logs con errores)
podman logs traefik 2>&1 | grep -i "error\|502\|backend" | tail -50

# pinguinoseguro-web
podman logs pinguinoseguro-web 2>&1 | tail -100
```

---

**Documento creado:** 2026-03-20  
**Próxima revisión:** 2026-04-20  
**Responsable actualización:** Equipo de Infraestructura

---

## 🧠 Nota Final para IA Agents

**Este documento es OBLIGATORIO de leer antes de cualquier deploy o cambio en producción.**

Los principios YATRA aplican:
1. **Verificación empírica** - Nunca asumir, siempre verificar con comandos reales
2. **Impacto mínimo** - Cambios pequeños, verificables, reversibles
3. **Automejora** - Cada incidente genera al menos 1 mejora en procedimientos
4. **Elegancia** - Si un arreglo se siente apresurado, replantear

**NUNCA repetir este incidente.**