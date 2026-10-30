# AD como fuente de autorización de servicios — Sentinel / PinguinoSeguro

**Fecha:** 2026-10-30 · **Estado AD verificado en vivo** (Fenix): 14 usuarios, 43 grupos, 4 OUs, 2 GPOs default.
**Decisión registrada:** AD es la única fuente de identidad (portal, correo, Guacamole). Sin passwords locales. Detalle de autoservicio de clave en vault: `SecurePenguin/TAREA_PORTAL_AUTOSERVICIO_CLAVE_AD`.

## 1. Estado de partida (evidencia, no especulación)

| Elemento | Fenix (gana) | Hercules (fósil) |
|---|---|---|
| Usuarios | 14: `jnovoas`, `admin`, `max`, `ventas`, `info`, `contacto`, `scliente`, `n8n`, `monitoreo`, `svc-guacamole-bind`, `svc-dovecot-bind`, + base | 4: solo base (Guest, Administrator, jnovoas, krbtgt) |
| Grupos | 43 (incl. `Portal Admins`, `Guacamole Users`, `Sentinel Admins`) | 39 (solo default) |
| Computers | `FENIX$`, `KINGU$` | `OCEAN$`, `HERCULES$` |
| FSMO | Fenix se declara PDC; Kingu lo reconoce | Hercules se declara PDC; Ocean lo reconoce → **split-brain** |

Conclusión: degradar hercules/ocean (T0), nada que migrar.

### OUs existentes

`Tenants`, `MailUsers`, `SecurePenguin`, `ServiceAccounts`, `Domain Controllers`.

### Cuentas a reordenar

- `svc-guacamole-bind`: `OU=ServiceAccounts`, UAC 66048 (servicio, no expira) ✅ bien.
- `n8n`, `monitoreo`: en `OU=MailUsers` como buzones ❌ → mover a `OU=ServiceAccounts` como `svc-n8n`, `svc-monitoreo`.

### Política de passwords vigente (dominio, 2026-10-30)

Complejidad on, longitud mínima 7, historial 24, edad mínima 1 día, máxima 42 días, bloqueo 30 min, umbral 0 (sin bloqueo por intentos — **endurecer en GPO-SP-Tenants-Base**).

## 2. Grupos por servicio (el contrato)

Alta = agregar al grupo. Baja = quitar del grupo. Todo lo demás es consecuencia automática.

| Grupo | Otorga |
|---|---|
| `SP-Portal-Admins` | Administrar su tenant (alta/baja usuarios y servicios) |
| `SP-Guacamole-Remote` | Conexiones de escritorio remoto asignadas |
| `SP-N8N-Flows` | Workflows n8n propios (owner = objectGUID) |
| `SP-Mail-Enterprise` | Buzón activo, cuota según plan |
| `SP-Monitoring-View` | Grafana embebido solo-lectura de su tenant |
| `SP-AI-Node` | Nodo IA soberana Nivel 1 (Ollama :11434 en su VM) |
| `SP-VPN-Access` | Peer WireGuard/MyCNet |
| `SP-VM-Server` | Pedir servidores (contenedor aislado + SSH) |
| `SP-VM-Desktop` | Pedir escritorios (xRDP/noVNC vía Guacamole) |

## 3. Tenant = OU

`OU=<RUT>,OU=Tenants,DC=pinguinoseguro,DC=cl`. El portal deriva el tenant del **DN de la sesión** (atributo `distinguishedName`), jamás de parámetros del navegador. Un admin-tenant solo opera dentro de su OU. El grupo admin global (`PORTAL_ADMIN_GROUP_DN`) queda reservado al operador.

## 4. Cuenta delegada de aprovisionamiento

`svc-portal-provision` en `OU=ServiceAccounts`: delegación de control **solo** sobre `OU=Tenants` (crear/deshabilitar usuarios, modificar membresías `SP-*`). Sin Domain Admin, sin logon interactivo (cubierto por GPO §5). El portal la usa para altas/bajas; nunca credenciales del operador.

## 5. GPOs a crear

| GPO | Vínculo | Contenido exigible en Samba |
|---|---|---|
| `GPO-SP-ServiceAccounts-DenyInteractive` | `OU=ServiceAccounts` | Denegar logon interactivo/RDP a `svc-*`; passwords largos sin expiración; auditoría de uso |
| `GPO-SP-MailUsers-Lockdown` | `OU=MailUsers` | Hereda passwords del dominio; bloqueo de pantalla; sin instalación de software |
| `GPO-SP-Tenants-Base` | `OU=Tenants` | Passwords del dominio + **umbral de bloqueo >0** (la política vigente tiene 0); expiración 42d; auditoría de logon; denegar acceso salvo grupos explícitos |
| `GPO-SP-PortalAdmins` | Filtrado a `SP-Portal-Admins` | Timeout de sesión corto; MFA cuando el portal lo exija |

Límite honesto: las GPOs de Samba no restringen "qué botón ve cada usuario" — eso lo hace el portal (§6) y cada servicio (§7).

## 6. Portal: del grupo al catálogo (repo `pinguinoseguro_web`)

- `ActiveDirectoryAuthService` ya devuelve `memberOf` (`services/adAuth.ts:13,120`). Falta `resolveEntitlements(memberOf)` → set de servicios visibles/pedibles.
- `determineRole()` actual solo distingue admin/cliente por un DN (`adAuth.ts:149`). Extender sin romper el login existente.
- Cuotas por plan **en Postgres** (`tenants.max_vms/max_ram_mb/max_disk_gb`), no en AD.

## 7. Restricción real por servicio (tres capas)

1. **AD**: pertenencia a grupos + GPOs de higiene.
2. **Portal**: catálogo filtrado por entitlements; "Solicitar servicio" → ticket + aprobación del admin de su tenant.
3. **Servicio**: Guacamole solo conexiones asignadas a su `objectGUID`; n8n owner por tenant; contenedor en red Podman dedicada por tenant; Grafana carpeta+datasource por tenant; mail solo su UPN.

Baja de servicio: quitar grupo → job revoca conexión Guacamole + detiene contenedor. Nunca borrado manual en consolas.
