# Tareas Fase 0 — AD único + servicios por contrato + VMs por Terraform

> Rama: `main` · Origen: sesión 2026-10-30 (auditoría Codex, vault SecurePenguin, estado AD en vivo).
> Cómo trabajar: un agente = una tarea. Cada tarea cierra con evidencia + commit + entrada en vault.

## T0. Consolidar AD único (FSMO ya en Fenix) — `agente:infra-ad`

- Corrección 2026-10-30 (operador): commit `b22835c3` registra que a las 17:55 se activó en Fenix la base restaurada desde Hercules con los siete FSMO apuntando a FENIX (auditoría multínodo:399-404). No fue transferencia en vivo (`fsmo transfer`), pero Fenix y Kingu confirman roles en Fenix. **No repetir la transferencia.**
- Las vistas locales antiguas de hercules/ocean que se declaran PDC son datos estancados, no split-brain operativo. No bloquear T1–T4 por ellas.
- [x] Subtask DNS EJECUTADO 2026-10-30: kingu A 10.88.0.2 + SRV _ldap/_kerberos prioridad 10 agregados a db.pinguinoseguro.cl.internal; backup .2026-10-30; named-checkzone OK; rndc reload; dig confirma A + ambos SRV. Fenix PDC prioridad 0, Kingu BDC prioridad 10.
- [ ] Degradar hercules/ocean a solo DNS **solo después** de validar replicación fenix↔kingu y resolver qué hacer con sus vistas locales (demote o apagado samba, BIND/PowerDNS públicos intactos).
- [ ] Evidencia: `drs showrepl` en kingu 0 fallos inbound desde fenix; conteo usuarios = 14 en ambos; `dns1/dns2.pinguinoseguro.cl` resuelven.
- Hallazgo DRS 2026-10-30: replicación útil fenix→kingu SANA (0 fallos). Fallo inverso kingu→fenix (`WERR_FILE_NOT_FOUND`, 40+ fallos) irrelevante: kingu no origina objetos. Causa probable DNS, no AD.
- Entregable: nota en `docs/ops/` + entrada vault.

## T1. Grupos SP-* + OUs tenant + cuenta delegada — `agente:infra-ad`

- [x] Crear grupos: `SP-Portal-Admins`, `SP-Guacamole-Remote`, `SP-N8N-Flows`, `SP-Mail-Enterprise`, `SP-Monitoring-View`, `SP-AI-Node`, `SP-VPN-Access`, `SP-VM-Server`, `SP-VM-Desktop`.

### Ejecución parcial T1 — 2026-10-30

- Creados en Fenix los nueve grupos indicados, vacíos y de seguridad/global, en `CN=Users,DC=pinguinoseguro,DC=cl` (el contenedor predeterminado de `samba-tool group add`).
- Verificación en vivo con `sudo -n samba-tool group show <grupo>` para cada uno: `groupType: -2147483646` (seguridad + global); no aparece atributo `member`, por lo que no tienen miembros.
- No se asignaron permisos. OUs de tenants, usuarios piloto, cuenta delegada y reordenamiento de cuentas siguen pendientes; T1 permanece abierto.
- [ ] Estructura: `OU=<RUT>,OU=Tenants` por cliente piloto; mover humanos tenant a su OU.
- [ ] Crear `svc-portal-provision` con delegación **solo** sobre `OU=Tenants` (nunca Domain Admin).
- [ ] Reordenar: `n8n`, `monitoreo` → `OU=ServiceAccounts` como `svc-n8n`, `svc-monitoreo` (UAC servicio 66048), miembros solo de su grupo `SP-*`.
- [ ] Verificar `svc-guacamole-bind`, `svc-dovecot-bind` en sus grupos.
- Ver spec: `docs/ops/ad-servicios-y-gpos.md` §2–§4.

## T2. GPOs por servicio — `agente:infra-ad`

