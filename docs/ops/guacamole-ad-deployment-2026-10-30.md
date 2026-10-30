# Guacamole con autenticación centralizada en Samba AD

**Fecha:** 2026-10-30
**Estado:** desplegado en Fenix, publicado por Kingu; HTTPS y DNS comprobados.
**URL:** <https://guacamole.pinguinoseguro.cl>

## Arquitectura efectiva

- El DNS público `guacamole.pinguinoseguro.cl` apunta a `64.176.8.191`, IP pública de Kingu. Las consultas a los DNS autoritativos y a resolutores públicos devolvieron esa dirección.
- Kingu termina TLS en Nginx y envía el tráfico por WireGuard a Fenix (`10.88.0.1:8082`). El firewall de Fenix limita ese puerto a Kingu (`10.88.0.2`). El puerto de Guacamole no se publica en la interfaz pública.
- Fenix ejecuta Guacamole 1.6.0, guacd 1.6.0 y PostgreSQL 16 en contenedores. El navegador solo accede a la interfaz web; los perfiles de conexión se administran en Guacamole y no son cuentas de autenticación.
- Guacamole consulta Samba AD por LDAPS/TLS 1.3 en Fenix, validando la CA instalada en la imagen. La búsqueda de usuarios limita el acceso al grupo AD `Guacamole Users`; `Guacamole Admins` recibe permisos acotados para crear y auditar conexiones.
- PostgreSQL conserva autorización y configuración. Se retiró el usuario local inicial `guacadmin`; no se deben aprovisionar cuentas humanas ni contraseñas locales en Guacamole.
- El bind técnico `svc-guacamole-bind` y su contraseña se guardan fuera del repositorio, en `/etc/guacamole/guacamole.env` con permisos root-only. La memoria persistente contiene la referencia de custodia; no registrar el valor del secreto en Git.
- Se aprovisionaron cinco conexiones SSH: Fenix (`10.88.0.1`), Kingu (`10.88.0.2`), Hercules (`10.88.0.4`), Ocean (`10.88.0.5`) y Marte (`10.88.0.6`), todas en puerto `4222`. Soma queda excluido según decisión del usuario.
- Las conexiones usan `jnovoas` con una clave Ed25519 dedicada a Guacamole. La clave privada se guarda en PostgreSQL de Guacamole y en `/etc/guacamole/ssh/id_ed25519` en Fenix, sin versionarla. En cada servidor se agregó la clave pública sin reemplazar otras claves, con `restrict,pty` y restricción de origen: guacd/Fenix permite `172.26.0.3`; los nodos remotos permiten `10.88.0.1`. Para revocarla, quitar su entrada identificada como `guac-ssh-jnovoas-20261030` de `~jnovoas/.ssh/authorized_keys`.
- Las cinco claves Ed25519 de host están fijadas en `infrastructure/guacamole/ssh_known_hosts`, montado de solo lectura en **guacd** (el contenedor que negocia SSH). Para Fenix y Hercules se fijó la clave Ed25519 subyacente a los certificados de host; los cinco fingerprints de la lista se cotejaron con las claves activas observadas.
- Los perfiles conceden `READ` al grupo AD `Guacamole Users` y `READ` más `ADMINISTER` a `Guacamole Admins`. No se guardó la contraseña AD en los perfiles.

## Incidencia y corrección

El primer acceso presentó `SSL_ERROR_BAD_CERT_DOMAIN`: Nginx estaba sirviendo el certificado de `impacta.pinguinoseguro.cl`, que no incluía el nombre de Guacamole. Se emitió un certificado Let's Encrypt individual para `guacamole.pinguinoseguro.cl` y se activó el virtual host TLS con proxy a Fenix. El certificado observado vence el 2027-01-28 y Certbot instaló la tarea de renovación.

El contenedor respondía dentro de Docker, pero Docker no materializaba la publicación del puerto al estar la interfaz principal conectada únicamente a redes `internal`. Se agregó `guacamole_edge` como red puente no interna para el servicio web y se recreó únicamente el contenedor Guacamole. PostgreSQL y su volumen persistente no se recrearon. Tras el cambio, `docker inspect` mostró el mapa `10.88.0.1:8082 -> 8080/tcp` y Fenix respondió HTTP 200.

La IP de proxy confiable de Tomcat incluye Kingu (`10.88.0.2`) y el gateway de la red puente de publicación (`172.26.0.1`), para procesar los encabezados reenviados cuando Docker usa su proxy de usuario.

Tras la primera publicación, la página de login cargaba pero el envío de credenciales devolvía HTTP 500. La causa fue firewalld: el bridge interno de Compose (`172.25.0.0/16`) no estaba asignado a una zona que permitiera el tráfico entre Guacamole, PostgreSQL y guacd. Se agregó la zona `guac-internal`, con destino `DROP`, forwarding entre miembros de la zona y el origen limitado a `172.25.0.0/16`; se aplicó en configuración permanente y runtime. Con eso se habilitó solo el tráfico interno requerido y el acceso del host a servicios de ese bridge continúa bloqueado.

Para las conexiones SSH se añadieron en Fenix la zona `guac-edge` (origen `172.26.0.0/16`, destino `DROP`) y dos políticas persistentes, también con destino `DROP`: `guac-to-host` permite únicamente desde guacd (`172.26.0.3`) hacia `10.88.0.1:4222`; `guac-to-wgmesh` permite desde ese mismo origen TCP/4222 hacia `10.88.0.2`, `.4`, `.5` y `.6` por `wg0`, con masquerade para que los servidores remotos vean como origen WireGuard de Fenix (`10.88.0.1`). No se abrió SSH hacia las redes públicas.

