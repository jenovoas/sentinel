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

## Incidencia y corrección

El primer acceso presentó `SSL_ERROR_BAD_CERT_DOMAIN`: Nginx estaba sirviendo el certificado de `impacta.pinguinoseguro.cl`, que no incluía el nombre de Guacamole. Se emitió un certificado Let's Encrypt individual para `guacamole.pinguinoseguro.cl` y se activó el virtual host TLS con proxy a Fenix. El certificado observado vence el 2027-01-28 y Certbot instaló la tarea de renovación.

El contenedor respondía dentro de Docker, pero Docker no materializaba la publicación del puerto al estar la interfaz principal conectada únicamente a redes `internal`. Se agregó `guacamole_edge` como red puente no interna para el servicio web y se recreó únicamente el contenedor Guacamole. PostgreSQL y su volumen persistente no se recrearon. Tras el cambio, `docker inspect` mostró el mapa `10.88.0.1:8082 -> 8080/tcp` y Fenix respondió HTTP 200.

La IP de proxy confiable de Tomcat incluye Kingu (`10.88.0.2`) y el gateway de la red puente de publicación (`172.26.0.1`), para procesar los encabezados reenviados cuando Docker usa su proxy de usuario.

## Evidencia y límites de validación

- `nginx -t` pasó y Nginx recargó la configuración.
- La negociación TLS pública presentó `CN=guacamole.pinguinoseguro.cl`, emisor Let's Encrypt `YE1` y SAN `guacamole.pinguinoseguro.cl`.
- `curl --resolve guacamole.pinguinoseguro.cl:443:64.176.8.191` devolvió HTTP 200; el endpoint de Fenix `http://10.88.0.1:8082/` también devolvió HTTP 200.
- El arranque de Guacamole registró extensiones LDAP, PostgreSQL y protección contra intentos repetidos (`ban`) cargadas.
- El contenedor web se recreó una segunda vez para aplicar la lista de proxies confiables; `docker inspect` mostró el valor efectivo y Fenix volvió a responder HTTP 200.
- No se guardó una contraseña AD humana ni se hizo login válido durante esta comprobación. La contraseña la debe introducir el usuario en el navegador; por eso la autenticación interactiva correcta queda pendiente de validación por Jaime.
- No se crearon perfiles RDP/SSH: no se especificaron los destinos ni sus políticas de acceso.
- En `nginx -t` aparece además una advertencia preexistente de valor duplicado `TLSv1.3` en el vhost de `pinguinoseguro`; la sintaxis valida y no impide servir Guacamole. No se modificó ese vhost.

## Operación y comprobación

- Compose: `infrastructure/guacamole/compose.yaml`.
- Configuración Nginx versionada: `infrastructure/guacamole/nginx/guacamole.pinguinoseguro.cl.conf`.
- Para ver estado en Fenix: `cd /home/jnovoas/proyectos/sentinel/infrastructure/guacamole && sudo docker compose --env-file /etc/guacamole/guacamole.env ps`.
- Para comprobar Nginx en Kingu: `sudo nginx -t && sudo systemctl reload nginx`.
- La renovación del certificado queda a cargo de Certbot en Kingu; verificarla con `sudo certbot renew --dry-run` en una ventana operativa.
- Mantener egress y acceso a redes Docker bajo revisión: `guacamole_edge` es no interna para que Docker publique el listener, mientras que PostgreSQL/guacd permanecen en la red interna y LDAPS usa su bridge dedicado.

## Respaldo y trazabilidad

Se conservaron respaldos root-only previos a la intervención en Fenix y Kingu, bajo `/root/guac-deploy-20261030/backup/`. La zona DNS vive en la configuración operativa del servidor DNS autoritativo y no forma parte de este repositorio. El cambio de código se documenta aquí; la nota persistente de Guacamole en la vault complementa la evidencia operativa sin incluir secretos en Git.
