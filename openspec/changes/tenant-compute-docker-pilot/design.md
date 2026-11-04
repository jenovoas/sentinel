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

- **Límite de disco mediante imagen ext4 de capacidad fija por tenant.** El candidato es un archivo completamente preasignado, formateado como ext4 y montado en el host como loop; Docker recibe solo la ruta montada. El tamaño del archivo es el techo físico del sistema de archivos. Se elige frente a `overlay2.size` porque el host no tiene XFS/`pquota`, y frente a cuotas del ext4 raíz porque estas no están habilitadas. La operación queda condicionada a probar persistencia tras reinicio, capacidad exacta, denegación de escrituras excedentes y destrucción segura; no se considera verificada todavía.
- **Capa escribible del contenedor cerrada.** El módulo configura rootfs de solo lectura; datos persistentes van al volumen limitado, `/tmp` a `tmpfs` acotado y logs `json-file` con rotación. La garantía completa sigue condicionada a que el runner autorice solo imágenes aprobadas sin volúmenes anónimos no controlados y pruebe las rutas escribibles de cada imagen.
- **Runner separado junto al daemon Docker de Kingu.** La comprobación del filesystem y la ruta bind deben ocurrir en el mismo host que consume el bind mount. No se aceptará un daemon Docker remoto con preflight ejecutado en otra máquina ni se expondrá el socket Docker por TCP. El acceso rootful a Docker equivale a privilegio de host; el servicio web no recibirá ese acceso.
- **Runner autenticado y catálogo cerrado.** El runner autenticará al portal por canal privado, validará tenant/solicitud y una lista fija de imágenes/operaciones, y nunca aceptará rutas, comandos, módulos o argumentos Terraform arbitrarios. La lista de cargas permanece vacía hasta que el dueño elija una plantilla; digest, `VOLUME` declarados y rutas escribibles deberán quedar revisados antes de habilitarla.
- **Los booleanos del módulo no son evidencia.** Los inputs `*_verified` son autodeclarados y no demuestran identidad, ACL, capacidad ni lock. Se mantienen en `false` como bloqueo del módulo mientras no exista runner; no se considerarán controles suficientes ni se quitarán antes de sustituirlos por comprobaciones efectivas dentro del executor.
- **Terraform requiere backend remoto con bloqueo.** El runner no usará estado local ni ejecutará `apply` si no hay backend remoto configurado y una operación de bloqueo funcional. Este cambio no inventa ni provisiona un servicio de estado que no se ha verificado en el entorno.
- **Sin ampliación de infraestructura para el piloto.** Kingu se usa temporalmente con su capacidad actual. La ampliación vertical o un segundo host se evalúa con clientes reales y mediciones de consumo.

## Risks / Trade-offs

- [Imagen loop ext4 no vuelve a montarse tras reinicio] → instalar y probar una unidad `.mount` persistente, y hacer que el runner exija montaje activo y tamaño correcto antes de iniciar Docker.
- [La preasignación puede agotar el disco del host] → reservar capacidad antes de crear la imagen, conservar un margen operativo y rechazar la solicitud si el espacio disponible no cubre el archivo completo más la reserva.
- [Rootfs de solo lectura puede impedir iniciar el escritorio] → inventariar rutas escribibles de la imagen y asignarlas explícitamente al volumen o a `tmpfs`; no relajar a rootfs escribible sin demostrar una cuota para esa capa.
- [El acceso al socket Docker equivale a privilegio de host] → runner no expuesto públicamente, autenticación fuerte, API cerrada, logs saneados y permisos del proceso minimizados; no montar el socket en un contenedor de cliente.
- [Backend remoto no definido] → inventariar los backends existentes; si ninguno sirve, detener la configuración hasta acordar proveedor y política. Bloquear cualquier operación si no se demuestra persistencia y lock; nunca usar estado local como alternativa silenciosa.
- [Identidad piloto y ACL Guacamole pendientes] → no crear cuentas ni asignar permisos; mantener la solicitud en estado bloqueado.

## Migration Plan

1. Crear y validar el módulo y el runner localmente, con planes sin recursos y pruebas negativas para cuota, identidad y autorización.
2. Verificar el backend remoto y el mecanismo de almacenamiento en un entorno aislado antes de tocar Kingu.
3. Ejecutar preflight de solo lectura en Kingu y confirmar cuota, capacidad, ACL, red e identidad autorizada.
4. Aplicar un solo tenant tras resolver los gates y medir recursos con el host actual.
5. En rollback, revocar el acceso, destruir solo la operación piloto y comprobar que el volumen loop, la red y el contenedor se eliminaron; conservar evidencia y backups acordados.

## Operational Gates

El código puede implementarse sin asumir estos valores, pero cualquier ejecución remota queda bloqueada hasta que se configuren y verifiquen: backend remoto con lock, digest y rutas escribibles de la imagen aprobada, identidad piloto y principal estable de Guacamole. La identidad piloto aún no existe; no se crearán cuentas ni permisos automáticamente.