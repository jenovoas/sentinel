http://localhost:3001/d/slo-monitoring
(admin/darkfenix)
→ Verás gráficos con datos en tiempo real# Sentinel Lab - Resumen de Implementación (B+C)

**Fecha**: 14 de Diciembre de 2025  
**Estado**: ✅ COMPLETO  
**Contexto**: Laboratorio con observabilidad, seguridad y automatización

---

## 🎯 PARTE C: SLOs & Error Budget - COMPLETADO

### Qué se configuró

1. **SLO Targets**:
   - Uptime: 99.9% (43.2 min downtime/mes)
   - Error Rate: <1% (máx 1 error por 100 requests)
   - Latencia P95: <1s

2. **Prometheus Rules** (`observability/prometheus/rules/alerts.yml`):
   - Alertas de burn rate fast (2h > 30x)
   - Alertas de burn rate slow (24h > 10x)
   - Alertas de error rate alto
   - Alertas de latencia excesiva
   - Métricas de recording para dashboards

3. **Grafana Dashboard** (`slo-budget.json`):
   - Panel: Disponibilidad Mensual (%)
   - Panel: Burn Rate 2h (múltiplos de error budget)
   - Panel: Burn Rate 24h (múltiplos de error budget)
   - Refresh: 30 segundos

4. **Documentación**:
   - README.md con sección completa de SLOs
   - Explicación de burn rate
   - Acciones recomendadas por estado de error budget

### Acceso

**Dashboard SLO**:
```
http://localhost:3001/d/slo-budget
Username: admin
Password: darkfenix
```

**Prometheus Alerts**:
```
http://localhost:9090/alerts
```

---

## 🤖 PARTE B: Automatización con n8n - CONFIGURADO

### Qué se configuró

1. **n8n Service**:
   - Corriendo en puerto 5678
   - Credenciales unificadas (admin/darkfenix)
   - Almacenamiento de workflows persistente

2. **Integraciones (Sin Google)**:
   - ✅ Slack Webhook (recomendado)
   - ✅ Email SMTP (mailhog local o SMTP real)
   - ✅ HTTP Request (flexible)

3. **Documentación** (`observability/n8n/workflows-readme.md`):
   - Setup de Slack App con webhooks
   - Templates n8n listos para usar
   - Ejemplos de reportes diarios

4. **Helper Script** (`observability/n8n/setup-n8n-slack.sh`):
   - Automatiza configuración de Slack webhook
   - Guía paso a paso

### Acceso

**n8n UI**:
```
http://localhost:5678
Username: admin
Password: darkfenix
```

### Crear tu primer workflow

**Opción 1: Usando el script** (más fácil)
```bash
# 1. Crea Slack App en https://api.slack.com/apps
# 2. Obtén el webhook URL
# 3. Ejecuta:
./observability/n8n/setup-n8n-slack.sh "https://hooks.slack.com/services/..."
```

**Opción 2: Manual**
```
1. Ve a http://localhost:5678
2. Create Workflow
3. Add Trigger: Cron (Daily, 09:00)
4. Add Node: HTTP Request
5. Configure Slack webhook URL
6. Save & Activate
```

---

## 📊 Archivos Modificados/Creados

```
observability/
├── prometheus/
│   └── rules/
│       └── alerts.yml (ACTUALIZADO)
│           └─ Nuevas alertas de SLO
│           └─ Reglas de recording
├── grafana/
│   └── provisioning/
│       └── dashboards/
│           └── json/
│               └─ slo-budget.json (NUEVO)
├── n8n/
│   ├── workflows-readme.md (NUEVO)
│   └── setup-n8n-slack.sh (NUEVO)
└── README.md (ACTUALIZADO)
```

---

## 🔗 Links Útiles

| Servicio | URL | Usuario | Password |
|----------|-----|---------|----------|
| Grafana | http://localhost:3001 | admin | darkfenix |
| Prometheus | http://localhost:9090 | - | - |
| n8n | http://localhost:5678 | admin | darkfenix |
| API | http://localhost:8000/docs | - | - |
| Frontend | http://localhost:3000 | - | - |

---

## 💡 Próximos Pasos Recomendados

### Corto Plazo (Hoy-Mañana)
1. Crear workflow n8n para Daily SLO Report
2. Integrar Slack webhook
3. Probar alertas manualmente

### Mediano Plazo (Esta semana)
1. Configurar PagerDuty para alertas críticas
2. Crear dashboard adicional de latencia
3. Agregar más reglas de SLO (custom metrics)

### Largo Plazo (Este mes)
1. Implementar postmortem automation
2. Agregar burn rate tracking histórico
3. Integrar con incident management system

---

## ⚠️ Notas Importantes

- **Autenticación Google**: No requerida. Usando Slack webhooks en su lugar.
- **Email**: Usa SMTP. Local: mailhog (puerto 1025). Production: configura tu servidor.
- **Persistencia**: Todos los workflows y dashboards persisten en volumes Docker.
- **Backup**: Recuerda hacer backup de Grafana dashboards si los modificas.

---

## 📞 Troubleshooting Rápido

**n8n no responde**:
```bash
docker-compose restart n8n
```

**Prometheus no carga reglas**:
```bash
docker-compose restart prometheus
# Verifica: http://localhost:9090/alerts
```

**Grafana no ve dashboards**:
```bash
docker-compose restart grafana
# Espera 30 segundos y recarga
```

**Slack webhook no funciona**:
1. Verifica URL en api.slack.com
2. Prueba manualmente:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_WEBHOOK_URL
```

---

**Sentinel Lab** está ahora completamente equipado con:
- ✅ Observabilidad (Prometheus + Loki + Grafana)
- ✅ Seguridad (auditd + systemd watchers)
- ✅ SLOs & Error Budget tracking
- ✅ Automatización de reportes (n8n)

🎉 **¡Listo para producción con monitoreo inteligente!**
