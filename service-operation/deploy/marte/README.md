# Backend de seguridad y observabilidad de Marte

El stack se aloja en Marte (`10.88.0.6`); Fenix (`10.88.0.1`) sigue como backend central. SOMA no forma parte de este stack. Prometheus obtiene por WireGuard las métricas de FastAPI, Cortex, gateway y PostgreSQL; conserva 30 días localmente y las envía a Mimir. Recoge además cinco node-exporters y cinco sondeos ICMP privados mediante blackbox-exporter. Grafana consulta Prometheus, Mimir y Loki. Alloy en ambos nodos entrega journald/auditd; Alloy de Fenix también sigue los logs JSON de Docker sin montar el socket del daemon.

## Procedimiento aplicado

1. Verificar nodo, WireGuard, disco, Firewalld y acceso administrativo; instalar Docker Engine y Compose v2 en Marte.
2. Copiar este directorio a `/opt/sentinel-marte`. Reutilizar el secreto existente `/etc/sentinel/grafana-admin-password`, montado como `/run/secrets/grafana-admin-password` y consumido con `GF_SECURITY_ADMIN_PASSWORD__FILE`. Conservar sus permisos restringidos y la lectura por el usuario del contenedor. No crear `.env` con la contraseña, no imprimirla y no volver a rotarla durante este despliegue: el admin real ya fue actualizado.
3. En Marte ejecutar `docker compose config --quiet`, revisar bindings y luego `docker compose up -d`. Confirmar salud HTTP y estado de cada contenedor.
4. Permitir TCP 3100 desde Fenix (`10.88.0.1`) y TCP 3000 desde los nodos administrativos autorizados. Prometheus/Mimir permanecen sin puertos publicados en el host.
5. En Fenix validar que Loki responde por `http://10.88.0.6:3100/ready`, y aplicar `compose.fenix-agent.yaml`. El agente usa `network_mode: host` para que sus conexiones a Loki salgan por WireGuard con la IP de Fenix que permite Firewalld; Alloy escucha su diagnóstico solo en `127.0.0.1:12345`. No monta el socket Docker.
6. Aceptar telemetría solo al confirmar objetivos Prometheus `up`, `remote_write` sin errores, etiquetas y entradas consultables en Loki y datasources provisionados en Grafana. `/-/healthy` del agente por sí solo no prueba ingesta.

La API de Loki se publica únicamente en la IP WireGuard de Marte, puerto 3100. Grafana se publica en la IP WireGuard, puerto 3000. La política Firewalld permite Loki solo desde Fenix y Grafana desde los nodos administrativos autorizados. Prometheus y Mimir no publican puertos en el host.

## Límites funcionales

- El panel Plataforma usa series reales de los cinco nodos, tres servicios core, RTT ICMP WireGuard, Mimir y Loki. Se corrigieron las consultas históricas `job="syslog"` y el panel de infraestructura ahora filtra `node="fenix"` para no mezclar hosts.
- Los paneles históricos de Redis y multi-tenant siguen fuera de aceptación: Redis no tiene exporter con ACL persistente de mínimos privilegios y no existen identidades/aislamiento tenant verificados. PostgreSQL sí entrega `pg_up=1` mediante un rol dedicado sin privilegios administrativos. No se crearon carpetas ni accesos tenant. Una etiqueta `tenant="platform"` no es un control de autorización.
- El almacenamiento Mimir es monolítico en disco local, con retención de 30 días. No brinda alta disponibilidad ni reemplaza una política de backup.
- Promtail no se usa: alcanzó EOL el 2026-03-02; Alloy es el agente de logs vigente.
- Truth Core no se arranca con el score fijo/procesamiento simulado histórico. El filtro SCV/entropía tampoco está conectado al Gateway Marte ni al Cortex servidor: AIOpsShield/`TelemetrySanitizer` son procesos activos distintos. Mantener ambas brechas separadas del verificador/score de contenido pendiente de recuperar y corregir.
- La recuperación fuera de banda de Marte NO está probada. No se realizan nuevos attaches eBPF/XDP, apertura de `/dev/watchdog` ni enforcement como parte del monitoreo. La presencia de programas de auditoría o de métricas del gateway no demuestra esos prerrequisitos.
- AIOpsShield/TelemetrySanitizer corren en el gateway de Marte. AIOpsDoom se trata como clase de amenaza; no se atribuye equivalencia al paper sin evaluar el flujo estructurado completo.
- Guardian Beta/Cortex y Gamma/API permanecen en Fenix; la UI de aprobación corresponde a Kingu. La GUI Tauri histórica fue un prototipo con métricas simuladas, retirada del árbol activo. No empaquetar hasta recuperar/revisar y conectar sus datos reales.

## Poblado aplicado y evidencia — 2026-10-31

Inventario desde el contenedor Prometheus, no desde el estado `Up` de Docker:

