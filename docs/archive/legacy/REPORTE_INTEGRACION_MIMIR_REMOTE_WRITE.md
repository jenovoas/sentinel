# 📊 Integración Final de Grafana Mimir (`sentinel-mimir`) mediante `remote_write`
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Mimir API:** `http://10.88.0.1:8080/prometheus`  
> **Tenant ID (Header):** `X-Scope-OrgID: sentinel`  
> **Prometheus Remote-Write URL:** `http://127.0.0.1:8080/api/v1/push`  
> **Estado:** 🟢 **PRODUCCIÓN 100% OPERATIVA**  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 Arquitectura e Integración Completa de Mimir

1. **Configuración de `remote_write` en Prometheus (`/etc/sentinel/prometheus.yml`)**:
   - `sentinel-prometheus` rescata métricas en tiempo real de `sentinel-cortex` (`:8000`) y `node_exporter` (`:9100`).
   - Reenvía el flujo de series temporales (*metrics stream*) hacia Mimir mediante la directiva `remote_write`:
     ```yaml
     remote_write:
       - url: http://127.0.0.1:8080/api/v1/push
         headers:
           X-Scope-OrgID: sentinel
     ```

2. **Verificación en Vivo en la API de Mimir (`http://127.0.0.1:8080/prometheus`)**:
   - Consulta ejecutada con éxito:
     ```bash
     curl -s -H 'X-Scope-OrgID: sentinel' 'http://127.0.0.1:8080/prometheus/api/v1/query?query=sentinel_cpu_temperature_celsius'
     ```
   - **Respuesta de Mimir**:
     ```json
     {
       "status": "success",
       "data": {
         "resultType": "vector",
         "result": [
           {
             "metric": {
               "__name__": "sentinel_cpu_temperature_celsius",
               "instance": "127.0.0.1:8000",
               "job": "sentinel_cortex"
             },
             "value": [1785339185.413, "45"]
           }
         ]
       }
     }
     ```

---

## 📈 Datasource Mimir en Grafana (`http://10.88.0.1:3001`)

El datasource `Mimir` (ID: `2`, UID: `eftiuu1b0t98gd`) en Grafana se encuentra leyendo directamente de Mimir en `http://localhost:8080/prometheus`. 

Tanto **Mimir** (almacenamiento masivo TSDB a largo plazo) como **Loki** (recolección centralizada de logs) y **Prometheus** (scrapeer de baja latencia) están totalmente engranados y operando en producción.