- [ ] `GPO-SP-ServiceAccounts-DenyInteractive` → `OU=ServiceAccounts`.
- [ ] `GPO-SP-MailUsers-Lockdown` → `OU=MailUsers`.
- [ ] `GPO-SP-Tenants-Base` → `OU=Tenants` (passwords: complejidad on, 7+, historial 24, expiración 42d, bloqueo 30min — política vigente 2026-10-30).
- [ ] `GPO-SP-PortalAdmins` → filtrado a `SP-Portal-Admins`.
- Ver spec: `docs/ops/ad-servicios-y-gpos.md` §5.

## T3. Portal: LDAPS + entitlements + perfil multitenant — `agente:portal` (repo `pinguinoseguro_web`)

- [ ] `LDAP_URL=ldaps://10.88.0.1:636` + `LDAP_BASE_DN` + CA + `PORTAL_ADMIN_GROUP_DN` en runtime Fenix.
- [ ] `resolveEntitlements(memberOf)` en `services/adAuth.ts`: grupo → set de servicios. Tenant desde el **DN** (`OU=<RUT>`), nunca del navegador.
- [ ] Perfil: "Mis servicios" (filtrado por entitlements), "Solicitar servicio" (ticket + aprobación admin del tenant), "Seguridad de la cuenta" (cambio clave AD — spec en vault `TAREA_PORTAL_AUTOSERVICIO_CLAVE_AD`).
- [ ] Vista admin-tenant: alta/baja en su OU vía `svc-portal-provision`; baja = deshabilitar, nunca borrar.
- [ ] Cuotas por plan en Postgres (`tenants.max_vms/max_ram_mb/max_disk_gb`).
- Ver spec: `docs/ops/portal-multitenant.md`.

## T4. Terraform `tenant-compute` — `agente:iac`

- [ ] `modules/tenant-compute/`: red Podman dedicada por tenant, contenedor servidor (SSH) o escritorio (xRDP/noVNC), DNS interno, node-exporter → Marte.
- [ ] Sin KVM: fenix/kingu Azure sin `/dev/kvm` (verificado 2026-10-30). Contenedores rootless, cuota CPU/RAM/disco.
- [ ] Alta Guacamole automática al desplegar (conexión RDP/VNC/SSH asignada solo a su `objectGUID`); revoke al quitar el grupo.
- [ ] Antes de elegir escritorio, seguir [`guacamole-servicios-remotos-plan-2026-10-30.md`](guacamole-servicios-remotos-plan-2026-10-30.md): piloto xRDP/RDP como candidato Guacamole; noVNC es un canal alternativo. Resolver en prueba la conversión `objectGUID` → principal LDAP/Guac autorizado.
- [ ] Conectar con `/api/portal/deploy` existente (servicio `services/deployment.ts`, tests en `__tests__/api/deployment-route.test.ts`).
- Ver spec: `docs/ops/terraform-tenant-compute.md`.

## T5. HA + backups — `agente:infra-ha` (después de T0–T4)

- [x] Postgres cron 03:00 UTC configurado + gzip + SHA256 + rsync por WireGuard; restore real desde copia Kingu probado el2026-10-31. Primera ejecución automática todavía no observada.
- [x] Jaime designó Marte como segundo backend (2026-10-31). Standby PostgreSQL streaming, réplica Redis y backend en espera operativos en Marte; ver evidencia abajo. Pendiente: failover/DNS.
- [ ] Status page informativa (sin SLA contractual hasta restore verificado).
- Diseño existe en vault (`PLAN_DESPLIEGUE_SENTINEL_HA`); aquí es ejecutar.

### Evidencia T5 — recuperación PostgreSQL, 2026-10-31

