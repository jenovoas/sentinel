# Guacamole con autenticación centralizada en Samba AD

**Fecha:** 2026-10-30
**Estado:** desplegado en Fenix, publicado por Kingu; HTTPS y DNS comprobados.
**URL:** <https://guacamole.pinguinoseguro.cl>

> **Actualización 30/31 de octubre:** la recuperación descrita al final fija
> `guacamole_internal=172.27/16` y `guacamole_ssh_egress=172.30/16`,
> guacd `172.30.0.2`. Las IP anteriores en la cronología son históricas.

## Arquitectura efectiva

- El DNS público `guacamole.pinguinoseguro.cl` apunta a `64.176.8.191`, IP pública de Kingu. Las consultas a los DNS autoritativos y a resolutores públicos devolvieron esa dirección.
- Kingu termina TLS en Nginx y envía el tráfico por WireGuard a Fenix (`10.88.0.1:8082`). El firewall de Fenix limita ese puerto a Kingu (`10.88.0.2`). El puerto de Guacamole no se publica en la interfaz pública.
- Fenix ejecuta Guacamole 1.6.0, guacd 1.6.0 y PostgreSQL 16 en contenedores. El navegador solo accede a la interfaz web; los perfiles de conexión se administran en Guacamole y no son cuentas de autenticación.
- Guacamole consulta Samba AD por LDAPS/TLS 1.3 en Fenix, validando la CA instalada en la imagen. La búsqueda de usuarios limita el acceso al grupo AD `Guacamole Users`; `Guacamole Admins` recibe permisos acotados para crear y auditar conexiones.
- PostgreSQL conserva autorización y configuración. Se retiró el usuario local inicial `guacadmin`; no se deben aprovisionar cuentas humanas ni contraseñas locales en Guacamole.
- El bind técnico `svc-guacamole-bind` y su contraseña se guardan fuera del repositorio, en `/etc/guacamole/guacamole.env` con permisos root-only. La memoria persistente contiene la referencia de custodia; no registrar el valor del secreto en Git.
- Se aprovisionaron cinco conexiones SSH: Fenix (`10.88.0.1`), Kingu (`10.88.0.2`), Hercules (`10.88.0.4`), Ocean (`10.88.0.5`) y Marte (`10.88.0.6`), todas en puerto `4222`. Soma queda excluido según decisión del usuario.
- Las conexiones usan `jnovoas` con una clave Ed25519 dedicada a Guacamole. La clave privada se guarda en PostgreSQL de Guacamole y en `/etc/guacamole/ssh/id_ed25519` en Fenix, sin versionarla. En cada servidor se agregó la clave pública sin reemplazar otras claves, con `restrict,pty` y restricción de origen: Fenix permite el IP fijo de guacd en `guacamole_ssh_egress` (`172.30.0.2`); los nodos remotos permiten `10.88.0.1`. Para revocarla, quitar su entrada identificada como `guac-ssh-jnovoas-20261030` de `~jnovoas/.ssh/authorized_keys`.
- Las identidades SSH están fijadas en `infrastructure/guacamole/ssh_known_hosts`, montado de solo lectura en **guacd**. El archivo incluye las claves RSA, ECDSA y Ed25519 que cada host tiene configuradas; además incluye los certificados Ed25519 presentes en Fenix, Kingu, Hercules y Ocean. Las claves públicas se cotejaron con `/etc/ssh/ssh_host_*_key.pub` y los certificados con los archivos `ssh_host_ed25519_key-cert.pub` de cada host.
- Los cinco perfiles de infraestructura conceden `READ` y `ADMINISTER` solo a `Guacamole Admins`. No se guarda la contraseña AD en los perfiles.

## Política de acceso y preparación multitenant

- `Guacamole Users` sirve como requisito de inicio de sesión LDAP, no como autorización automática a los servidores de plataforma. En la revisión del 2026-10-30 se retiró de las cinco conexiones el permiso `READ` que tenía ese grupo. `jnovoas` conserva acceso porque pertenece a `Guacamole Admins`.
- Las conexiones Fenix, Kingu, Hercules, Ocean y Marte son perfiles administrativos de la plataforma; no deben concederse a clientes/tenants. Comparten la identidad SSH restringida de `jnovoas`, por lo que la clave no es una credencial apta para usuarios ni cargas de tenants.
- Antes de incorporar tenants: definir grupos AD separados por tenant y una política de autorización Guacamole que solo asocie cada grupo con sus propias conexiones/conexiones-grupo; revisar el filtro LDAP de grupos (`LDAP_GROUP_SEARCH_FILTER`, ahora limitado a `Guacamole Users` y `Guacamole Admins`) para descubrir los nuevos grupos; comprobar pertenencia efectiva, revocación y ausencia de permisos heredados/cruzados con cuentas de prueba de dos tenants.
- Cada tenant requiere cuentas o certificados SSH propios, con privilegios mínimos y destinos limitados por el servidor y la red. No reutilizar la clave SSH de administración de plataforma. Los ACL de Guacamole no sustituyen la autorización del host, la segmentación de red ni el aislamiento de datos del servicio destino.
- Mantener SFTP deshabilitado salvo necesidad aprobada. Evaluar desactivar copia/pegado por perfil según el modelo de datos y las tareas permitidas; Guacamole los habilita por defecto y permite configurar `disable-copy` y `disable-paste`. La política se definirá antes de ofrecer sesiones a tenants.
- La implementación actual autentica contra el dominio compartido y mantiene perfiles en PostgreSQL, pero aún no constituye un aislamiento multitenant completo: no se han aprovisionado tenants, identidades SSH por tenant ni pruebas negativas entre tenants.

