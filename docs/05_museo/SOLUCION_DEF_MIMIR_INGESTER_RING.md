# 🛠️ Diagnóstico y Solución Definitiva: Mimir Ingester & Ring Setup (`sentinel-mimir`)

> **Servidor:** Fan (`10.88.0.1`)  
> **Contenedor:** `sentinel-mimir`  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🟢 **LISTO Y OPERATIVO (Status: `ready`)**

---

## 🔬 Diagnóstico del Error de Mimir

Al consultar la API de Prometheus en Mimir, retornaba el error:
```json
{"status":"error","errorType":"internal","error":"too many unhealthy instances in the ring"}
```

### Causa Raíz Identificada:
Por defecto, Grafana Mimir viene configurado para operar en clúster multinodo con un `replication_factor: 3`. Al ejecutarse en modo contenedor de nodo único en el servidor **Fan**, el anillo (*ingester ring*) no encontraba los 3 nodos requeridos para alcanzar quorum de escritura/lectura y marcaba la instancia como no saludable.

---

## 🛡️ Solución Aplicada

Se generó e implementó la configuración declarativa de nodo único en `/etc/sentinel/mimir.yaml`:

```yaml
multitenancy_enabled: true

server:
  http_listen_port: 8080
  grpc_listen_port: 9095

common:
  storage:
    backend: filesystem
    filesystem:
      dir: /data/mimir

ingester:
  ring:
    replication_factor: 1
    kvstore:
      store: inmemory

store_gateway:
  sharding_ring:
    replication_factor: 1

blocks_storage:
  backend: filesystem
  filesystem:
    dir: /data/mimir/blocks
  tsdb:
    dir: /data/mimir/tsdb
```

---

## 📊 Verificación Empírica del Estado

1. **Estado de Salud (`curl http://127.0.0.1:8080/ready`)**:
   - Retorna: **`ready`** (tras transcurrir los 15s de estabilización del ingester ring).
2. **Prueba de Consulta API (`GET /prometheus/api/v1/query?query=up`)**:
   - Retorna: **`{"status":"success","data":{"resultType":"vector","result":[]}}`** (Éxito absoluto sin errores de quorum ni unhealthy instances).

