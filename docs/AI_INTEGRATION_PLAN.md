# Plan de Implementación: Integración de IA Local (Ollama) en Sentinel

## Objetivo

Integrar Ollama (IA local) en todos los servicios de Sentinel para proporcionar análisis inteligente de anomalías, explicaciones contextuales de alertas, y enriquecimiento automático de workflows.

---

## Estado Actual

### ✅ Ya Implementado
- `tools/watchdog_loader_ai.py` - Watchdog con integración Ollama para n8n workflows
- `host-metrics/audit-watchdog.sh` - Watchdog de seguridad (sin IA aún)
- `backend/app/services/anomaly_detector.py` - Detector estadístico (sin IA)
- Workflows n8n con referencias a Ollama

### ❌ Faltante
- Servicio Ollama en `docker-compose.yml`
- Integración de IA en `AnomalyDetector` para explicaciones inteligentes
- Endpoint de backend para consultas de IA
- Watchdog de seguridad con análisis de IA
- Variables de entorno configuradas

---

## Cambios Propuestos

### 1. Agregar Servicio Ollama a Docker Compose

Agregar nuevo servicio después de n8n en `docker-compose.yml`

### 2. Integrar IA en AnomalyDetector

Modificar `backend/app/services/anomaly_detector.py` para enriquecer anomalías con explicaciones de IA

### 3. Crear Endpoint de IA en Backend

Nuevo archivo `backend/app/routers/ai.py` con endpoint `/api/v1/ai/query`

### 4. Mejorar Watchdog de Seguridad con IA

Modificar `host-metrics/audit-watchdog.sh` para análisis inteligente de eventos

### 5. Actualizar Variables de Entorno

Agregar configuración de Ollama en `.env` y `backend/app/config.py`

---

## Recursos del Sistema

### Ollama con phi3:mini
- **RAM**: ~2-4 GB
- **Disco**: ~2 GB (modelo descargado)
- **CPU**: Moderado (sin GPU)
- **Latencia**: 1-3 segundos por query

### Modelos Disponibles
- `phi3:mini` (1.3B params) - Rápido, ligero, recomendado
- `llama3.2:1b` (1B params) - Muy rápido, menos preciso

---

## Verificación

1. Verificar servicio Ollama: `curl http://localhost:11434/api/tags`
2. Test endpoint de IA: `curl -X POST http://localhost:8000/api/v1/ai/query`
3. Verificar enriquecimiento de anomalías con campo `ai_analysis`
4. Test watchdog con análisis de IA
5. Verificar n8n workflows con Ollama

---

## Rollback Plan

Si hay problemas:
```bash
export AI_ENABLED=false
docker-compose restart backend
# O detener completamente:
docker-compose stop ollama
```

---

Ver plan completo en: `/home/jnovoas/sentinel/docs/AI_INTEGRATION_PLAN.md`