## Incidencia y corrección

El primer acceso presentó `SSL_ERROR_BAD_CERT_DOMAIN`: Nginx estaba sirviendo el certificado de `impacta.pinguinoseguro.cl`, que no incluía el nombre de Guacamole. Se emitió un certificado Let's Encrypt individual para `guacamole.pinguinoseguro.cl` y se activó el virtual host TLS con proxy a Fenix. El certificado observado vence el 2027-01-28 y Certbot instaló la tarea de renovación.

El contenedor respondía dentro de Docker, pero Docker no materializaba la publicación del puerto al estar la interfaz principal conectada únicamente a redes `internal`. Se agregó `guacamole_edge` como red puente no interna para el servicio web y se recreó únicamente el contenedor Guacamole. PostgreSQL y su volumen persistente no se recrearon. Tras el cambio, `docker inspect` mostró el mapa `10.88.0.1:8082 -> 8080/tcp` y Fenix respondió HTTP 200.

La IP de proxy confiable de Tomcat incluye Kingu (`10.88.0.2`) y el gateway de la red puente de publicación (`172.26.0.1`), para procesar los encabezados reenviados cuando Docker usa su proxy de usuario.

Tras la primera publicación, la página de login cargaba pero el envío de credenciales devolvía HTTP 500. La causa fue firewalld: el bridge interno de Compose (`172.25.0.0/16`) no estaba asignado a una zona que permitiera el tráfico entre Guacamole, PostgreSQL y guacd. Se agregó la zona `guac-internal`, con destino `DROP`, forwarding entre miembros de la zona y el origen limitado a `172.25.0.0/16`; se aplicó en configuración permanente y runtime. Con eso se habilitó solo el tráfico interno requerido y el acceso del host a servicios de ese bridge continúa bloqueado.

Para las conexiones SSH, la zona Fenix `guac-edge` tiene origen `172.26.0.0/16` y `172.27.0.0/16`, con destino `DROP`. Sus políticas persistentes también tienen destino `DROP`: `guac-to-host` permite únicamente desde guacd (`172.27.0.2`) hacia `10.88.0.1:4222`; `guac-to-wgmesh` permite desde ese mismo origen TCP/4222 hacia `10.88.0.2`, `.4`, `.5` y `.6` por `wg0`, con masquerade para que los servidores remotos vean como origen WireGuard de Fenix (`10.88.0.1`). No se abrió SSH hacia las redes públicas.

La primera comprobación de conectividad se hizo desde el contenedor web y no representaba la ruta real de las sesiones. El SSH lo inicia guacd, que estaba conectado solo a `guacamole_internal` (`172.25.0.0/16`, sin gateway); por eso se desconectaba con `SSH handshake failed`. Una corrección inicial añadió guacd a `guacamole_edge`, pero produjo un segundo fallo: el alias DNS `guacd` quedó en dos redes y el contenedor web intentó usar la IP de salida, donde el firewall bloqueaba `4822`. La configuración final usa una red exclusiva `guacamole_ssh_egress` (`172.27.0.0/16`, gateway `172.27.0.1`) solo para guacd, y monta allí `ssh_known_hosts` como solo lectura. Guacamole llega a guacd por el alias único de `guacamole_internal`; guacd conserva esa red interna para su canal de control y usa la red exclusiva para el egress SSH limitado. Se recreó solo el contenedor web para limpiar su resolución DNS previa.

## Evidencia y límites de validación

