# Plan para ampliar Guacamole con servicios remotos seguros y multitenant

**Fecha:** 2026-10-30  
**Estado:** planificado; no se instalaron servicios ni se cambiaron redes en esta tarea.  
**Objetivo:** preparar una sesión futura para decidir y habilitar, con evidencia, escritorios RDP/VNC, terminales Kubernetes cuando exista un clúster, transferencia SFTP y auditoría de sesiones.

## 1. Contexto verificado que debe conservar la siguiente sesión

- La instancia actual es Apache Guacamole/guacd `1.6.0` en contenedores en Fenix; PostgreSQL `16` guarda configuración y permisos. Kingu termina TLS/Nginx y publica `https://guacamole.pinguinoseguro.cl` hacia Fenix por WireGuard.
- Guacamole autentica por LDAPS contra Samba AD. `Guacamole Users` permite iniciar sesión; `Guacamole Admins` administra las conexiones actuales. Se retiró `READ` del grupo general en los cinco perfiles de plataforma. Fenix, Kingu, Hercules, Ocean y Marte siguen siendo conexiones SSH administrativas exclusivas para `Guacamole Admins`. Soma queda fuera.
- Las cinco conexiones usan SSH en puerto `4222`, la identidad dedicada y limitada de `jnovoas`, pins verificados en `infrastructure/guacamole/ssh_known_hosts`, y el egress fijo de guacd `172.30.0.2`. La clave actual no sirve para tenants.
- Redes actuales relevantes en Fenix: web Guacamole en `guacamole_edge`; PostgreSQL, web y guacd se comunican por `guacamole_internal`; el SSH sale por `guacamole_ssh_egress`. Firewalld limita el egress actual a TCP/4222 y destinos concretos. No ampliar esta política a subredes o puertos generales.
- Topología a revalidar en el preflight: Fenix es nodo de desarrollo/compilación y PDC; Kingu aloja producción contenerizada, Traefik, BDC y el proxy TLS público; Hercules y Ocean cumplen DNS público en DMZ; Marte aloja seguridad/monitorización y parte del backend. No mover AD a la DMZ ni instalar escritorio remoto en DC, DNS público o Marte por defecto.
- La Fase 0 ya define `SP-Guacamole-Remote`, `SP-VM-Server`, `SP-VM-Desktop`, tenant como `OU=<RUT>,OU=Tenants`, y cómputo tenant en contenedores Podman rootless porque Fenix/Kingu no exponen KVM. El módulo Terraform plantea alta/revocación Guacamole, escritorio xRDP/noVNC, red dedicada por tenant y métricas a Marte.
- La última evidencia del despliegue confirma Guacamole SSH interactivo a Fenix; las cinco rutas SSH estrictas pasaron desde la red de guacd. La UI de los otros cuatro perfiles debe validarse cuando se usen.

## 2. Decisiones de seguridad para la ampliación

1. **No instalar protocolos por disponibilidad.** En la sesión futura primero se inventarían destinos, demanda, sistema operativo y puertos existentes. No asumir que hay Windows, un escritorio Linux o un clúster Kubernetes.
2. **Primer candidato: escritorio aislado de tenant con xRDP y conexión Guacamole RDP**, ligado a T4 de Terraform. Validar arranque rootless, ciclo de sesión, audio/portapapeles según necesidad y autenticación PAM/AD. Si xRDP no cumple, comparar VNC. noVNC es otra aplicación/canal de acceso, no una conexión Guacamole; no publicar ambos canales a la vez por defecto.
3. **No habilitar RDP/VNC en controladores de dominio, DNS de DMZ ni hosts de monitoreo** como solución rápida. Para operación gráfica de plataforma, inventariar primero un destino de administración dedicado y aislado.
4. **Kubernetes solo si el inventario demuestra que existe un clúster operativo.** No instalar un clúster para habilitar la conexión Guacamole. Usar identidad/certificado de servicio por tenant, CA verificada y RBAC limitado a su namespace y a los pods autorizados; nunca kubeconfig `cluster-admin` compartido.
5. **Telnet queda excluido.** Aunque guacd documenta el protocolo, el tráfico entre guacd y el destino no está cifrado.
6. **SFTP opt-in y perfil separado.** Mantener desactivado en conexiones generales. Si se aprueba, usar usuario/clave SSH propio del servicio o tenant, `sftp-root-directory` mínimo y controles explícitos de carga y descarga. No ofrecer acceso al `/` del host.
7. **Grabación desactivada hasta aprobar una política.** Antes de activarla, definir finalidad, formatos, ubicación, cifrado de almacenamiento, ACL de reproducción, retención/borrado, responsable y acceso de auditoría. No registrar teclas salvo requisito formal; un typescript puede contener órdenes y datos sensibles.
8. **Portapapeles y archivos por defecto restringidos en conexiones tenant.** Desactivar copia/pegado salvo necesidad operativa justificada; evaluar por separado cada dirección de transferencia. Mantener SFTP y redirección de unidades apagados si no forman parte del servicio contratado.
9. **Autenticación central no implica credenciales de destino centralizadas.** El login web va contra AD. Cada destino RDP/VNC/Kubernetes debe tener su propio mecanismo de autenticación y autorización, sin secretos de operador compartidos. Evaluar MFA mediante el IdP o TOTP de Guacamole antes de abrir acceso a clientes externos.
10. **Sin puertos públicos nuevos.** Guacd obtiene solo egress mínimo desde `172.27.0.2` al destino/puerto elegido. Las conexiones entrantes de RDP/VNC/SSH se limitan a la red privada/tenant; Guacamole/guacd no deben conectarse a todos los bridges de clientes.

