# T4 tenant-compute con Docker

## Estado y alcance

Al 2026-11-04 T4 está en preparación local, no desplegado. Existen un módulo Terraform Docker, un preflight de almacenamiento ext4 loop y un aprovisionador conservador con modo de planificación por defecto. Hay 24 pruebas unitarias; 23 usan fixtures/comandos simulados y una valida la unidad generada con `systemd-analyze verify`. Terraform/OpenTofu no están instalados en el entorno de desarrollo, por lo que no se han ejecutado `fmt`, `validate` ni planes. No se ha probado el almacenamiento en Kingu ni existe runner. El checkout no declara backend Terraform; la existencia de un servicio remoto compatible fuera del repositorio no se ha inventariado. No se ha ejecutado `apply`.

El destino temporal propuesto es Kingu, con el daemon Docker existente y su capacidad actual. La tenant elegida para el piloto es `laespiguita`; todavía no hay identidad de usuario piloto autorizada. No crear usuarios, membresías ni permisos. La plantilla inicial está aplazada: no elegir WordPress, escritorio ni otra carga por inferencia.

## Diseño previsto

- Terraform con el proveedor Docker, invocado únicamente por un runner separado del portal y del Cortex.
- El runner debe ejecutarse en el mismo host que el daemon Docker para que el preflight de `/proc/self/mountinfo`, `losetup` y la ruta bind valide el host que consume el volumen. No exponer el socket Docker por TCP.
- La cuota dura candidata es una imagen ext4 completamente preasignada, montada persistentemente mediante loop y entregada al contenedor como único volumen de datos persistente. Es una propuesta pendiente de pruebas, no una garantía operativa actual.
- El contenedor previsto usa red interna dedicada, sin puertos publicados, rootfs de solo lectura, `tmpfs` acotado y rotación de logs. Ninguna imagen se aprobará sin digest inmutable, revisión de `VOLUME` y asignación de todas las rutas escribibles a almacenamiento limitado.
- No se encontraron bloques `backend` en los archivos `.tf` del checkout ni referencias a MinIO/Consul/S3 en Compose o ejemplos de entorno revisados. La infraestructura y credenciales disponibles fuera del repositorio aún deben inventariarse antes de elegir backend. No usar estado local como alternativa.
- El portal conserva autenticación, autorización y derivación del tenant desde la sesión. El runner no confiará en tenant enviado libremente por el cliente ni en una cabecera sin vincularla con la operación durable.

## Gates pendientes

No ejecutar `apply` hasta tener evidencia de:

1. Aprovisionamiento idempotente y montaje persistente de la cuota ext4, probado en un entorno descartable con llenado, rechazo de escritura excedente, reinicio y recuperación.
2. Preflight y daemon Docker en el mismo host; límites efectivos de CPU/RAM y ausencia de volúmenes o rutas escribibles fuera de la cuota.
3. Módulo validado con versión fijada de Terraform: `fmt -check`, `init -backend=false`, `validate`, planes sin recursos y destrucción limitada a la solicitud.
4. Runner privado, autenticado, durable, recuperable e idempotente, con operaciones tipadas y catálogo cerrado.
5. Backend remoto con persistencia y bloqueo concurrente comprobado; credenciales fuera del repositorio.
6. Identidad piloto autorizada y principal ACL de Guacamole verificado. Esta identidad no existe y no debe crearse durante la preparación.
7. Plantilla seleccionada explícitamente por el dueño y probada con sus rutas escribibles.

Los booleanos `*_verified` del módulo actual son valores de entrada autodeclarados: no constituyen evidencia de que esos controles se hayan comprobado. Se mantienen cerrados y no sustituyen las comprobaciones efectivas que deberá ejecutar el runner.

## Validación ya realizada

- Ocho pruebas del preflight con fixtures y dieciséis del aprovisionador: 24/24 pasan. La última valida la unidad `.mount` con `systemd-analyze verify`; las demás no montan ext4 ni prueban una cuota física.
- El aprovisionador rechaza raíces no canónicas o inseguras, imágenes existentes con propietario/permisos inadecuados y unidades systemd que no sean archivos regulares seguros o no coincidan exactamente con la configuración esperada.
- Una prueba real en `/tmp` creó una imagen de 16 MiB con `fallocate`, `mkfs.ext4 -E nodiscard` y una segunda preasignación; `blkid` confirmó ext4 y `st_blocks` confirmó asignación completa. Se detectó que `mkfs.ext4` reduce bloques asignados si no se preasigna de nuevo, y el aprovisionador ahora lo corrige y verifica. No se montó la imagen.
- `openspec validate tenant-compute-docker-pilot --strict`: válido tras alinear propuesta, diseño, requisitos y tareas.
- Sintaxis Python: validada en la preparación previa.
- Sin prueba real de montaje, cuota, reinicio o Docker en Kingu; sin Terraform y sin `apply`.

## Operación y evidencia

La aplicación real requiere autorización explícita posterior a todos los gates. Debe verificarse acceso autorizado, aislamiento entre tenants, ausencia de puertos públicos, límites efectivos, integraciones acordadas y destrucción limpia. Registrar por separado preparación local, preflight remoto y despliegue que efectivamente se haya ejecutado. No declarar T4 desplegado por tener un módulo, un plan o documentación.
