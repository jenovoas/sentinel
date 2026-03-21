# 🤖 n8n Workflows para Sentinel - Guía de Implementación

**Fecha**: 14 de Diciembre, 2025  
**Workflows disponibles**: 6  
**Estado**: ✅ Listos para importar

---

## 📋 Workflows Disponibles

### 1. Daily SLO Report
- **Archivo**: `1-daily-slo-report.json`
- **Frecuencia**: Diario a las 9:00 AM
- **Descripción**: Reporte diario con estadísticas de CPU, memoria y anomalías de las últimas 24 horas
- **Salida**: Mensaje formateado a Slack

### 2. High CPU Alert
- **Archivo**: `2-high-cpu-alert.json`
- **Frecuencia**: Cada 5 minutos
- **Descripción**: Alerta cuando el uso de CPU supera el 80%
- **Salida**: Notificación urgente a Slack

### 3. Anomaly Detector
- **Archivo**: `3-anomaly-detector.json`
- **Frecuencia**: Cada 15 minutos
- **Descripción**: Detecta y notifica anomalías críticas en la última hora
- **Salida**: Lista de hasta 5 anomalías más recientes

### 4. Database Health Check
- **Archivo**: `4-database-health-check.json`
- **Frecuencia**: Cada 6 horas
- **Descripción**: Monitorea conexiones activas, locks y tamaño de la base de datos
- **Salida**: Reporte de salud con indicadores de estado

### 5. Weekly Summary Report
- **Archivo**: `5-weekly-summary.json`
- **Frecuencia**: Lunes a las 10:00 AM
- **Descripción**: Resumen semanal completo con estadísticas de 7 días
- **Salida**: Reporte ejecutivo con métricas clave

### 6. Memory Warning Alert
- **Archivo**: `6-memory-warning-alert.json`
- **Frecuencia**: Cada 10 minutos
- **Descripción**: Alerta cuando el uso de memoria supera el 85%
- **Salida**: Notificación con severidad (Warning/Critical)

---

## 🚀 Guía de Importación Rápida

### Paso 1: Acceder a n8n
```
URL: http://localhost:5678
Usuario: admin
Password: REDACTED_PASSWORD
```

### Paso 2: Importar un Workflow

1. En n8n, haz clic en **"New"** → **"Workflow"**
2. Haz clic en el menú (⋮) → **"Import from File"** o **"Import from URL"**
3. Selecciona el archivo JSON del workflow que deseas importar
4. El workflow se cargará automáticamente en el canvas

### Paso 3: Configurar Variables de Entorno

Antes de activar los workflows, configura la variable de entorno para Slack:

#### Opción A: Configurar en n8n UI
1. Ve a **Settings** → **Environments**
2. Agrega: `SLACK_WEBHOOK_URL` = `tu_webhook_url_de_slack`

#### Opción B: Configurar en Docker Compose
Edita `podman-compose.yml`:
```yaml
n8n:
  environment:
    - SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Luego reinicia n8n:
```bash
podman-compose restart n8n
```

### Paso 4: Activar el Workflow

1. En el workflow importado, haz clic en el toggle **"Active"** (arriba a la derecha)
2. El workflow comenzará a ejecutarse según su schedule

---

## 🔧 Configuración de Slack Webhook

### Crear Webhook en Slack

1. Ve a https://api.slack.com/apps
2. Haz clic en **"Create New App"** → **"From scratch"**
3. Nombre: `Sentinel Bot`
4. Selecciona tu workspace
5. En **Features** → **Incoming Webhooks** → Activa el toggle
6. Haz clic en **"Add New Webhook to Workspace"**
7. Selecciona el canal donde quieres recibir notificaciones (ej: `#sentinel-alerts`)
8. Copia la URL del webhook (formato: `https://hooks.slack.com/services/T.../B.../XXX`)

### Probar el Webhook

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"✅ Sentinel Bot conectado!"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## 🧪 Probar Workflows sin Slack

Si aún no tienes Slack configurado, puedes probar los workflows con estas modificaciones:

### Opción 1: Usar Manual Trigger

1. Importa el workflow
2. Cambia el nodo **"Schedule Trigger"** por **"Manual Trigger"**
3. Haz clic en **"Execute Workflow"**
4. Verás el resultado en el panel de ejecución

### Opción 2: Usar Webhook Local

Reemplaza el nodo "Send to Slack" con un nodo HTTP Request que apunte a:
```
http://localhost:8000/api/v1/test-webhook
```

---

## 📊 Personalización de Workflows

### Cambiar Frecuencia de Ejecución

En el nodo **Schedule Trigger**, puedes modificar:

- **Cron Expression**: `0 9 * * *` (diario a las 9 AM)
- **Interval**: Cada X minutos/horas
- **Specific Times**: Horarios específicos

Ejemplos:
```
0 */6 * * *    # Cada 6 horas
0 8,12,18 * * * # A las 8 AM, 12 PM y 6 PM
0 0 * * 1      # Cada lunes a medianoche
```

### Cambiar Umbrales de Alerta

En los workflows de alertas, modifica los valores en el nodo **"IF"**:

```javascript
// CPU Alert - cambiar de 80% a 90%
"value2": 90

// Memory Alert - cambiar de 85% a 95%
"value2": 95
```

### Agregar Más Métricas

En el nodo **"Build Report"** (Code), puedes agregar más campos:

```javascript
const networkTX = (sample.network_bytes_sent / 1024 / 1024).toFixed(2);
const networkRX = (sample.network_bytes_recv / 1024 / 1024).toFixed(2);

// Agregar al texto del reporte
`*Network:* ${networkTX} MB sent, ${networkRX} MB received\n`
```