- Producción inspeccionada: `sentinel-postgres` PostgreSQL16.15, primaria (`pg_is_in_recovery=false`) y **cero** conexiones en `pg_stat_replication`. No se reinició ni modificó la base/volumen vivo: solo snapshot SQL consistente y `pg_dump`. Credenciales rotadas no se copiaron ni expusieron.
- Evidencia final autoritativa: `sentinel_backup_20261031_060109.sql.gz`,1.259.643bytes, SHA256 `f3801232d7d3471e5215a34e9b972c4f47ff5da119fa16bb293d5449eec3debe`; inicio06:01:08.500104UTC, fin06:01:15.226589UTC. Las corridas anteriores se conservan como historial, no sustituyen este resultado.
- `scripts/backup/recovery.py` envió archivo, checksum y manifiesto a Kingu por SSH4222/WireGuard; recuperó la copia realmente almacenada en `/home/jnovoas/backups/sentinel/fenix-postgres` y restauró con la imagen local fija `sha256:6a2e324ebe59af6031c4c1cd96c1d5072c2ebc36563d2196365e43b8297c062d`, red none, sin puertos, tmpfs512MiB, memoria512MiB/CPU1 y sin volúmenes vivos.
- Coincidieron16 tablas,49.538filas por conteo/fingerprint y297registros de catálogo/large objects. Invariantes SHA256 `86e4affe3412075395ae366ea956605cca32b570d63c147a17dc11c0436815f7`. Temporales propios eliminados; copia off-node y reporte0600 conservados en directorio0700.
- Tiempos finales: dump1,097s; transferencia0,366s; restore+verificación3,753s; total6,727s. Esto mide restore PostgreSQL aislado con imagen disponible, **no** RTO de host/aplicación. No prueba roles globales, secretos, Redis, checkpoints Cortex, PITR ni failover.
- Cron único del usuario real `jnovoas` (UID1001),03:00 diario Etc/UTC: `/usr/bin/python3 .../recovery.py --config /home/jnovoas/.sentinel-backup-recovery.json`. Primera ejecución automática prevista2026-11-01 y aún no observada. Lock evita concurrencia; retención automática sigue deshabilitada.
- Verificación final: test unitario de recuperación, `bash -n` de scripts y restore real completos pasan. La guarda de capacidad rechaza antes del backup cuando `2*database_bytes +128MiB` supera el tmpfs de512MiB.
- RPO objetivo programado24h más retrasos/fallos, no garantizado; no WAL/PITR, cifrado en reposo ni WORM. El tránsito sí usa SSH sobre WireGuard.
- **Standby Marte operativo (2026-10-31 ~06:35 UTC):** `sentinel-postgres-standby` en Marte, red host, volumen `/var/lib/sentinel-postgres-standby`, `hot_standby=on`, imagen `postgres:16-alpine`. Primario ve `pg_stat_replication=10.88.0.6|streaming|async`; slot físico `marte_standby`. Prueba funcional: fila insertada en Fenix leída en Marte (`pg_is_in_recovery=true`); tabla de prueba eliminada después. Secreto `replicator` en `/etc/sentinel/postgres-replication-password` (0600) en ambos nodos, sincronizado por SSH; rol con `REPLICATION LOGIN` sin superusuario. `pg_hba` del primario limita replicación a `10.88.0.6/32` (+ red bridge interna por el DNAT de Docker); firewall Fenix acepta 5433 TCP solo desde `10.88.0.6/32`.
- Hallazgo: `10.88.0.1:5432` lo ocupa `laespiguita-db` (otro proyecto, no tocar). Sentinel publica replicación en `10.88.0.1:5433` dedicado + `monitoring_exposure`; `sentinel_internal` sigue `internal: true`. Compose validado y primario `healthy` tras recreación (16 tablas intactas).
- **Réplica Redis operativa (2026-10-31 ~06:40 UTC):** `sentinel-redis-replica` en Marte, red host, volumen `/var/lib/sentinel-redis-replica`, AOF activado, imagen `redis:7-alpine`. Primario ve `connected_slaves=1`, `slave0=10.88.0.6,online,lag=0`; réplica `role:slave`, `master_link_status:up`. Prueba funcional: clave escrita en Fenix leída en Marte; escritura directa en réplica rechazada (`READONLY`); clave de prueba eliminada del primario.
- Usuario ACL `replicator` mínimo (`+psync|+replconf|+ping`, sin canales), secreto en `/etc/sentinel/redis-replication-password` (0600) en ambos nodos. `aclfile /data/users.acl` persistido en volumen `redis_data`; sobrevive recreaciones. Publicación WG dedicada `10.88.0.1:6380`; firewall acepta solo desde `10.88.0.6/32`.
- Incidente controlado: el primer `ACL SAVE` persistió `user default on nopass` y dejó Redis sin contraseña (backend 503). Se restauró la contraseña del default en el ACL, `ACL SAVE`, backend 200 y `NOAUTH` verificado sin credencial. Sin pérdida de datos (AOF intacto).
- **Backend en espera (2026-10-31 ~06:44 UTC):** `sentinel-backend-standby` en Marte, misma imagen `dd532f7a-gamma-review-1`, env `/etc/sentinel/backend-standby.env` (0600, mismas claves JWT/LDAP, DB/Redis a réplicas locales), puerto solo loopback. Health 503 esperado: DB `healthy/is_primary:false`, Redis `READONLY` (réplica). El 503 acredita modo espera, no fallo. Procedimiento de promoción/failback en `docs/ops/failover-fenix-marte.md`, validado en seco (estados reales, sin promover).
- **Ensayo failover 2026-10-31:** promoción Marte con pérdida cero (LSN `0/822D420` idéntico), failback a Fenix timeline 3, réplicas reconstruidas y verificadas. Detalle en `docs/ops/failover-fenix-marte.md`.
- **Fixes backend 2026-10-31:** login AD roto por `entry.raw_attributes` (inexistente en ldap3 2.9.1; es `entry.entry_raw_attributes`) — ningún login AD funcionaba; corregido y verificado con sesión real. Dashboard 500 por funciones perdidas en refactor (`get_system_metrics`, `get_gpu_metrics`, `get_network_metrics`, `get_repo_activity`, `get_db_health`, `check_thresholds_and_log`) — restauradas mínimas con psutil/fallbacks que nunca lanzan. Imagen `sentinel-backend:dd532f7a-gamma-review-4` healthy. Cableado Cortex: `CORTEX_INTERNAL_URL=http://10.88.0.1:8000` en `sentinel-frontend.service.d/cortex.conf` (el default `http://backend:8000` solo vale en compose mononodo).

