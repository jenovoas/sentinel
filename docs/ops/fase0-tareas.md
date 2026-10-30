# Tareas Fase 0 — AD único + servicios por contrato + VMs por Terraform

> Rama: `main` · Origen: sesión 2026-10-30 (auditoría Codex, vault SecurePenguin, estado AD en vivo).
> Cómo trabajar: un agente = una tarea. Cada tarea cierra con evidencia + commit + entrada en vault.

## T0. Consolidar AD único (FSMO ya en Fenix) — `agente:infra-ad`

- Corrección 2026-10-30 (operador): commit `b22835c3` registra que a las 17:55 se activó en Fenix la base restaurada desde Hercules con los siete FSMO apuntando a FENIX (auditoría multínodo:399-404). No fue transferencia en vivo (`fsmo transfer`), pero Fenix y Kingu confirman roles en Fenix. **No repetir la transferencia.**
- Las vistas locales antiguas de hercules/ocean que se declaran PDC son datos estancados, no split-brain operativo. No bloquear T1–T4 por ellas.
- [ ] Subtask DNS: Samba DNS de Fenix en `:5353` resuelve `kingu.pinguinoseguro.cl` → `10.88.0.2`; BIND en `:53` (resolver local de Fenix) aún devuelve NXDOMAIN y su SRV LDAP anuncia solo Fenix. Revisar vista BIND (zona/split-horizon) sin tocar sistemas remotos.
- [ ] Degradar hercules/ocean a solo DNS **solo después** de validar replicación fenix↔kingu y resolver qué hacer con sus vistas locales (demote o apagado samba, BIND/PowerDNS públicos intactos).
- [ ] Evidencia: `drs showrepl` en kingu 0 fallos inbound desde fenix; conteo usuarios = 14 en ambos; `dns1/dns2.pinguinoseguro.cl` resuelven.
- Hallazgo DRS 2026-10-30: replicación útil fenix→kingu SANA (0 fallos). Fallo inverso kingu→fenix (`WERR_FILE_NOT_FOUND`, 40+ fallos) irrelevante: kingu no origina objetos. Causa probable DNS, no AD.
- Entregable: nota en `docs/ops/` + entrada vault.

## T1. Grupos SP-* + OUs tenant + cuenta delegada — `agente:infra-ad`

- [ ] Crear grupos: `SP-Portal-Admins`, `SP-Guacamole-Remote`, `SP-N8N-Flows`, `SP-Mail-Enterprise`, `SP-Monitoring-View`, `SP-AI-Node`, `SP-VPN-Access`, `SP-VM-Server`, `SP-VM-Desktop`.
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

- [ ] Postgres cron 03:00 + gzip + SHA256 + rsync por WireGuard; restore probado (no solo backup).
- [ ] DNS cruzado + Traefik failover Kingu; réplica acordada.
- [ ] Status page informativa (sin SLA contractual hasta restore verificado).
- Diseño existe en vault (`PLAN_DESPLIEGUE_SENTINEL_HA`); aquí es ejecutar.

## T6. Pool soberano GPU — `agente:ia` (con cliente piloto firmado)

- [ ] Omnirouter :20128 + GPU compartida; Nivel 1 CPU (`sovereign-ai-node`, sin GPU) puede ir en T4.
- Ver vault: `ESTRATEGIA_NEGOCIO_IA_SOBERANA`, `ARQUITECTURA_INFERENCIA_SOBERANA`.

## T7. Poblado monitoreo Marte — `agente:obs`

- [ ] Exporters por nodo, métricas servicios Sentinel, Promtail→Loki, dashboards plataforma + por tenant, alertas vía n8n, rotar admin grafana.
- Ver spec: `docs/ops/marte-monitoreo-poblado.md`.

---

## Reglas para todos los agentes

Pegable en cada prompt (del procedimiento estándar §7):

> Despliegue Sentinel: `sudo -n` siempre en remoto; cero passwords/tokens en CLI; prohibido `curl -k`; prohibido `sed -i` en `/etc` (plantilla + backup + validate); imágenes pineadas; `graphify update` una vez; Soma e inferencia GPU fuera de alcance; hercules/ocean no se tocan salvo T0; marte por 4222; un cambio = un commit + push + entrada en vault. Leer `docs/ops/procedimiento-despliegue-estandar.md` antes de empezar.
