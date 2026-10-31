# T7. Poblado de monitoreo y métricas en Marte — `agente:obs`

> Estado verificado 2026-10-31: infraestructura, servicios core, PostgreSQL y logs poblados; **T7 no está aceptado íntegramente** por los bloqueos de Redis, notificaciones y tenants descritos abajo. La recuperación fuera de banda de Marte NO está probada: este trabajo no habilita eBPF/XDP, watchdog ni enforcement.

## 1. Evidencia aplicada

- Marte pasó de seis a siete contenedores al incorporar blackbox-exporter privado, sin publicar 9115. Prometheus/Mimir siguen sin puerto publicado; Grafana y Loki conservan sus bindings WireGuard existentes.
- Desde el contenedor Prometheus se observaron **15/15 objetivos `up=1`**: cinco node-exporters (Marte, Fenix, Kingu, Hercules, Ocean), tres endpoints reales core (FastAPI, Cortex y gateway Marte), PostgreSQL, Prometheus y cinco sondeos ICMP WireGuard. Los cinco `probe_success` fueron 1. CPU/RAM/disco raíz devolvieron una serie por nodo.
- Node-exporter de Fenix es un único contenedor en `10.88.0.1:9100`. Kingu/Hercules/Ocean usan una única instancia Debian `1.9.0-1+b4`, configurada para su IP WG antes de instalar. No se instaló Docker en esos nodos ni se duplicaron exporters.
- Mimir devolvió los mismos **15 objetivos sanos** mediante su API de consulta, incluido `pg_up{job="sentinel-postgres-fenix"}=1`. `prometheus_remote_storage_samples_failed_total{tenant="platform"}` fue 0; retraso de envío observado de unos 17 s. La cola pendiente fluctúa y no se confunde con fallo o ausencia de datos.
- Loki devolvió logs recientes de Fenix (`docker-container`, `systemd-journal`) y Marte (`systemd-journal`). El journal Fenix no ingería líneas: se corrigió el mount de `/etc/machine-id`; el contador pasó de 0 a más de 349 mil incluyendo el historial permitido. Se incorporaron etiquetas `service` de journald y `tenant="platform"`; Docker mantiene `service="docker"` genérico sin socket del daemon. No se imprimieron entradas de logs.
- Grafana: salud `OK` de los tres datasources (`prometheus`, `mimir`, `loki`) con el admin existente; no hubo nueva rotación. Se cargó **Sentinel — Plataforma** (10 paneles), se corrigió el filtro Fenix del dashboard de host (11 paneles) y se migraron consultas Loki del inexistente `job="syslog"` a las fuentes reales (4 paneles). Las 29 consultas de esos tres dashboards devolvieron datos. No se afirma prueba visual del navegador.
- La contraseña Grafana permanece en `/etc/sentinel/grafana-admin-password`, consumida por `GF_SECURITY_ADMIN_PASSWORD__FILE`. El paso 2 del README ya no prescribe `.env` con contraseña plana. No se modificó ni mostró el secreto.

La etiqueta operativa `tenant="platform"` no establece segregación ni autorización. En Grafana 13 la API observada devuelve `meta.provisioned=false` junto a `provisionedExternalId` coincidente con el JSON; la evidencia consiste en UID cargado, consultas y salud, no en ese booleano.

## 2. Cambios privados de red y reversión