## 3. Decisión pendiente en la integración AD–Guacamole–Terraform

El spec de `terraform-tenant-compute.md` propone asignar conexiones al `objectGUID` del usuario. La instalación actual combina autenticación LDAP con permisos de PostgreSQL: Guacamole asocia entidades por nombre de usuario/grupo (en esta configuración, UPN/`cn`), no se ha demostrado un ACL nativo por `objectGUID`.

Antes de implementar aprovisionamiento automático, elegir y probar una identidad estable que sí se mapee en Guacamole:

- **Opción preferida para aislamiento tenant:** grupo AD por tenant para autorización de conexiones, con una conexión-grupo propia y `READ` solo para ese grupo; mantener `SP-Guacamole-Remote` como entitlement grueso del servicio.
- **Opción por usuario:** asignar ACL al UPN canónico del usuario, con un mapeo explícito y pruebas de renombre/baja.
- Si producto exige `objectGUID`, construir y probar la traducción GUID → UPN/grupo en el aprovisionador; no insertar el GUID en `guacamole_entity` suponiendo que Guacamole lo resolverá.

La búsqueda LDAP actual limita el inicio de sesión a miembros de `Guacamole Users` y el filtro de grupos reconoce únicamente `Guacamole Users` y `Guacamole Admins`. La futura sesión debe diseñar cómo descubrir los grupos `SP-*` y grupos tenant, conservar la puerta de inicio de sesión y evitar que pertenecer al grupo general otorgue `READ` a conexiones de plataforma. Verificar también grupos anidados, capitalización, revocación de permisos y usuarios con varias membresías.

## 4. Matriz de servicios y elegibilidad

| Capacidad | Cuándo habilitar | Modelo seguro para Sentinel | Estado actual |
|---|---|---|---|
| SSH | Administración de servidores Linux | Solo Admins para hosts de plataforma; por tenant, identidad propia, host pin, usuario no compartido, ACL/egress mínimos | Configurado; interfaz Guac confirmada para Fenix |
| RDP | Destino Windows o escritorio xRDP que lo requiera | TLS/NLA cuando aplique, identidad AD del tenant sin contraseña compartida guardada, destino privado, permisos por tenant | Sin destinos ni servicio nuevos confirmados |
| VNC | Aplicación/desktop que lo requiera y no pueda usar RDP | Destino privado; autenticación única por instancia/tenant; verificar limitaciones de AD antes de ofrecerlo | Sin destinos confirmados |
| Kubernetes | Existe clúster con necesidad de consola de pod | Cuenta de servicio o certificado por tenant, CA válida, namespace y RBAC mínimo | No se confirmó clúster; no instalar uno para Guac |
| SFTP | Entrega/recepción de archivos aprobada | Conexión separada, raíz confinada, cuenta por tenant, subida/bajada según necesidad | No habilitado como servicio general |
| Grabación | Auditoría con política de retención aprobada | Ruta dedicada protegida, lectura restringida, retención y borrado medibles | No configurada |
| Telnet | Ninguna para el entorno actual | Excluido por tráfico sin cifrar | No habilitar |

## 5. Trabajo para la próxima sesión

### G0. Preflight de solo lectura

- Leer este plan, `guacamole-ad-deployment-2026-10-30.md`, procedimiento estándar, `fase0-tareas.md`, `ad-servicios-y-gpos.md` y `terraform-tenant-compute.md`.
- Revisar estado git y rama `main`; comprobar los cinco perfiles actuales, permisos efectivos, `LDAP_USER_SEARCH_FILTER`, `LDAP_GROUP_SEARCH_FILTER`, extensiones cargadas, versión de guacd y sus redes/firewall.
- En cada host candidato, levantar OS/rol, paquetes/servicios/listeners activos, escritorio existente, AD/PAM, clúster/namespaces si los hubiera, y tráfico de red requerido. Consultas remotas siempre con `sudo -n`; nunca incluir contraseñas o tokens en argumentos.
- Clasificar cada hallazgo como existente, requerido, descartado o pendiente de decisión. No instalar ni abrir puertos durante G0.

