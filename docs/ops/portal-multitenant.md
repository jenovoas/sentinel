# Portal multitenant — spec de implementación (repo `pinguinoseguro_web`)

> Ejecuta `agente:portal`. Prerrequisitos: T0 (AD único en fenix), T1 (grupos `SP-*`, OUs tenant, `svc-portal-provision`).
> Spec madre de autoservicio de clave: vault `SecurePenguin/TAREA_PORTAL_AUTOSERVICIO_CLAVE_AD` (criterios de aceptación y prohibiciones; no duplicar aquí).

## 1. Punto de partida verificado (2026-10-30)

- `services/adAuth.ts`: autentica por LDAPS, devuelve `AdUser` con `memberOf: string[]`; `determineRole()` admin/cliente por `PORTAL_ADMIN_GROUP_DN`.
- `utils/request-session.ts`: sesión canónica vinculada a `objectGUID`.
- `app/api/portal/deploy/` + `deployment-catalog/`: existen con tests (tenant desde sesión, idempotency-key). Falta el ejecutor Terraform (`services/deployment.ts` es interfaz).
- Diagnóstico vault 2026-10-30: runtime Fenix `:8080` sin `LDAP_URL`/`LDAP_BASE_DN`/`LDAP_TLS_CA_FILE`/`PORTAL_ADMIN_GROUP_DN`; corregir en este task.
- P0 abiertos (TODO.md del portal): servicios por tenant con datos reales, acciones (reiniciar/consola/backup), DTE real SII, aritmética S60 en facturación.

## 2. Entitlements desde AD

```ts
// services/entitlements.ts (nuevo, SRP: solo mapeo grupo→servicio)
const SERVICE_GROUPS = {
  'CN=SP-Guacamole-Remote,...': ['remote-desktop'],
  'CN=SP-VM-Server,...':        ['vm-server'],
  'CN=SP-VM-Desktop,...':       ['vm-desktop'],
  // ... resto de SP-*
} // DNs exactos salen de T1; comparar en minúsculas como determineRole() ya hace.
resolveEntitlements(memberOf: string[]): ServiceId[]
```

- Tenant: extraer `OU=<RUT>` del `distinguishedName` de la sesión. Si no hay OU tenant (ej. operador) → alcance global.
- Nunca aceptar `tenantId` del navegador (los tests ya lo exigen).

## 3. Perfil de usuario ("Mis servicios")

- Lista solo servicios de sus entitlements, con estado (activo/pendiente) desde `tenant_service_assignments` (tabla ya existe según TODO.md).
- "Solicitar servicio": crea ticket + notifica al admin de su OU. El admin aprueba → membresía AD (vía `svc-portal-provision`) → job Terraform (T4).
- "Seguridad de la cuenta": cambio de clave según spec de vault (reauth + step-up MFA, LDAPS con CA, sin persistir secretos, auditoría sin passwords).
- Admin-tenant: "Usuarios de mi tenant" (filtro `OU=<RUT>`), alta en su OU + grupos del plan, baja = `userAccountControl` deshabilitado (nunca delete).

## 4. Variables de entorno (runtime Fenix)

`LDAP_URL=ldaps://10.88.0.1:636`, `LDAP_BASE_DN`, `LDAP_TLS_CA_FILE`, `LDAP_TLS_SERVERNAME`, `PORTAL_ADMIN_GROUP_DN`. Sin estas, el endpoint responde 503 (comportamiento ya implementado 2026-10-30, commit `e0fa5c2`).

## 5. Criterios de aceptación

- Usuario `SP-VM-Desktop` no ve ni puede pedir `vm-server` (test de entitlements cruzados).
- Admin de `OU=RUT-A` no lista ni modifica usuarios de `OU=RUT-B` (test de aislamiento, como los existentes de deploy).
- Cambio de clave: clave vieja deja de autenticar en portal + Guacamole; sesiones previas invalidadas según diseño.
- `git diff --check`, ESLint, `tsc --noEmit`, suite del área en verde. Sin secretos en fixtures ni logs.