La primera comprobación de conectividad se hizo desde el contenedor web y no representaba la ruta real de las sesiones. El SSH lo inicia guacd, que estaba conectado solo a `guacamole_internal` (`172.25.0.0/16`, sin gateway); por eso los perfiles abrían el túnel y se desconectaban con `SSH handshake failed`. Se conectó guacd también a `guacamole_edge` y se montó allí `ssh_known_hosts` como solo lectura. guacd ahora conserva su enlace interno con Guacamole y PostgreSQL, además de usar la ruta de salida limitada para SSH.

## Evidencia y límites de validación

- `nginx -t` pasó y Nginx recargó la configuración.
- La negociación TLS pública presentó `CN=guacamole.pinguinoseguro.cl`, emisor Let's Encrypt `YE1` y SAN `guacamole.pinguinoseguro.cl`.
- `curl --resolve guacamole.pinguinoseguro.cl:443:64.176.8.191` devolvió HTTP 200; el endpoint de Fenix `http://10.88.0.1:8082/` también devolvió HTTP 200.
- El arranque de Guacamole registró extensiones LDAP, PostgreSQL y protección contra intentos repetidos (`ban`) cargadas.
- El contenedor web se recreó una segunda vez para aplicar la lista de proxies confiables; `docker inspect` mostró el valor efectivo y Fenix volvió a responder HTTP 200.
- Después de aplicar la zona de firewall, los logs registraron autenticación exitosa de `jnovoas@pinguinoseguro.cl` por LDAP y `POST /api/tokens` con HTTP 200 desde su navegador. Se comprobó también conexión TCP desde Guacamole a PostgreSQL (`5432`), guacd (`4822`) y LDAPS (`636`). No se leyó ni guardó la contraseña humana.
- Jaime confirmó que pudo entrar con su usuario y que la página carga correctamente.
- Una solicitud controlada con una identidad inexistente recibió rechazo de credenciales; no volvió a producir HTTP 500. El GET de datos de sesión sin autenticación devuelve 403, como corresponde.
- La primera prueba de usuario mostró `SSH handshake failed` y desconexión inmediata. La inspección confirmó que guacd no tenía ruta por defecto; se corrigieron su red y el montaje de `ssh_known_hosts`. Luego, desde el namespace real de guacd (`172.26.0.3`), se autenticó por SSH en los cinco destinos con verificación estricta de las claves de host. El log confirmó `Auth key successfully imported` antes del fallo de handshake previo a la corrección.
- PostgreSQL contiene cinco perfiles SSH y permisos de grupo (`Guacamole Users`: `READ`; `Guacamole Admins`: `READ` y `ADMINISTER`). Se comprobaron nombres, protocolos, destinos y permisos por consulta; no se imprimió ni versionó la clave privada.
- Después de recrear Guacamole y provisionar los perfiles, la URL pública devolvió HTTP 200 con validación TLS correcta (`curl --resolve` al IP público, sin omitir la verificación del certificado). El intento de resolver el DNS desde la shell local no resolvió el nombre; la prueba directa con SNI/Host correcto confirmó endpoint y certificado.
- Falta repetir la apertura interactiva desde la sesión de Jaime después de esta corrección de guacd; la ruta, autenticación SSH y verificación de host ya pasaron desde el namespace exacto del proxy.
- En `nginx -t` aparece además una advertencia preexistente de valor duplicado `TLSv1.3` en el vhost de `pinguinoseguro`; la sintaxis valida y no impide servir Guacamole. No se modificó ese vhost.

## Operación y comprobación

- Compose: `infrastructure/guacamole/compose.yaml`.
- Configuración Nginx versionada: `infrastructure/guacamole/nginx/guacamole.pinguinoseguro.cl.conf`.
- Para ver estado en Fenix: `cd /home/jnovoas/proyectos/sentinel/infrastructure/guacamole && sudo -n docker compose --env-file /etc/guacamole/guacamole.env ps`.
- Para comprobar Nginx en Kingu: `sudo -n nginx -t && sudo -n systemctl reload nginx`.
- La renovación del certificado queda a cargo de Certbot en Kingu; verificarla con `sudo -n certbot renew --dry-run` en una ventana operativa.
- Mantener egress y acceso a redes Docker bajo revisión: `guacamole_edge` es no interna para que Docker publique el listener, mientras que PostgreSQL/guacd permanecen en la red interna y LDAPS usa su bridge dedicado.
- Firewall Fenix: revisar `sudo -n firewall-cmd --zone=guac-internal --list-all`, `sudo -n firewall-cmd --zone=guac-edge --list-all` y `sudo -n firewall-cmd --info-policy guac-to-host` / `guac-to-wgmesh`, además de sus equivalentes `--permanent`. `guac-internal` requiere `172.25.0.0/16`, `forward=yes` y `target=DROP`; `guac-edge` requiere `172.26.0.0/16` y `target=DROP`; las políticas SSH deben limitar origen a guacd `172.26.0.3` y destinos/puertos descritos arriba. No sustituir estas zonas por `trusted` ni ampliar sus destinos/puertos sin revisar el flujo.
- Clave dedicada: custodiar `/etc/guacamole/ssh/id_ed25519` en Fenix con permisos `0600`; no copiarla fuera del host ni añadirla al repositorio. Para rotarla, actualizar los perfiles y los cinco `authorized_keys`, verificar sesiones y retirar la clave anterior.

## Respaldo y trazabilidad

Se conservaron respaldos root-only previos a la intervención en Fenix y Kingu, bajo `/root/guac-deploy-20261030/backup/`. La zona DNS vive en la configuración operativa del servidor DNS autoritativo y no forma parte de este repositorio. El cambio de código se documenta aquí; la nota persistente de Guacamole en la vault complementa la evidencia operativa sin incluir secretos en Git.