- `nginx -t` pasó y Nginx recargó la configuración.
- La negociación TLS pública presentó `CN=guacamole.pinguinoseguro.cl`, emisor Let's Encrypt `YE1` y SAN `guacamole.pinguinoseguro.cl`.
- `curl --resolve guacamole.pinguinoseguro.cl:443:64.176.8.191` devolvió HTTP 200; el endpoint de Fenix `http://10.88.0.1:8082/` también devolvió HTTP 200.
- El arranque de Guacamole registró extensiones LDAP, PostgreSQL y protección contra intentos repetidos (`ban`) cargadas.
- El contenedor web se recreó una segunda vez para aplicar la lista de proxies confiables; `docker inspect` mostró el valor efectivo y Fenix volvió a responder HTTP 200.
- Después de aplicar la zona de firewall, los logs registraron autenticación exitosa de `jnovoas@pinguinoseguro.cl` por LDAP y `POST /api/tokens` con HTTP 200 desde su navegador. Se comprobó también conexión TCP desde Guacamole a PostgreSQL (`5432`), guacd (`4822`) y LDAPS (`636`). No se leyó ni guardó la contraseña humana.
- Jaime confirmó que pudo entrar con su usuario y que la página carga correctamente.
- Una solicitud controlada con una identidad inexistente recibió rechazo de credenciales; no volvió a producir HTTP 500. El GET de datos de sesión sin autenticación devuelve 403, como corresponde.
- La primera prueba de usuario mostró `SSH handshake failed` y desconexión inmediata; después, Guacamole reportó `Connection timed out` al crear el túnel a guacd. La separación de `guacamole_ssh_egress` resolvió el alias ambiguo: desde Guacamole, `guacd` resuelve solo a `172.25.0.3` y el TCP al puerto `4822` responde. Desde el namespace de guacd (`172.27.0.2`), pasaron SSH autenticado, validación estricta de host y asignación TTY a los cinco destinos por `4222`.
- Guacamole registró `Host key does not match known hosts entry` para los intentos SSH. La comparación inicial fijaba solo una representación de la identidad del host; Fenix volvió a conectar cuando `ssh_known_hosts` incluyó su clave pública Ed25519 exacta. Para evitar el mismo fallo al negociarse otro tipo, se cotejaron y fijaron todas las claves RSA/ECDSA/Ed25519 anunciadas por los cinco servidores y sus certificados Ed25519 configurados. El archivo está montado directamente en guacd y se lee al iniciar cada conexión.
- Validación posterior: desde el namespace de red real de guacd, SSH con `StrictHostKeyChecking=yes`, la clave dedicada de Guacamole y el archivo versionado completó autenticación y comando no destructivo en los cinco destinos. Guacd registró `SSH connection successful` para Fenix y Jaime confirmó que se conectó desde Guacamole. La conexión interactiva de Guacamole a los otros cuatro destinos aún no tiene evidencia de éxito posterior a la última actualización de sus pins.
- PostgreSQL contiene cinco perfiles SSH. Se comprobaron nombres, protocolos, destinos y permisos por consulta; no se imprimió ni versionó la clave privada.
- Revisión de seguridad multitenant: la consulta de permisos encontró inicialmente `READ` de `Guacamole Users` en los cinco perfiles de plataforma. Se retiraron exactamente esas cinco filas en PostgreSQL; la consulta posterior confirmó que solo `Guacamole Admins` retiene `READ` y `ADMINISTER` en Fenix, Kingu, Hercules, Ocean y Marte. Los cinco perfiles no tienen grupo padre; `Guacamole Users` no tiene permisos de sistema ni de grupos de conexiones. No se cambiaron conexiones, credenciales, firewall ni contenedores.
- Después de recrear Guacamole y provisionar los perfiles, la URL pública devolvió HTTP 200 con validación TLS correcta (`curl --resolve` al IP público, sin omitir la verificación del certificado). El intento de resolver el DNS desde la shell local no resolvió el nombre; la prueba directa con SNI/Host correcto confirmó endpoint y certificado.
- Queda pendiente verificar una sesión interactiva de Guacamole para Kingu, Hercules, Ocean y Marte tras la actualización de todos los pins. La prueba SSH estricta desde el namespace real de guacd sí pasó para los cinco destinos.
- En `nginx -t` aparece además una advertencia preexistente de valor duplicado `TLSv1.3` en el vhost de `pinguinoseguro`; la sintaxis valida y no impide servir Guacamole. No se modificó ese vhost.

## Operación y comprobación

