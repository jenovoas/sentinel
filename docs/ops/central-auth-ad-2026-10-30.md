# Autenticación humana centralizada en Samba AD

**Fecha:** 2026-10-30
**Entornos:** Fenix (`main`, systemd) y Kingu (servicios de producción)
**Objetivo:** AD es la autoridad única de contraseña humana. Los servicios
pueden conservar perfiles, tenants, membresías y roles, pero no contraseñas ni
hashes locales reutilizables.

## Estado confirmado

- **Correo en Fenix:** Dovecot IMAP y Postfix SMTP AUTH autentican contra AD por
  LDAPS. El passdb local de Dovecot fue retirado. Alias de correo comparte la
  identidad de AD.
- **Portal Pinguino Seguro:** la API activa en Fenix usa bind UPN por LDAPS. Su
  PostgreSQL conserva `objectGUID` y asignaciones tenant/rol; no almacena
  contraseñas. TLS hacia el PDC y health HTTP 200 fueron comprobados. Falta
  completar una autenticación válida interactiva y MFA.
- **API Sentinel:** el código ahora autentica por bind UPN a AD y utiliza la
  fila `users` solamente como asignación tenant/perfil/rol. La migración elimina
  los hashes bcrypt existentes y agrega el vínculo por `objectGUID`. El
  despliegue runtime y su verificación se registran abajo cuando terminen; no
  se debe inferir despliegue por el commit.
- **Cortex:** acepta JWT emitidos por Sentinel; no mantiene inicio de sesión ni
  credenciales humanas propias.
- **n8n:** contenedor activo versión 1.41.0. Usa gestión de usuarios propia.
  LDAP, SAML y OIDC no están disponibles en Community; LDAP/SSO requieren
  licencia self-hosted Business/Enterprise. Por tanto, sigue siendo una brecha
  para el requisito global hasta integrar un IdP compatible o sustituir la
  edición/servicio. No reutilizar ni sincronizar contraseñas locales.
- **Grafana:** no se encontró un servicio Grafana activo en Kingu ni Fenix en la
  comprobación del 2026-10-30. La imagen de Compose no equivale a un servicio
  desplegado. Grafana OSS sí soporta LDAP; debe conectarse a AD antes de
  habilitar usuarios interactivos si vuelve a desplegarse.
- **Cuentas técnicas:** PostgreSQL, Redis, LDAP bind y credenciales de agentes
  son identidades de servicio, no cuentas humanas; deben seguir separadas,
  limitadas y protegidas. No usar una cuenta de servicio para acceso humano.

## Diseño de Sentinel

1. El backend verifica la contraseña mediante bind LDAPS directo con el UPN
   presentado. Verifica CA y nombre TLS; no registra la contraseña.
2. AD devuelve `objectGUID`, UPN/correo y pertenencia directa a grupos. La fila
   local se busca dentro de la organización solicitada usando primero el
   `objectGUID`; para filas existentes se permite un enlace inicial por correo.
3. La fila debe existir, estar activa y pertenecer a la organización. La
   autorización multitenant continúa en Sentinel; autenticarse en AD no concede
   membresías de tenant automáticamente.
4. `Sentinel Admins` determina el privilegio global. Los roles tenant siguen
   siendo asignaciones de aplicación. Si LDAP no está disponible, el endpoint
   responde 503; credenciales inválidas responden 401.
5. PostgreSQL deja `password_hash` nullable por compatibilidad de esquema, pero
   la migración borra todos sus valores. Ningún flujo de login lee ese campo.

La implementación usa `ldap3` con TLS obligatorio y un bridge interno dedicado
`172.23.0.0/16`; el host bridge es `172.23.0.1`. El firewall de Fenix permite
desde ese origen únicamente TCP/636 en la zona `ad-ldap`. El servicio Samba AD
escucha esa interfaz además de las interfaces ya autorizadas. No abrir LDAP/389
ni exponer el bridge fuera de Fenix.

## Despliegue Sentinel

Estado: **preparación local**, hasta que se añada evidencia runtime.

Antes de ejecutar la migración:

1. Confirmar rama `main`, imagen y revisión actual de Sentinel en Fenix.
2. Crear respaldo root-only de PostgreSQL, `/etc/sentinel/backend.env`, CA,
   `smb.conf` y configuración Compose. Verificar que el dump no esté vacío.
3. Añadir el bridge a la zona `ad-ldap` y a `interfaces` de Samba; reiniciar
   Samba solo cuando el bridge exista y se haya respaldado su configuración.
4. Configurar LDAP por entorno, montar CA de solo lectura, construir la imagen y
   recrear únicamente `backend`.
5. Confirmar la revisión Alembic anterior antes de migrar. La migración elimina
   irreversiblemente los hashes locales; el rollback requiere restaurar el dump
   previo, no ejecutar downgrade.
6. Verificar logs de migración, health endpoint, handshake LDAPS desde el
   contenedor, rechazo 401 de credencial inválida y que no existan hashes
   locales. Verificar autenticación válida solo con una sesión AD autorizada.

## Procedimiento de auditoría de identidad

- Enumerar servicios activos y distinguir interfaces humanas de APIs internas.
- Revisar configuración efectiva/runtime, no solo archivos Compose o imágenes.
- Confirmar proveedor de credenciales, grupos, mapeo de roles y tenant,
  recuperación de cuenta, MFA y comportamiento ante caída de AD.
- Buscar tablas/campos de contraseña, bcrypt/Argon hashes, cuentas owner y
  bypasses de proxy. No leer ni imprimir secretos durante la auditoría.
- Probar fallo de AD, credencial inválida y una autenticación válida con
  contraseña introducida de forma segura; revisar logs sin copiar credenciales.
- Registrar cada despliegue tanto aquí como en la vault, separando cambios
  preparados de estado realmente desplegado.

## Referencias

- [`central-auth-mail-2026-10-30.md`](central-auth-mail-2026-10-30.md)
- Pinguino Seguro: `docs/ops/central-auth-multitenant.md`, CHG-0023 y ADR-0011.
- n8n LDAP/SSO: requiere edición Business/Enterprise self-hosted.
- Grafana OSS LDAP: documentación oficial de autenticación LDAP.
