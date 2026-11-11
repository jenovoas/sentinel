# Design

## Context

El contrato T4 plantea red, contenedor, almacenamiento persistente, métricas y Guacamole. El estado registrado para Kingu indica Docker rootful sobre `overlayfs`/ext4, sin cuotas activas ni XFS/`pquota`; ese dato no se volvió a medir en esta fase. El módulo Docker, el preflight ext4 loop y el aprovisionador idempotente con unidad systemd existen localmente, pero no se han validado con Terraform ni probado en Kingu. Las ocho pruebas del preflight usan fixtures y las dieciséis del aprovisionador incluyen quince con comandos simulados y una validación de unidad con `systemd-analyze`; en total, 24/24 pasan. Ninguna demuestra montaje, límite físico o persistencia reales. Una prueba aislada real de archivo ext4 confirmó `fallocate`, `mkfs.ext4 -E nodiscard`, reasignación completa y detección `blkid`; no se montó. El aprovisionador exige rutas canónicas y raíces propiedad del usuario efectivo, no escribibles por grupo/otros; además verifica propietario/permisos de imágenes existentes, seguridad y contenido exacto de las unidades, y asignación física completa después del formato. La guía heredada de Podman no representa el runtime seleccionado. El piloto apunta temporalmente a Kingu; no se ejecutará `apply` durante esta implementación sin aprobación operativa separada.

## Goals / Non-Goals

**Goals:**
- Separar el ejecutor de Terraform del proceso Next.js y restringirlo a operaciones del catálogo aprobadas.
- Hacer que el almacenamiento mutable de cada tenant tenga un límite físico verificable antes del `apply`.
- Mantener imágenes, recursos y redes aislados; aplicar límites cgroup de CPU y memoria.
- Rechazar el despliegue si falta estado remoto con lock o falla una comprobación local del host.

**Non-Goals:**
- Cambiar filesystem raíz, activar cuotas en `/dev/vda2`, instalar paquetes o modificar Kingu durante esta fase local.
- Publicar servicios tenant en puertos públicos.
- Integrar automáticamente Guacamole, DNS, métricas o inventario sin interfaces verificadas.
- Aumentar recursos de Kingu o crear otro host antes de que existan clientes reales.

## Decisions

- **Límite de disco mediante imagen ext4 de capacidad fija por tenant.** El archivo de 32 MiB creado por el aprovisionador y montado como loop expuso 26 464 256 B; la escritura hasta `ENOSPC` confirmó el límite y un marcador sobrevivió desmontaje/remontaje, con preflight real válido antes y después. Esto verifica capacidad física y remonte local, no recuperación de unidad tras reinicio de VM ni destrucción segura; Docker solo recibe la ruta montada.
- **Destrucción sin pérdida de datos compartidos.** El aprovisionador actual identifica el almacenamiento por tenant, no por solicitud; destruir una operación elimina solo su contenedor y red. El volumen ext4 persiste hasta una operación tenant-level separada con autorización explícita y verificación de cero referencias activas.
- **Purge tenant-level solo por operador local.** No se expone por HTTP: un subcomando local requiere root, tenant_id validado, confirmación explícita, PostgreSQL disponible sin operaciones activas ni contenedores que monten la ruta, y verificación exacta de unidad, loop e imagen. Toda comprobación fallida conserva los datos.
- **Capa escribible del contenedor cerrada.** El módulo configura rootfs de solo lectura; datos persistentes van al volumen limitado, `/tmp` a `tmpfs` acotado y logs `json-file` con rotación. La garantía completa sigue condicionada a que el runner autorice solo imágenes aprobadas sin volúmenes anónimos no controlados y pruebe las rutas escribibles de cada imagen.
- **Runner separado junto al daemon Docker de Kingu.** La comprobación del filesystem y la ruta bind deben ocurrir en el mismo host que consume el bind mount. No se aceptará un daemon Docker remoto con preflight ejecutado en otra máquina ni se expondrá el socket Docker por TCP. El acceso rootful a Docker equivale a privilegio de host; el servicio web no recibirá ese acceso.
- **Runner autenticado y catálogo cerrado.** El runner autenticará al portal por canal privado, validará tenant/solicitud y una lista fija de imágenes/operaciones, y nunca aceptará rutas, comandos, módulos o argumentos Terraform arbitrarios. La lista de cargas permanece vacía hasta que el dueño elija una plantilla; digest, `VOLUME` declarados y rutas escribibles deberán quedar revisados antes de habilitarla.
- **Los booleanos del módulo no son evidencia.** Los inputs `*_verified` son autodeclarados y no demuestran identidad, ACL, capacidad ni lock. Se mantienen en `false` como bloqueo del módulo mientras no exista runner; no se considerarán controles suficientes ni se quitarán antes de sustituirlos por comprobaciones efectivas dentro del executor.
- **Backend remoto HTTP con estado PostgreSQL y lock durable.** El runner implementará los endpoints HTTP del backend Terraform y persistirá estado y leases de lock en PostgreSQL mediante su DSN operativo; Terraform nunca tendrá fallback local. El backend exige credenciales por entorno, transacciones para exclusión mutua y disponibilidad del PostgreSQL configurado. No se añade una base local/Compose ni se inventa configuración de producción; una DSN ausente o un lock fallido bloquea la operación.
- **Preflight de almacenamiento en runtime 100% Rust.** El runner crea/verifica el ext4 loop y entrega al módulo evidencia tipada (verificado, bytes de filesystem y margen libre); Terraform no invoca `external` ni scripts Python. Los scripts Python existentes quedan como herramientas locales/offline y pruebas.
- **Sin ampliación de infraestructura para el piloto.** Kingu se usa temporalmente con su capacidad actual. La ampliación vertical o un segundo host se evalúa con clientes reales y mediciones de consumo.

