# 📊 Verificación Técnica del Estado Final de Grafana Mimir (`sentinel-mimir`)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Contenedor:** `sentinel-mimir`  
> **Estado en Vivo (`curl http://127.0.0.1:8080/ready`):** 🟢 **`ready`**  
> **Host Header Requerido:** `X-Scope-OrgID: sentinel`  
> **Grafana Datasource UID:** `eftiuu1b0t98gd` (`Mimir-Sentinel`)  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 Verificación Empírica del Estado de Mimir

1. **Estado de Salud de Mimir (`GET /ready`)**:
   - Retorna: **`ready`** 🟢 (El ingester ring completó su ciclo de estabilización inicial y permanece en estado 100% activo sin caer en espera).

2. **Ingesta Continua de Métricas Remotas (`remote_write`)**:
   - `sentinel-prometheus` está empujando métricas activamente vía `remote_write` hacia Mimir.
   - Consulta directa en la API de Mimir:
     ```bash
     curl -s -H 'X-Scope-OrgID: sentinel' 'http://127.0.0.1:8080/prometheus/api/v1/query?query=sentinel_cpu_temperature_celsius'
     ```
   - **Resultado**:
     ```json
     {"status":"success","data":{"resultType":"vector","result":[{"metric":{"__name__":"sentinel_cpu_temperature_celsius","instance":"127.0.0.1:8000","job":"sentinel_cortex"},"value":[1785339809.511,"45"]}]}}
     ```

3. **Integración con Grafana mediante Custom Header (`X-Scope-OrgID`)**:
   - Reconfiguramos el Datasource de Grafana `Mimir-Sentinel` (`eftiuu1b0t98gd`) inyectando automáticamente la cabecera `X-Scope-OrgID: sentinel`.
   - Consulta a través del Proxy de Grafana:
     ```bash
     curl -s -u admin:admin 'http://127.0.0.1:3001/api/datasources/proxy/uid/eftiuu1b0t98gd/api/v1/query?query=sentinel_cpu_temperature_celsius'
     ```
   - **Resultado**: **Éxito total (`status: success`)**. Grafana ahora puede consultar directamente tanto Mimir como Prometheus.
