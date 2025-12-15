# Workflow n8n: SLO Alert - Notificación de Incidentes

Este workflow monitorea alertas de SLOs en Prometheus y envía notificaciones a Slack cada 5 minutos.

## 📋 Pasos para Crear el Workflow

### 1. Acceder a n8n
- URL: http://localhost:5678
- Usuario: admin
- Contraseña: darkfenix

### 2. Crear Nuevo Workflow
1. Click en "+ New" (parte superior)
2. Seleccionar "Workflow"
3. Se abrirá una pantalla vacía

### 3. Agregar Nodos

#### A. Nodo 1: Cron Trigger (Ejecutar cada 5 minutos)
1. En el canvas, buscar "Cron"
2. Seleccionar "Cron Trigger"
3. Configurar:
   - Unit: Minutes
   - Value: 5
   - Click "Add"

#### B. Nodo 2: HTTP Request (Leer alertas de Prometheus)
1. Conectar el Cron a un nuevo nodo
2. Buscar "HTTP Request"
3. Configurar:
   - Method: GET
   - URL: `http://prometheus:9090/api/v1/query?query=ALERTS{severity="critical"}`
   - Response: JSON

#### C. Nodo 3: IF - Verificar si hay alertas
1. Conectar HTTP Request a IF
2. Configurar condición:
   - Value 1: `{{ $json.data.result.length }}`
   - Operator: `>`
   - Value 2: `0`

#### D. Nodo 4: HTTP Request (Enviar a Slack)
1. Conectar IF (rama "true") a nuevo HTTP Request
2. Configurar:
   - Method: POST
   - URL: **REEMPLAZAR CON TU WEBHOOK DE SLACK**
   - Headers: `Content-Type: application/json`
   - Body (JSON):
   ```json
   {
     "text": "⚠️ SLO Alert Detectado!\n{{ $json.data.result.map(r => r.metric.alertname).join(', ') }}"
   }
   ```

### 4. Configurar Slack Webhook

#### Opción A: Si tienes cuenta de Slack
1. Ve a https://api.slack.com/apps
2. Click "Create New App"
3. Selecciona workspace
4. Ve a "Incoming Webhooks"
5. Click "Add New Webhook to Workspace"
6. Selecciona canal (ej: #alerts)
7. Copia la URL del Webhook
8. Pega en el Nodo 4 en lugar de `YOUR_SLACK_WEBHOOK_URL`

#### Opción B: Usar Slack Test Webhook (demo)
Si no tienes Slack, puedes usar un webhook de prueba:
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```
(Esto es un ejemplo, crea el tuyo en Slack)

### 5. Guardar y Activar
1. Click en "Save" (arriba a la derecha)
2. Dale un nombre: "SLO Alert - Notificación de Incidentes"
3. Click el botón verde "Activate" para activar el workflow
4. El workflow se ejecutará automáticamente cada 5 minutos

## 🧪 Pruebas

### Probar sin Slack
1. Desactiva temporalmente el Slack (desconecta el nodo)
2. Activa el Cron manualmente
3. Verifica que Prometheus devuelve datos

### Probar con datos reales
1. Triggers una alerta en Prometheus (opcional, genera carga)
2. El workflow enviará notificación a Slack en 5 minutos

## 📊 Variables Útiles

```javascript
// Acceder a datos de Prometheus
{{ $json.data.result[0].metric.alertname }}

// Extraer todos los nombres de alertas
{{ $json.data.result.map(r => r.metric.alertname).join(', ') }}

// Timestamp del alert
{{ $json.data.result[0].value[0] }}
```

## 🔗 Referencias

- [n8n HTTP Request Node](https://docs.n8n.io/nodes/n8n-nodes-base.httpRequest/)
- [n8n Cron Trigger](https://docs.n8n.io/nodes/n8n-nodes-base.cronTrigger/)
- [Prometheus Alert Query](http://localhost:9090/alerts)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)

## ⚠️ Troubleshooting

**El workflow no se ejecuta cada 5 minutos:**
- Verifica que esté "Activated" (botón verde)
- Revisa los logs: Menu → Workflow Settings → Executions

**No recibe notificaciones:**
- Verifica el Webhook URL de Slack
- Confirma que Prometheus tiene alertas: http://localhost:9090/alerts
- En n8n, click "Execute Workflow" para probar manualmente

**Errores de conexión:**
- Verifica que Prometheus está running: `docker-compose ps`
- URL debe ser `http://prometheus:9090` (desde dentro del contenedor)

---
**Última actualización:** 14 de Diciembre de 2025