## Risks / Trade-offs

- [Imagen loop ext4 no vuelve a montarse tras reinicio] → instalar y probar una unidad `.mount` persistente, y hacer que el runner exija montaje activo y tamaño correcto antes de iniciar Docker.
- [La preasignación puede agotar el disco del host] → reservar capacidad antes de crear la imagen, conservar un margen operativo y rechazar la solicitud si el espacio disponible no cubre el archivo completo más la reserva.
- [Rootfs de solo lectura puede impedir iniciar el escritorio] → inventariar rutas escribibles de la imagen y asignarlas explícitamente al volumen o a `tmpfs`; no relajar a rootfs escribible sin demostrar una cuota para esa capa.
- [El acceso al socket Docker equivale a privilegio de host] → runner no expuesto públicamente, autenticación fuerte, API cerrada, logs saneados y permisos del proceso minimizados; no montar el socket en un contenedor de cliente.
- [Backend PostgreSQL no disponible o local sin persistencia externa] → exigir DSN operativa configurada, proteger credenciales por entorno, probar persistencia y lock/unlock entre procesos; fallar cerrado ante pérdida del backend y nunca escribir estado Terraform local.
- [Identidad piloto y ACL Guacamole pendientes] → no crear cuentas ni asignar permisos; mantener la solicitud en estado bloqueado.

## Migration Plan

1. Crear y validar el módulo y el runner localmente, con planes sin recursos y pruebas negativas para cuota, identidad y autorización.
2. Verificar el backend remoto y el mecanismo de almacenamiento en un entorno aislado antes de tocar Kingu.
3. Ejecutar preflight de solo lectura en Kingu y confirmar cuota, capacidad, ACL, red e identidad autorizada.
4. Aplicar un solo tenant tras resolver los gates y medir recursos con el host actual.
5. En rollback, revocar el acceso y destruir solo la operación piloto; comprobar que se eliminaron su contenedor y red y que el volumen ext4 permanece. Un purge tenant-level requiere autorización explícita y cero referencias activas; conservar evidencia y backups acordados.

## Operational Gates

## Plantilla aprobada: n8n-automation (2026-11-11)

- **Imagen:** `docker.io/n8nio/n8n@sha256:3a5dd07de8be0afcb4b23eeb6e2e7a724cda912e082aa286fdf7792ec3a9a4a8` (tag 1.55.0, digest verificado por `docker inspect` local). Sin `VOLUME` declarados; usuario `node` (no root); expone solo `5678/tcp`.
- **Ruta escribible:** `/home/node/.n8n` → volumen ext4 del tenant montado en `/workspace` (misma ruta que usa el módulo para todos los tenants). Sin bind-mounts del host, sin `network_mode: host`.
- **Red:** interna dedicada por operación + red edge externa parametrizada (`edge_network_name`, p. ej. `traefik_public` en Kingu). Vacío = solo interna.
- **Descartadas:** `wordpress-pro` (decisión explícita del dueño: superficie histórica de CVEs), `wazuh-siem` (`network_mode: host` + monta `/var/log`, `/etc` del host: viola aislamiento). `guacamole-rdp` queda como segunda candidata (AD verificado) tras demostrar el ciclo con n8n.
- **Variables del operador para habilitarla (fuera de git):** `DEPLOYMENT_EXECUTION_ENABLED=true`, `DEPLOYMENT_APPROVED_TEMPLATE=docker-pilot`, `DEPLOYMENT_IMAGE_METADATA_REVIEWED=true`, `DEPLOYMENT_IMAGE_DIGEST=<digest de arriba>`, `DEPLOYMENT_IMAGE_VOLUME_PATHS='["/workspace"]'`, `DEPLOYMENT_IMAGE_WRITABLE_PATHS='["/workspace"]'`, `DEPLOYMENT_EDGE_NETWORK=traefik_public` (o vacío), más límites `DEPLOYMENT_DISK_LIMIT_BYTES`, `DEPLOYMENT_MIN_HOST_FREE_BYTES`, `DEPLOYMENT_CPU_LIMIT`, `DEPLOYMENT_MEMORY_LIMIT_MB`, `DEPLOYMENT_TMPFS_LIMIT_MB` y gates `DEPLOYMENT_PILOT_IDENTITY_AUTHORIZED`, `DEPLOYMENT_GUACAMOLE_ACL_VERIFIED`, `DEPLOYMENT_CAPACITY_APPROVED`.
- **Tenant piloto:** laespiguita (ya existe como tenant real). El `apply` requiere orden explícita del dueño; este documento no la sustituye.