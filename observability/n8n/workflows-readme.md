# n8n Workflows - Sentinel Lab

## Setup n8n Sin Google (Slack + Email Simple)

### 1. Acceder a n8n

```
http://localhost:5678
Usuario: darkfenix
Contraseña: darkfenix
```

### 2. Crear tu primer workflow - OPCIÓN FÁCIL

**Usando template pre-hecho:**

1. Ve a http://localhost:5678
2. Click "New" → "Workflow"
3. Click menú (tres puntos) → "Import from JSON"
4. Copia el contenido de: `observability/n8n/workflow-daily-report-template.json`
5. Pega en el dialog de import
6. Click "Import"
7. Edita y reemplaza `YOUR/WEBHOOK/URL` con tu webhook real
8. Click "Save"

---

## Crear Slack App (Requerido para Slack)

### Paso 1: Crear Slack App

1. Ve a https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Sentinel Bot"
4. Workspace: tu workspace
5. En Features → Incoming Webhooks → Activar
6. Click "Add New Webhook to Workspace"
7. Selecciona canal (ej: #alerts)
8. Copia la URL (será así: `https://hooks.slack.com/services/T.../B.../XXX`)

### Paso 2: Usar el webhook en n8n

En tu workflow n8n:
1. En el nodo "Send to Slack" (HTTP Request node)
2. Reemplaza la URL: `{{ $env['SLACK_WEBHOOK'] }}` o pega tu URL directa
3. Save & Activate

---

## Opción B: Email Abierto (SMTP)

Si quieres email sin Google:

### Paso 1: Configurar mailhog (email local)

Ya incluido en Docker Compose. Acceder en: `http://localhost:1025`

### Paso 2: n8n Send Email

```
1. En n8n, Add Node: Send Email
   - From: sentinel@localhost
   - To: admin@sentinel.local
   - Subject: "Daily SLO Report"
   - Text: contenido del reporte
2. Save & Activate
```

---

## Workflow Templates

### Template 1: Daily Report a Slack

**Archivo**: `workflow-daily-report-template.json`

**Lo que hace**:
- Trigger: Cada día a las 9 AM
- Build: Crea reporte con status de servicios
- Send: Envía a Slack via webhook

**Cómo usarlo**:
1. Importa JSON desde n8n UI
2. Reemplaza `YOUR/WEBHOOK/URL` con tu webhook real
3. Save & Activate

### Template 2: Manual Test (En el dashboard)

```
1. Click "New"
2. Click "Manual trigger" nodo
3. Click "Execute Workflow"
4. Verás output en el panel
```

---

## Testing Rápido sin Slack

Si aún no tienes Slack webhook:

1. Ve a http://localhost:5678
2. Click "New" → "Workflow"
3. Trigger: Manual Trigger
4. Node: Code
   ```
   return [{
     "json": {
       "message": "✅ Workflow funcionando!",
       "time": new Date().toISOString()
     }
   }];
   ```
5. Save & Execute
6. Verás el resultado en la UI

---

## Verificar que n8n está corriendo

```bash
# Ver que n8n está disponible
curl -s http://localhost:5678/api/v1/workflows | jq '.'

# Contar workflows
curl -s http://localhost:5678/api/v1/workflows | jq '.data | length'
```

---

## Próximos Pasos

- ✅ Crear workflow básico (manual o template)
- ✅ Configurar Slack webhook
- ✅ Activar trigger automático (Cron)
- ✅ Monitorear ejecuciones en n8n UI
- ✅ Agregar logging/alerting adicional

---

## Troubleshooting

**n8n UI dice "no workflows"**:
- Normal. Crea uno manualmente o importa template
- Click "New" → "Workflow"

**Webhook de Slack no funciona**:
1. Verifica URL en https://api.slack.com/apps
2. Asegúrate que el webhook apunta a un canal válido
3. Prueba manualmente:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_WEBHOOK_URL
```

**Workflow no se ejecuta**:
1. Verifica que "Active" está encendido (verde)
2. Si es Cron, espera a la hora configurada
3. O prueba con "Manual Trigger" + "Execute"