## T6. Pool soberano GPU — `agente:ia` (con cliente piloto firmado)

- [ ] Omnirouter :20128 + GPU compartida; Nivel 1 CPU (`sovereign-ai-node`, sin GPU) puede ir en T4.
- Ver vault: `ESTRATEGIA_NEGOCIO_IA_SOBERANA`, `ARQUITECTURA_INFERENCIA_SOBERANA`.

## T7. Poblado monitoreo Marte — `agente:obs`

- [ ] Exporters por nodo, métricas servicios Sentinel, Promtail→Loki, dashboards plataforma + por tenant, alertas vía n8n, rotar admin grafana.
- Ver spec: `docs/ops/marte-monitoreo-poblado.md`.

## T8. Guardian Marte → MyCNet Fenix → CrystalRuntime — `agente:PuenteCortex`

- Alcance autorizado: suscriptor WebSocket de Cortex y aceptación real de semillas remotas en lane A, configuración privada de Cortex Fenix y evidencia proyecto/vault. Main mantiene `guardian-uplink` Marte.
- No tocar scheduler/bio, enforcement eBPF, portal, Docker global ni reglas de firewall globales dentro de esta subtarea. La integración y los commits corresponden al agente principal.
- Preflight 2026-10-30: `main` en `8f0423f3`; cambios previos en `Cargo.lock`, Compose Fenix y Guacamole preservados. `sudo -n true` pasó; Cortex `sentinel-cortex:8f0423f3` healthy; MyCNet escucha únicamente `10.88.0.1:7474/TCP` y `:4242/UDP`.
- La URL efectiva `ws://172.20.0.1:7474/api/v1/stream` no coincide con el listener. Cortex ya tiene egress `172.29.0.2/16`, zona Docker `ACCEPT`: corregir destino a la IP privada real antes de inventar DNAT/proxy/reglas.
- Aceptación: handshake y suscripción desde Cortex; seed remoto correlacionado hasta la inyección real del cristal, sin confundir amplitud cero con excitación ni QHC 1 Hz con DTC software.
- Despliegue observado: imagen `sentinel-cortex:8f0423f3-uplink-a1e1fe4a1045` (huella de árbol sin commit), digest `sha256:878ce8ddc65a4e10fe2aa70cdb71d5d0db6742724faf28bd9d206201d84b6bf3`; solo Cortex recreado, healthy. URL corregida a `ws://10.88.0.1:7474/api/v1/stream`, backup protegido, Compose válido, sin cambios de firewall/Docker global.
- Evidencia propia: 23:54:37 UTC WS101 y frames recibidos; 23:54:41 token647121428/raw0 aceptado realmente por lane A. QHC=true, pero PULSE CHECK Valid=false/Coherence=False; frecuencia DTC no medida por falta de sesión autorizada.
- Pruebas finales: 59/60 pasan, incluidas las6 del puente; falla `test_truth_claim_handler_smoke_aiopsdoom_intercept` (`verification_time_us.is_number()`), causalidad no establecida, sin reintento ni cambio fuera de alcance. Detalle/límites/incidente de captura: [puente-mycnet-cortex-2026-10-30](puente-mycnet-cortex-2026-10-30.md); vault `sentinel/15_Puente_MyCNet_Cortex_2026-10-30.md`.
- Correlación final propia 23:57:56 UTC: 12/12 event_id realmente emitidos en WAL Marte, convertidos con el mismo DefaultHasher del uplink, coinciden con tokens aceptados por CrystalRuntime Fenix. Ejemplo `guardian-alpha-80945644173814-225437-EXEC_ALLOWED` → token711715798 → lane A índice22 a23:57:55.950191, raw0. La sonda coordinada PID225249 no apareció en22s (reporte Main); no se declara cobertura de todo exec ni se le atribuyen estas filas.