- Compose: `infrastructure/guacamole/compose.yaml`.
- Configuración Nginx versionada: `infrastructure/guacamole/nginx/guacamole.pinguinoseguro.cl.conf`.
- Plan de ampliación RDP/VNC/Kubernetes/SFTP, grabación e integración multitenant: [`guacamole-servicios-remotos-plan-2026-10-30.md`](guacamole-servicios-remotos-plan-2026-10-30.md).
- Para ver estado en Fenix: `cd /home/jnovoas/proyectos/sentinel/infrastructure/guacamole && sudo -n docker compose --env-file /etc/guacamole/guacamole.env ps`.
- Para comprobar Nginx en Kingu: `sudo -n nginx -t && sudo -n systemctl reload nginx`.
- La renovación del certificado queda a cargo de Certbot en Kingu; verificarla con `sudo -n certbot renew --dry-run` en una ventana operativa.
- Mantener egress y acceso a redes Docker bajo revisión: `guacamole_edge` es no interna para que Docker publique el listener; PostgreSQL permanece en la red interna; guacd usa `guacamole_internal` y la red dedicada `guacamole_ssh_egress`; LDAPS usa su bridge dedicado.
- Firewall Fenix: `guac-internal` usa `172.27.0.0/16`, `forward=yes`, `target=DROP`; `guac-edge` usa `172.26.0.0/16` y `172.30.0.0/16`, `target=DROP`. Las políticas SSH limitan el origen a guacd `172.30.0.2` y mantienen únicamente los cinco destinos TCP/4222 descritos. `scripts/configure-guacamole-network.sh runtime` alinea las fuentes/reglas con las subredes efectivas; después del smoke, repetir con `permanent`. Nunca hace reload ni sustituye zonas por `trusted`.
- Clave dedicada: custodiar `/etc/guacamole/ssh/id_ed25519` en Fenix con permisos `0600`; no copiarla fuera del host ni añadirla al repositorio. Para rotarla, actualizar los perfiles y los cinco `authorized_keys`, verificar sesiones y retirar la clave anterior.

## Respaldo y trazabilidad

Se conservaron respaldos root-only previos a la intervención en Fenix y Kingu, bajo `/root/guac-deploy-20261030/backup/`. La zona DNS vive en la configuración operativa del servidor DNS autoritativo y no forma parte de este repositorio. El cambio de código se documenta aquí; la nota persistente de Guacamole en la vault complementa la evidencia operativa sin incluir secretos en Git.

## Recuperación tras reasignación de redes — 30/31 de octubre

El operador reportó JavaScript de Next/Turbopack al abrir Guacamole. En la URL
canónica no se observó esa respuesta: Kingu y el upstream Fenix entregaron HTML
de Guacamole. Sin embargo, una comprobación real en Chromium encontró fallo en
el bootstrap de autenticación: PostgreSQL no era alcanzable y la aplicación
mostraba su pantalla de error. El HTTP200 del HTML no era prueba de funcionamiento.

La recreación anterior de redes había dejado `sentinel_sentinel_internal` en
`172.25/16`, `guacamole_internal` en `172.27/16` y el egress SSH en `172.30/16`.
El firewall conservaba la asignación antigua: clasificaba `172.27/16` como
`guac-edge`, con forward bloqueado. Se alineó la política con las redes actuales,
sin mover Sentinel ni reiniciar Docker:

- Compose fija ahora explícitamente `guacamole_internal=172.27.0.0/16`;
  conserva la red SSH ya efectiva `172.30/16` y guacd `172.30.0.2`.
- Script versionado `scripts/configure-guacamole-network.sh`: migra
  `172.27/16` a `guac-internal`, añade `172.30/16` a `guac-edge`, retira la
  asignación obsoleta `172.25/16` y actualiza solo el origen de las reglas
  TCP/4222 existentes. Aplicado runtime y permanent, sin reload Firewalld.
- La clave dedicada de Fenix conserva `restrict,pty` y limita su origen a
  `172.30.0.2`, no a la IP antigua. Respaldo de `authorized_keys` conservado;
  no se cambió material de clave ni contraseña humana.
- Validación Compose correcta; no fue necesario recrear ningún contenedor.
- Chromium cargó la URL canónica con resolución aislada a `64.176.8.191`,
  conservando hostname/SNI y validación TLS. Formulario visible de Apache
  Guacamole1.6.0, campos Username/Password; `/api/patches` y `/api/languages`
  HTTP200; solicitud inicial vacía, con Content-Type de formulario, a
  `/api/tokens` HTTP403 esperado. Sin fallos de transporte en esa carga.
- Desde el namespace real de guacd, SSH estricto usando la clave existente
  y `ssh_known_hosts` completó `/usr/bin/true` con salida0 en Fenix, Kingu,
  Hercules, Ocean y Marte. No se copiaron secretos.

No se verificó login humano válido ni una sesión gráfica de Guacamole. La
respuesta Next/Turbopack pegada por el operador no se atribuye a este fallo de
PostgreSQL sin la URL exacta que la produjo. El resolver local del entorno de
auditoría continúa sin resolver el dominio; el DNS público consultado sí devuelve
Kingu. No se cambió DNS global ni se omitió validación TLS.