### G1. Cerrar autorización antes de abrir destinos

- Alinear los grupos de Fase 0 y el mapeo estable AD→Guacamole (sección 3).
- Diseñar connection-groups por tenant, sin heredar permiso general sobre los cinco perfiles de plataforma.
- Definir aprovisionamiento idempotente API/Terraform y revocación al quitar entitlement, usuario o tenant; eliminar conexiones huérfanas.
- Verificar login AD existente, extensiones y estrategia MFA. No almacenar contraseña personal en perfiles.

### G2. Elegir un único piloto gráfico

- Si T4 sigue vigente, pilotear un contenedor `desktop` rootless de un solo tenant en red Podman dedicada.
- Evaluar primero xRDP/RDP dentro de ese contenedor; confirmar compatibilidad del sistema base, PAM/AD, NLA/TLS, recursos/cupos y alcance de firewall.
- Considerar VNC solo si el piloto demuestra una necesidad que xRDP no cubre. Mantener noVNC fuera del camino Guacamole hasta una decisión explícita de producto.
- No configurar sesiones de escritorio en Fenix/Kingu DC ni en Hercules/Ocean DNS DMZ.

### G3. Añadir transferencia/auditoría como decisiones separadas

- Si se aprueba SFTP, crear un perfil específico, verificar el host key SSH, confinar raíz y probar que cada dirección de transferencia cumple la política.
- Si se aprueba grabación, hacer una sesión sintética sin secretos y comprobar reproducción, permisos, tamaño, retención y borrado.
- Aplicar controles de clipboard por perfil; verificar que la configuración efectiva coincide con la política.

### G4. Kubernetes condicional

- Ejecutar solo si G0 encuentra clúster real y servicio operativo. Validar conectividad desde guacd, TLS/CA y RBAC negativo entre namespaces.
- Si no existe clúster o no hay caso de uso, registrar “no aplica” y cerrar esta rama sin instalar Kubernetes.

### G5. Rollout gradual, validación y rollback

- Hacer un único tenant/piloto; no propagar a todos los nodos por bucle ni modificar a la vez Nginx, Guac, AD y firewalld.
- Aplicar cambios de configuración con plantilla versionada, respaldo verificado, validación previa y ejecución de los smoke tests del procedimiento estándar.
- Verificar: acceso permitido al recurso propio; denegado a infraestructura y otro tenant; aislamiento de red; autenticación con AD; identidad del host/API validada; transferencia/clipboard/recording como se definieron; revocación inmediata; logs sin secretos.
- Rollback: quitar permisos/connection-group piloto, deshabilitar perfil, detener servicio nuevo, revertir solo las reglas egress añadidas y restaurar backup verificado. Mantener Guacamole SSH y el login AD existente.

## 6. Criterios de salida de la futura sesión

- Cada protocolo queda etiquetado **habilitado**, **no aplica** o **pendiente con evidencia**, con destino y responsable nombrados.
- Cero nuevos puertos públicos; egress de guacd limitado a destinos/puertos requeridos; los cinco perfiles administrativos permanecen restringidos a `Guacamole Admins`.
- Ningún tenant ve ni alcanza recursos de otro tenant; las pruebas negativas se realizan con dos identidades tenant distintas.
- La identidad de provisión Guacamole, cuotas Terraform, redes, credenciales y revocación están documentadas junto al flujo del portal.
- Estado final real, comandos de verificación sin secretos, cambios, rollback y evidencia quedan en Sentinel y en la vault.

## 7. Referencias

- Implementación y estado operativo actual: [`guacamole-ad-deployment-2026-10-30.md`](guacamole-ad-deployment-2026-10-30.md).
- Flujo de trabajo: [`procedimiento-despliegue-estandar.md`](procedimiento-despliegue-estandar.md).
- Tareas Fase 0: [`fase0-tareas.md`](fase0-tareas.md), especialmente T1, T3 y T4.
- Grupos/AD: [`ad-servicios-y-gpos.md`](ad-servicios-y-gpos.md).
- Cómputo: [`terraform-tenant-compute.md`](terraform-tenant-compute.md).
- [Apache Guacamole 1.6.0 — protocolos Docker](https://guacamole.apache.org/doc/gug/guacamole-docker.html).
- [Apache Guacamole 1.6.0 — configuración, SSH/SFTP, recording, RDP, VNC, Kubernetes y clipboard](https://guacamole.apache.org/doc/gug/configuring-guacamole.html).
- [Apache Guacamole 1.6.0 — autenticación LDAP y asociación con PostgreSQL](https://guacamole.apache.org/doc/gug/ldap-auth.html).
- [Apache Guacamole 1.6.0 — MFA](https://guacamole.apache.org/doc/gug/mfa.html).
