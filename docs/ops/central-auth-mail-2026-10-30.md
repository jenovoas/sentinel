# Integración de correo con Samba AD

**Fecha:** 2026-10-30
**Rama/plataforma:** `main` / Fenix Debian systemd
**Estado:** autenticación de IMAP y SMTP AUTH contra AD verificada en vivo

## Diseño vigente

- Samba AD en Fenix es la autoridad de contraseña. Dovecot usa LDAP passdb
  sobre LDAPS y valida las contraseñas de usuario con bind de AD.
- Postfix delega SMTP AUTH a Dovecot mediante SASL. Por tanto, IMAP y SMTP
  Submission comparten la misma identidad y contraseña de dominio.
- La cuenta técnica `svc-dovecot-bind` sirve para búsquedas LDAP en el
  directorio; no autentica a usuarios ni guarda una copia de sus contraseñas.
- El grupo `Mail-Users` limita qué cuentas del dominio tienen acceso al correo.
  Dovecot aplica un userdb estático UID/GID 5000 y Maildir bajo
  `/var/mail/vhosts/pinguinoseguro.cl/`.
- Las direcciones `@www` se resolvieron como `proxyAddresses` de la cuenta
  canónica. Comparten buzón y credencial AD; no tienen contraseña de alias.
- No se cambió la contraseña AD existente de `jnovoas`. La contraseña clara no
  está guardada en este repositorio.

## Cambios aplicados en Fenix

- Se creó `OU=MailUsers`, `OU=ServiceAccounts` y el grupo de seguridad
  `Mail-Users`; las identidades de buzón se agregaron/sincronizaron desde el
  directorio y sus atributos canónicos/alias.
- Se emitieron certificados LDAPS para Fenix PDC y Kingu DC adicional con una
  CA privada; el nombre/SAN del certificado del PDC se valida por LDAPS.
- Se instaló el módulo LDAP de Dovecot y se configuró
  `/etc/dovecot/ad-auth.conf` como archivo `root:root`, modo `0600`, con
  validación estricta de CA. `/etc/ldap/ldap.conf` usa `REFERRALS off` para
  que las búsquedas no sigan referrals públicos fuera del dominio.
- Se retiró `/etc/dovecot/users` de la configuración activa y se preservó en
  `/root/ad-mail-auth-2026-10-30/backup/retired-auth/dovecot-users-legacy`,
  modo root-only. No queda un passdb local habilitado.
- El script idempotente
  [`scripts/sync_ad_mail_identities.py`](../../scripts/sync_ad_mail_identities.py)
  está instalado en Fenix como
  `/usr/local/sbin/sentinel-sync-ad-mail-identities` (0750).

## Evidencia de verificación

- `doveadm auth test` aceptó una cuenta canónica y un alias `@www` con la
  contraseña de la identidad AD correspondiente.
- `doveadm user` resolvió UID/GID 5000 y la ruta Maildir canónica del alias.
- Un cliente SMTP de prueba completó STARTTLS y SMTP AUTH contra Postfix;
  no se envió ningún mensaje.
- Dovecot y Postfix quedaron activos con listeners IMAPS 993, SMTPS 465 y
  Submission 587.
- En Kingu se comprobó la replicación entrante de usuarios y del grupo
  `Mail-Users` desde Fenix; `drs showrepl --summary` en Kingu devolvió
  `ALL GOOD`. Fenix aún muestra errores previos de replicación inversa desde
  Kingu (`WERR_FILE_NOT_FOUND`/`NTTIME(0)`), así que no se afirma que AD replique
  correctamente en ambas direcciones.

## Operación y rollback

Usar `doveadm auth test usuario@pinguinoseguro.cl` con ingreso interactivo de
la contraseña; no pasarla como argumento ni registrarla en shell history.
Revisar `systemctl is-active dovecot postfix` y el log de autenticación sin
copiar secretos. Las configuraciones anteriores están respaldadas bajo
`/root/ad-mail-auth-2026-10-30/backup/` en Fenix, con permisos root-only.

Las credenciales actuales de `max` y `svc-dovecot-bind`, así como el estado de
las credenciales canónicas/aliases, se conservan solo en la vault privada del
usuario. Nunca copiarlas aquí ni a Git. El procedimiento integrado de portal y
correo está en el runbook del repositorio Pinguino Seguro, junto con CHG-0023.