## T9. Scheduler observado y checkpoint real — `agente:principal`

- Retirados encolados ficticios GC/PhaseAlign/BackupS60 y heartbeat QHC→BIO.
- La compuerta nativa observa igualdad exacta de fase/amplitud nodo a nodo en
  las dos lanes existentes; no fuerza su estado ni usa senos temporales.
- Checkpoint local real por `CrystalRuntime::persist`, conservando plazo60s y
  ruta crítica independiente de portal/presencia; éxito y fallo separados.
- DTC, evolución/PID y drive continuo no se sustituyen por trabajos del scheduler.
- El modelo temporal C/experimentos permanece separado de la compuerta nativa.
- Detalle, pruebas y evidencia de despliegue:
  [scheduler-observado-2026-10-31.md](scheduler-observado-2026-10-31.md).
- Pendiente fuera de esta corrección: definir/conectar presencia de operador
  autorizada; no asumir que QHC, Redis sin validar o el singleton FFI la proveen.


---

## Reglas para todos los agentes

Pegable en cada prompt (del procedimiento estándar §7):

> Despliegue Sentinel: `sudo -n` siempre en remoto; cero passwords/tokens en CLI; prohibido `curl -k`; prohibido `sed -i` en `/etc` (plantilla + backup + validate); imágenes pineadas; `graphify update` una vez; Soma e inferencia GPU fuera de alcance; hercules/ocean no se tocan salvo T0; marte por 4222; un cambio = un commit + push + entrada en vault. Leer `docs/ops/procedimiento-despliegue-estandar.md` antes de empezar.