- Hercules: TCP 9100 permitido en `wgmesh` solamente desde Marte `10.88.0.6/32`, runtime y permanente.
- Ocean: regla aditiva `wg0`, origen `10.88.0.6`, destino `10.88.0.5`, TCP 9100. Fragmento `/etc/nftables.d/sentinel-observability.nft` incluido por `/etc/nftables.conf`; validación `nft -c` del conjunto y aplicación runtime **solo del fragmento**, sin `flush ruleset` ni reload.
- Fenix: `echo-request` ICMP permitido en `wgmesh` únicamente de Marte a la IP WG Fenix, runtime y permanente, para RTT real.
- PostgreSQL exporter usa el rol `sentinel_monitor`, con login pero sin superusuario, `CREATEROLE` ni `CREATEDB`; el secreto permanece en un fichero `0400`. Se publica exclusivamente en `10.88.0.1:9187` mediante una red dedicada porque `sentinel_internal` es deliberadamente interna. Prometheus y Mimir observaron `pg_up=1`.
- No se abrieron puertos públicos, se recargó el firewall, se detuvieron servicios de negocio para provocar alarmas ni se tocaron AD/MyCNet.
- Copias de configuración anterior: `/var/backups/sentinel-observability/20261031T0555Z/` en Fenix, Marte y Ocean, más `/var/backups/sentinel-observability/20261031T0625Z/prometheus.yml` antes de agregar PostgreSQL en Marte; directorios `0700`. Revertir solo archivos/reglas propios y recrear exclusivamente colectores consumidores; nunca `compose down` ni reemplazar un ruleset sobre cambios posteriores. Exporters nativos eran instalaciones nuevas. No se ha ensayado una reversión ni se han modificado scripts de backup.

Los archivos, inventario detallado, límites y comandos de aceptación sin secretos están en [`service-operation/deploy/marte/README.md`](../../service-operation/deploy/marte/README.md).

## 3. Bloqueos exactos y alcance no aceptado

1. **Redis:** no se desplegó exporter ni serie `redis_*`. Se rechazó reutilizar `REDIS_PASSWORD` en `Config.Env`; falta una ACL persistente de mínimos privilegios compatible con rotación. El panel histórico de Redis sigue sin aceptación.
2. **Alertas n8n:** `docker-compose.fenix.yml` declara `sentinel-n8n`, pero no hay contenedor desplegado, unidad n8n ni listener 5678 en los cinco nodos. Las únicas rutas identificadas son plantillas versionadas: `POST /webhook/alert/enriched` (`n8n/workflows/alert-enriched-example.json`, `active=false`) y `POST /webhook/aiops-ingest` (`service-operation/monitoring/observability/n8n/workflows/aiops_shield_workflow.json`, sin activación declarada). La guía SLO tiene un destino Slack por reemplazar. Prometheus devuelve `activeAlertmanagers=[]` y reglas `groups=[]`. Falta workflow real, autenticación y canal/destinatario humano aprobado. **No se envió alerta de prueba ni se afirma recepción** por WhatsApp/Telegram/Slack. No se arrancó n8n por inferencia.
3. **Vistas tenant:** no existen identidades/grupos y aislamiento verificados. No se crearon carpetas/accesos tenant ni se ejecutó el test A/B. El dashboard multi-tenant histórico no demuestra aislamiento.
4. **Alertas funcionales adicionales:** caída/disco/QHC-dead-man/certificado no se declaran implementadas ni notificadas. La disponibilidad de `/metrics` no demuestra estado QHC sano ni entrega de alertas.
5. **Logs:** configuración auditd no demuestra ingesta auditd reciente. Promtail no se instala (EOL); Alloy es el agente vigente. La retención efectiva Loki sigue en 30 días; los 90 días del diseño requieren dimensionamiento y validación de capacidad.

## 4. Criterios de aceptación

| Criterio | Estado |
| --- | --- |
| Plataforma con nodos + servicios core `up=1`, RTT WG, disco/RAM | Verificado por consultas: cinco nodos, tres servicios, cinco sondeos |
| Lectura real Mimir después de remote_write | Verificada: 15 objetivos sanos con etiqueta platform, incluido `pg_up=1` |
| Logs Fenix/Marte + datasources/paneles operativos | Verificados con conteos, salud API y consultas; sin prueba visual |
| Dashboard tenant piloto aislado A/B | Bloqueado por identidades y autorización; no implementado |
| Alerta de prueba extremo a extremo hacia receptor aprobado | Bloqueada por runtime/workflow/destinatario; no enviada |
| Password admin Grafana rotado y fuera de Env plano | Rotación previa conservada; FILE documentado, admin existente autenticó las consultas |

La integración final se registra junto con los cambios de configuración, pruebas y nota de vault de la sesión.