| Job | Destinos reales | Resultado |
| --- | --- | --- |
| `prometheus` | `prometheus:9090` | 1 objetivo |
| `node-exporter-marte` | `node-exporter:9100` | 1 objetivo |
| `node-exporter-wg` | `10.88.0.{1,2,4,5}:9100` — Fenix, Kingu, Hercules, Ocean | 4 objetivos |
| `sentinel-fastapi-fenix` | `10.88.0.1:8000/metrics` | 1 objetivo |
| `sentinel-cortex-fenix` | `10.88.0.1:8001/metrics` | 1 objetivo |
| `sentinel-security-gateway-marte` | `10.88.0.6:8090/metrics` | 1 objetivo |
| `sentinel-postgres-fenix` | `10.88.0.1:9187/metrics` | 1 objetivo |
| `wireguard-icmp` | `10.88.0.{1,2,4,5,6}` mediante `blackbox-exporter:9115` | 5 objetivos |

Se observaron **15/15 objetivos `up=1`** y **5/5 `probe_success=1`**. Mimir devolvió los mismos 15 objetivos con `tenant="platform"` mediante `/prometheus/api/v1/query`, incluido `pg_up=1`, comprobando lectura después de `remote_write`. El contador de muestras fallidas fue 0; la cola pendiente fluctúa durante el envío y el retraso observado fue de unos 17 s, no se exige una cola instantáneamente vacía. Las consultas de CPU, RAM y disco raíz devolvieron cinco series, una por nodo.

Loki devolvió entradas recientes de Fenix (`docker-container` y `systemd-journal`) y Marte (`systemd-journal`) con `node` y `tenant="platform"`. El journal de Fenix estaba en cero: faltaba montar `/etc/machine-id`; tras corregirlo, su contador de líneas pasó a más de 349 mil, incluyendo el historial permitido de 24 h. Se conservan las etiquetas `service` de journald; el origen de archivos Docker se etiqueta genéricamente `service="docker"` sin atribuir nombres de contenedor inexistentes. La configuración de auditd no equivale a demostrar entradas auditd recientes.

Los tres datasources Grafana (`prometheus`, `mimir`, `loki`) respondieron `OK` a su endpoint de salud usando el admin existente sin exponerlo. Se cargaron los UID `sentinel-platform` (10 paneles), `sentinel-host-infrastructure` (11 paneles) y `sentinel-containers-and-logs` (4 paneles). Sus 29 consultas devolvieron datos; los logs se comprobaron sin imprimir contenido. La API de esta versión devuelve `meta.provisioned=false` y un `provisionedExternalId` coincidente con el JSON: la aceptación se apoya en UID, consultas y salud, no en ese booleano. No se afirma validación visual de la UI.

### Cambios operativos acotados

- Alertmanager `sentinel-marte-alertmanager` (octavo contenedor del stack): SMTP a `10.88.0.1:587` con `server_name=mail.pinguinoseguro.cl` (el cert no tiene IP SAN), secreto `/etc/sentinel/alertmanager-smtp-password` dueño `nobody:nogroup` 0600 (el contenedor corre como 65534). Reglas en `rules-sentinel.yml`.
- Fenix: Alloy incorpora `/etc/machine-id`; se agregó un único node-exporter en `10.88.0.1:9100` y un PostgreSQL exporter en `10.88.0.1:9187`. Este último usa `sentinel_monitor` sin privilegios administrativos, secreto `0400` y una red de exposición dedicada: la red de datos `sentinel_internal` permanece `internal: true`.
- Kingu, Hercules y Ocean: paquete Debian `prometheus-node-exporter` `1.9.0-1+b4`, una instancia nativa por nodo. Se creó `/etc/default/prometheus-node-exporter` con `ARGS="--web.listen-address=<IP_WG>:9100"` **antes** de instalar, manteniendo ese archivo con `--force-confold`, para impedir un arranque inicial público. No se instaló Docker ni se duplicaron exporters.
- Hercules: regla Firewalld runtime y permanente en `wgmesh` para TCP 9100, únicamente desde `10.88.0.6/32`. Su resolución del repositorio Debian falló; se transfirió por SSH el mismo paquete descargado por APT en Kingu, sin cambiar DNS ni AD.
- Ocean: `ocean-observability.nft` instalado en `/etc/nftables.d/sentinel-observability.nft`; `/etc/nftables.conf` lo incluye al final. La regla admite exclusivamente `wg0`, origen `10.88.0.6`, destino `10.88.0.5`, TCP 9100. Se validó el archivo completo con `nft -c`; al runtime se agregó solo esa regla, **sin cargar el `flush ruleset` ni recargar el firewall**.
- Fenix: regla ICMP `echo-request` runtime y permanente en `wgmesh`, solo de `10.88.0.6/32` a `10.88.0.1`, para medir RTT. No se cambiaron puertos públicos.