---

## 🔍 Monitoreo de Workflows

### Ver Ejecuciones

1. En n8n, ve a **"Executions"** (panel izquierdo)
2. Verás todas las ejecuciones recientes
3. Haz clic en una ejecución para ver detalles

### Logs de Ejecución

```bash
# Ver logs de n8n
podman-compose logs -f n8n

# Filtrar solo errores
podman-compose logs n8n | grep ERROR
```

### Verificar Estado de Workflows

```bash
# API de n8n para listar workflows
curl -s http://localhost:5678/api/v1/workflows | jq '.data[] | {name, active}'
```

---

## 🛠️ Troubleshooting

### Workflow no se ejecuta

**Problema**: El workflow está activo pero no se ejecuta

**Soluciones**:
1. Verifica que el toggle "Active" esté en verde
2. Revisa el schedule en el nodo Schedule Trigger
3. Espera al menos un ciclo completo (ej: si es cada 5 min, espera 5 min)
4. Prueba con "Execute Workflow" manualmente

### Error en nodo HTTP Request

**Problema**: `Error: connect ECONNREFUSED`

**Soluciones**:
1. Verifica que el backend esté corriendo: `podman-compose ps backend`
2. Usa `http://backend:8000` en lugar de `http://localhost:8000` (dentro de Docker)
3. Verifica la URL del endpoint en la API docs: http://localhost:8000/docs

### Slack no recibe mensajes

**Problema**: El workflow se ejecuta pero no llegan mensajes a Slack

**Soluciones**:
1. Verifica que `SLACK_WEBHOOK_URL` esté configurada correctamente
2. Prueba el webhook manualmente con `curl`
3. Revisa que el canal de Slack exista y el bot tenga permisos
4. Verifica los logs de ejecución en n8n

### Error de sintaxis en Code node

**Problema**: `SyntaxError` en el nodo de código

**Soluciones**:
1. Verifica que todas las comillas estén balanceadas
2. Asegúrate de usar `return { json: ... }` al final
3. Usa `console.log()` para debug y revisa los logs

---

## 📈 Workflows Avanzados (Próximos)

Ideas para workflows adicionales:

- **Disk Space Monitor**: Alerta cuando el disco supera el 80%
- **Service Restart Alert**: Notifica cuando un servicio se reinicia
- **Backup Verification**: Verifica que los backups se ejecuten correctamente
- **Performance Degradation**: Detecta degradación gradual del rendimiento
- **Security Audit**: Reporta eventos de seguridad sospechosos
- **Cost Tracking**: Monitorea costos de recursos (para cloud)

---

## 📝 Ejemplos de Mensajes

### Daily SLO Report
```
📊 *Sentinel Daily Report*

*Period:* Last 24 hours
*Date:* 2025-12-14

*CPU Usage:*
  • Average: 45.2%
  • Peak: 78.5%

*Memory Usage:*
  • Average: 62.1%
  • Peak: 75.3%

*Anomalies Detected:* 2

⚠️ Review anomalies in Grafana

_View details: http://localhost:3001_
```

### High CPU Alert
```
🚨 *HIGH CPU ALERT*

*CPU Usage:* 85.3% (Threshold: 80%)
*Memory Usage:* 62.1%
*Time:* 12/14/2025, 3:45:23 PM

⚠️ *Action Required*
Check Grafana dashboard for details
http://localhost:3001
```

### Weekly Summary
```
📅 *Sentinel Weekly Summary*

*Period:* Last 7 days
*Week ending:* 2025-12-14

*CPU Performance:*
  • Average: 42.5%
  • Peak: 92.1%
  • Minimum: 12.3%

*Memory Performance:*
  • Average: 58.7%
  • Peak: 82.4%

*Anomalies Summary:*
  • Total: 15
  • Critical: 3

*System Health:* 🟡 Good

_View detailed analytics: http://localhost:3001_
```

---

## ✅ Checklist de Implementación

- [ ] Acceder a n8n (http://localhost:5678)
- [ ] Crear Slack webhook
- [ ] Configurar `SLACK_WEBHOOK_URL` en n8n
- [ ] Importar workflow 1: Daily SLO Report
- [ ] Importar workflow 2: High CPU Alert
- [ ] Importar workflow 3: Anomaly Detector
- [ ] Importar workflow 4: Database Health Check
- [ ] Importar workflow 5: Weekly Summary
- [ ] Importar workflow 6: Memory Warning Alert
- [ ] Activar todos los workflows
- [ ] Probar ejecución manual de cada uno
- [ ] Verificar que lleguen mensajes a Slack
- [ ] Monitorear ejecuciones durante 24 horas

---

## 🎯 Mejores Prácticas

1. **Nombra tus workflows claramente**: Usa nombres descriptivos
2. **Documenta cambios**: Agrega notas en los nodos
3. **Prueba antes de activar**: Usa "Execute Workflow" primero
4. **Monitorea ejecuciones**: Revisa logs regularmente
5. **Ajusta umbrales**: Personaliza según tu sistema
6. **Evita spam**: No configures alertas muy frecuentes
7. **Usa variables de entorno**: Para credenciales y URLs
8. **Mantén backups**: Exporta workflows regularmente

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `podman-compose logs n8n`
2. Verifica la documentación oficial: https://docs.n8n.io
3. Prueba los endpoints manualmente: http://localhost:8000/docs
4. Revisa el estado de servicios: `podman-compose ps`

---

**¡Listo para automatizar!** 🚀

Comienza importando el workflow de Daily SLO Report y expande desde ahí.
