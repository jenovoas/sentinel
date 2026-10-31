# Multitenancy Mimir/Loki — preparación con rollback

Estado: **APLICADO Y VERIFICADO** el 2026-10-31 (Mimir y Loki en Marte, Alloy de Fenix).
Fecha: 2026-10-31.
Alcance: Marte (`10.88.0.6`) + Alloy de Fenix (`10.88.0.1`).

Evidencia de aplicación:

- `loki` `/loki/api/v1/labels` sin header → **401**, con `X-Scope-OrgID: fake` → **200**.
- `mimir.yml` en Marte contiene `multitenancy_enabled: true`; `loki.yml` contiene `auth_enabled: true`.
- Alloy de Fenix ejecuta `loki.write` con `X-Scope-OrgID = "fake"` (config viva coincide con `new/alloy-fenix.alloy`).

## Cambios aplicados

| Componente | Cambio | Tenant legacy |
|---|---|---|
| Mimir | `multitenancy_enabled: true` | `anonymous` |
| Loki | `auth_enabled: true` | `fake` |
| Grafana datasource Mimir | header `X-Scope-OrgID: anonymous` | — |
| Grafana datasource Loki | header `X-Scope-OrgID: fake` | — |
| Alloy Marte | `loki.write` con `X-Scope-OrgID: fake` | — |
| Alloy Fenix | `loki.write` con `X-Scope-OrgID: fake` | — |
| Prometheus | sin cambios; hoy no tiene `remote_write` a Mimir | — |

`fake` es el tenant que Loki usa cuando `auth_enabled: false`; `anonymous` es el
equivalente de Mimir. Por eso los datos actuales siguen visibles tras el cambio.

## Artefactos

- `backup/`: copia exacta de las configuraciones vivas antes del cambio.
- `new/`: configuraciones preparadas.
- `apply-marte.sh`: aplica Marte en orden Alloy → Loki → Grafana → Mimir.
- `rollback-marte.sh`: restaura Marte y reinicia los servicios.
- `apply-fenix-alloy.sh` / `rollback-fenix-alloy.sh`: Alloy de Fenix.
- `smoke-mimir.sh` / `smoke-loki.sh`: validación con contenedores temporales.

## Smoke tests (staging, sin tocar producción)

Ejecutados en contenedores temporales con volúmenes vacíos y eliminados después:

| Test | Resultado |
|---|---|
| Mimir `multitenancy_enabled=true` | `/ready`; labels sin header **401**, con `anonymous` **200** |
| Loki `auth_enabled=true` | `/ready`; labels sin header **401**, con `fake` **200** |
| Alloy `fmt` Marte/Fenix | rc=0 |
| Datasources YAML | headers Mimir `anonymous` y Loki `fake` presentes |

Repetir con `smoke-mimir.sh` / `smoke-loki.sh` antes de la ventana.

## Orden de aplicación

1. **Fenix primero** (no disruptivo: Loki aún no exige auth):
   ```bash
   cd /home/jnovoas/proyectos/sentinel/service-operation/deploy/marte/staging-tenancy-20261031
   ./apply-fenix-alloy.sh
   ```
   Verificar que `sentinel-fenix-alloy` siga enviando logs a Loki.
2. **Marte**:
   ```bash
   sudo /opt/sentinel-marte/staging/tenancy-20261031/apply-marte.sh
   ```
3. El script verifica:
   - Loki `labels` sin header → 401 y con `X-Scope-OrgID: fake` → 200.
   - Mimir `labels` con `X-Scope-OrgID: anonymous` → 200.
   - Grafana datasources `loki` y `mimir` healthy.

## Rollback

1. Marte:
   ```bash
   sudo /opt/sentinel-marte/staging/tenancy-20261031/rollback-marte.sh
   ```
2. Fenix (opcional; con Loki sin auth el header se ignora):
   ```bash
   cd /home/jnovoas/proyectos/sentinel/service-operation/deploy/marte/staging-tenancy-20261031
   ./rollback-fenix-alloy.sh
   ```

## Verificación manual

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://10.88.0.6:3100/loki/api/v1/labels
curl -s -o /dev/null -w '%{http_code}\n' -H 'X-Scope-OrgID: fake' http://10.88.0.6:3100/loki/api/v1/labels
docker run --rm --network sentinel_marte_observability postgres:16-alpine \
  sh -c 'wget -qO- --header="X-Scope-OrgID: anonymous" http://sentinel-marte-mimir:9009/prometheus/api/v1/labels'
curl -fsS http://10.88.0.6:3000/api/health
```

## Límites y siguiente fase

- Los dashboards actuales (incluido `sentinel-multitenant-clients`) consultan
  **Prometheus** (`uid: prometheus`), no Mimir. Mimir no tiene `remote_write`
  hoy; habilitar su multitenancy no cambia el aislamiento de métricas.
- El aislamiento real por cliente requiere:
  1. Ingesta por tenant (Prometheus/Alloy → Mimir/Loki con `X-Scope-OrgID`).
  2. Datasource por org de Grafana con el header del tenant.
  3. Dashboard `tenant-overview` por org (hoy no existe; el iframe muestra
     “dashboard not found”).
- `provision-tenant.sh` crea la org y el mapping JWT; no crea datasource ni
  dashboard todavía.