Las configuraciones anteriores se preservaron en `/var/backups/sentinel-observability/20261031T0555Z/`, directorio `0700`, en Fenix, Marte y Ocean. En Marte incluye compose, Prometheus, Alloy, provisioning y dashboards; en Fenix, los archivos previos del agente; en Ocean, nftables previo. Los paquetes nativos y sus archivos de configuración no existían previamente. No se ejecutó una prueba de reversión ni se tocaron scripts de backup.

Para volver atrás, restaurar **solo** los archivos cambiados desde esas copias y recrear exclusivamente los colectores afectados; no usar `compose down`. Los exporters nativos son instalaciones nuevas: deshabilitar únicamente `prometheus-node-exporter` si se revierte esa parte. Quitar solo las reglas añadidas de 9100/ICMP y, en Ocean, el include y la regla con comentario `sentinel-observability`; nunca restaurar un ruleset completo sobre cambios posteriores. El secreto Grafana queda fuera de esta reversión.

### Bloqueos que siguen abiertos

- **Redis:** no hay exporter ni serie `redis_*`. No se reutiliza la contraseña maestra en `Config.Env`; falta una ACL persistente de mínimos privilegios y su integración con la rotación coordinada. El panel histórico de Redis no es evidencia de instrumentación.
- **n8n y notificaciones:** `docker-compose.fenix.yml` declara `sentinel-n8n` en el puerto WG 5678, pero no existe contenedor desplegado, unidad n8n ni listener 5678 en los cinco nodos inspeccionados. Las rutas versionadas son las plantillas `POST /webhook/alert/enriched` (`n8n/workflows/alert-enriched-example.json`, `active=false`) y `POST /webhook/aiops-ingest` (`service-operation/monitoring/observability/n8n/workflows/aiops_shield_workflow.json`, sin activación declarada). La guía SLO contiene un destino Slack por reemplazar, no un receptor aprobado. Prometheus devuelve `activeAlertmanagers=[]` y `groups=[]` en reglas. Falta habilitar/identificar un workflow real, su autenticación y un canal/destinatario humano autorizado. No se arrancó n8n ni se envió una alerta de prueba; no se afirma entrega a WhatsApp/Telegram/Slack.
- **Tenants:** faltan identidades, grupos y un aislamiento validado. No se implementaron vistas tenant ni se declara superado el test A/B.
- **Retención:** Prometheus/Mimir y Loki mantienen 30 días efectivos. Los 90 días propuestos para logs no fueron aplicados sin dimensionamiento/validación de capacidad.

### Aceptación no destructiva para el integrador

Estos comandos no imprimen secretos ni entradas de logs. Ejecutar desde Fenix:

```sh
# Mostrar únicamente estado, etiquetas y error de scrape; esperar 15 objetivos sanos.
ssh -p 4222 marte 'sudo -n docker exec sentinel-marte-prometheus wget -qO- http://127.0.0.1:9090/api/v1/targets' \
  | jq '.data.activeTargets[] | {job:.labels.job,node:.labels.node,health,lastError}'

# Prometheus: 15 objetivos platform up; Mimir: la misma lectura, no sólo escritura aceptada.
ssh -p 4222 marte 'sudo -n docker exec sentinel-marte-prometheus wget -qO- "http://127.0.0.1:9090/api/v1/query?query=count%28up%7Btenant%3D%22platform%22%7D%20%3D%3D%201%29"'
ssh -p 4222 marte 'sudo -n docker exec sentinel-marte-prometheus wget -qO- "http://mimir:9009/prometheus/api/v1/query?query=count%28up%7Btenant%3D%22platform%22%7D%20%3D%3D%201%29"'

# Blackbox: cinco valores 1; contar logs sin imprimir contenido.
ssh -p 4222 marte 'sudo -n docker exec sentinel-marte-prometheus wget -qO- "http://127.0.0.1:9090/api/v1/query?query=probe_success%7Bjob%3D%22wireguard-icmp%22%7D"'
ssh -p 4222 marte 'sudo -n docker exec sentinel-marte-prometheus wget -qO- "http://loki:3100/loki/api/v1/query?query=sum%20by%28node%2Cjob%29%20%28count_over_time%28%7Bnode%3D~%22fenix%7Cmarte%22%2Ctenant%3D%22platform%22%7D%5B5m%5D%29%29"' \
  | jq '.data.result'

# Validación de fuentes, sin reinicios.
ssh -p 4222 marte 'sudo -n docker exec sentinel-marte-prometheus promtool check config /etc/prometheus/prometheus.yml && sudo -n docker exec sentinel-marte-alloy alloy validate /etc/alloy/config.alloy'
```

En Grafana comprobar los UID citados y `/api/datasources/uid/{prometheus,mimir,loki}/health` con la sesión/admin existente. Si se automatiza, leer el fichero FILE dentro de un proceso protegido; nunca incluir la contraseña en argumentos, URL o salida. Al reemplazar archivos bind-mount mediante `install`, recrear exclusivamente el contenedor consumidor: un `HUP` sobre un mount al inode anterior no aplica ese reemplazo.
