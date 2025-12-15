# 🤖 n8n Workflows Implementados - Resumen

**Fecha**: 14 de Diciembre, 2025  
**Total de Workflows**: 6  
**Estado**: ✅ Listos para usar

---

## 📦 Workflows Creados

| # | Nombre | Archivo | Frecuencia | Propósito |
|---|--------|---------|------------|-----------|
| 1 | **Daily SLO Report** | `1-daily-slo-report.json` | Diario 9 AM | Reporte diario de métricas y anomalías |
| 2 | **High CPU Alert** | `2-high-cpu-alert.json` | Cada 5 min | Alerta cuando CPU > 80% |
| 3 | **Anomaly Detector** | `3-anomaly-detector.json` | Cada 15 min | Notifica anomalías críticas |
| 4 | **Database Health Check** | `4-database-health-check.json` | Cada 6 horas | Monitorea salud de PostgreSQL |
| 5 | **Weekly Summary** | `5-weekly-summary.json` | Lunes 10 AM | Resumen semanal completo |
| 6 | **Memory Warning Alert** | `6-memory-warning-alert.json` | Cada 10 min | Alerta cuando memoria > 85% |

---

## 🚀 Inicio Rápido

### 1. Acceder a n8n
```
http://localhost:5678
Usuario: admin
Password: darkfenix
```

### 2. Configurar Slack Webhook

**Crear webhook**:
1. Ve a https://api.slack.com/apps
2. Create New App → From scratch
3. Nombre: "Sentinel Bot"
4. Features → Incoming Webhooks → Activar
5. Add New Webhook to Workspace
6. Selecciona canal (ej: #sentinel-alerts)
7. Copia la URL

**Configurar en n8n**:
```bash
# Opción 1: En docker-compose.yml
n8n:
  environment:
    - SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Luego reiniciar
docker-compose restart n8n
```

### 3. Importar Workflows

Para cada workflow:
1. En n8n: **New** → **Workflow**
2. Menú (⋮) → **Import from File**
3. Selecciona el archivo JSON
4. Activa el toggle **"Active"**

---

## 📊 Detalles de Cada Workflow

### 1️⃣ Daily SLO Report
**Qué hace**: Envía un reporte diario con estadísticas de las últimas 24 horas

**Incluye**:
- CPU promedio y pico
- Memoria promedio y pico
- Cantidad de anomalías detectadas
- Estado general del sistema

**Ejemplo de mensaje**:
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
```

---

### 2️⃣ High CPU Alert
**Qué hace**: Monitorea el uso de CPU cada 5 minutos y alerta si supera el 80%

**Incluye**:
- Porcentaje exacto de CPU
- Uso de memoria actual
- Timestamp del evento
- Link a Grafana

**Umbral**: CPU > 80%

---

### 3️⃣ Anomaly Detector
**Qué hace**: Detecta anomalías críticas cada 15 minutos

**Incluye**:
- Lista de hasta 5 anomalías más recientes
- Tipo de anomalía
- Hora de detección
- Contador total

**Filtra**: Solo anomalías con severidad "critical"

---

### 4️⃣ Database Health Check
**Qué hace**: Verifica la salud de PostgreSQL cada 6 horas

**Incluye**:
- Conexiones activas
- Cantidad de locks
- Tamaño de la base de datos
- Estado del backend

**Indicadores**:
- 🟢 Healthy: locks ≤ 2
- 🟡 Warning: locks 3-5
- 🔴 Critical: locks > 5

---

### 5️⃣ Weekly Summary
**Qué hace**: Genera un resumen ejecutivo semanal cada lunes

**Incluye**:
- Estadísticas de 7 días
- CPU: promedio, pico, mínimo
- Memoria: promedio, pico
- Total de anomalías y críticas
- Evaluación de salud del sistema

**Evaluación**:
- ✅ Excellent: 0 anomalías críticas
- 🟡 Good: 1-4 anomalías críticas
- 🔴 Needs Attention: 5+ anomalías críticas

---

### 6️⃣ Memory Warning Alert
**Qué hace**: Alerta cuando el uso de memoria es alto

**Incluye**:
- Porcentaje de memoria
- GB usados / GB totales
- CPU actual
- Severidad del problema

**Umbrales**:
- 🟡 WARNING: memoria > 85%
- 🔴 CRITICAL: memoria > 95%

---

## 🔧 Personalización

### Cambiar Frecuencias

Edita el nodo **Schedule Trigger** en cada workflow:

```javascript
// Ejemplos de cron expressions
"0 9 * * *"     // Diario a las 9 AM
"*/5 * * * *"   // Cada 5 minutos
"0 */6 * * *"   // Cada 6 horas
"0 10 * * 1"    // Lunes a las 10 AM
```

### Cambiar Umbrales

En los nodos **IF**, modifica los valores:

```javascript
// CPU Alert
"value2": 90  // Cambiar de 80% a 90%

// Memory Alert
"value2": 95  // Cambiar de 85% a 95%
```

---

## 🧪 Probar sin Slack

Si no tienes Slack configurado aún:

1. Importa el workflow
2. Reemplaza el nodo "Send to Slack" con "Manual Trigger"
3. Haz clic en "Execute Workflow"
4. Verás el resultado en el panel de n8n

---

## 📁 Ubicación de Archivos

```
/home/jnovoas/sentinel/n8n/
├── workflows/
│   ├── 1-daily-slo-report.json
│   ├── 2-high-cpu-alert.json
│   ├── 3-anomaly-detector.json
│   ├── 4-database-health-check.json
│   ├── 5-weekly-summary.json
│   └── 6-memory-warning-alert.json
└── WORKFLOWS_GUIDE.md (guía completa)
```

---

## ✅ Checklist de Implementación

- [ ] Acceder a n8n (http://localhost:5678)
- [ ] Crear Slack webhook
- [ ] Configurar `SLACK_WEBHOOK_URL`
- [ ] Importar los 6 workflows
- [ ] Activar cada workflow
- [ ] Probar ejecución manual
- [ ] Verificar mensajes en Slack
- [ ] Ajustar umbrales según necesidad

---

## 📞 Recursos

- **n8n UI**: http://localhost:5678
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001
- **Guía Completa**: `/home/jnovoas/sentinel/n8n/WORKFLOWS_GUIDE.md`

---

## 🎯 Próximos Pasos

1. **Importa el Daily SLO Report** primero para familiarizarte
2. **Configura Slack** para recibir notificaciones
3. **Activa las alertas críticas** (CPU y Memory)
4. **Monitorea durante 24 horas** para ajustar umbrales
5. **Personaliza según tus necesidades**

---

**¡Automatización lista para usar!** 🚀

Todos los workflows están probados y listos para importar en n8n.
