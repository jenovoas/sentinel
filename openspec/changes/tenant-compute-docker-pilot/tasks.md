# Tasks

## 1. Almacenamiento con cuota dura

- [ ] 1.1 El aprovisionador idempotente y la unidad systemd están implementados localmente; 16 pruebas del aprovisionador y 8 del preflight (24 en total) cubren comandos simulados, rechazo de imágenes/unidades con permisos inseguros y validación de la unidad con `systemd-analyze verify`. Las raíces e imágenes exigen ruta canónica, propietario efectivo y ausencia de escritura/acceso por grupo u otros; la unidad existente debe ser regular, segura y coincidir exactamente. Una imagen temporal de 16 MiB se preasignó, formateó con `mkfs.ext4 -E nodiscard`, volvió a preasignar y verificó con `blkid`/`st_blocks`; falta probar montaje persistente en una VM descartable, llenado, escritura excedente, reinicio y recuperación. No ejecutar en Kingu.
- [ ] 1.2 El preflight e integración con Terraform están escritos; 8 pruebas unitarias con fixtures pasan. Falta validar con Terraform, probar el bloqueo end-to-end y demostrar límite físico, llenado y remonte en entorno descartable. No se ha probado en Kingu.

## 2. Módulo Terraform Docker

- [ ] 2.1 El módulo local ya fija proveedor Docker y valida tenant/CIDR/digest y algunos límites; Terraform no está instalado, por lo que faltan `fmt`, `init -backend=false`, `validate` y plan sin recursos.
- [ ] 2.2 Verificar red interna, ausencia de puertos publicados, rootfs de solo lectura, límites CPU/RAM efectivos, volumen ext4, `tmpfs` y rotación de logs. El executor debe usar el mismo host que el daemon Docker y rechazar imágenes con `VOLUME` o rutas escribibles fuera de almacenamiento limitado.
- [ ] 2.3 Implementar destrucción acotada a tenant+solicitud; probar planes de destrucción sin afectar recursos ajenos ni eliminar respaldos no autorizados.

## 3. Runner separado y estado

- [ ] 3.1 Implementar runner Rust separado del portal/Cortex, privado y autenticado; persistir tenant+solicitud+clave idempotente y huella del payload, con recuperación durable y exclusión por lease. El catálogo queda vacío hasta que se elija una plantilla.
- [ ] 3.2 No hay bloques `backend` en los archivos `.tf` del checkout ni referencias a MinIO/Consul/S3 en los archivos Compose y ejemplos de entorno revisados. El inventario operativo fuera del repositorio no está hecho; no afirmar que no exista un servicio utilizable. Exigir backend remoto y lock funcional; si no hay uno compatible, detenerse hasta acordar proveedor. No permitir estado local ni credenciales en Git.
- [ ] 3.3 Publicar estados monotónicos, saneados y aislados por tenant; comprobar tenant+operación en el runner y no confiar solo en una cabecera. Verificar que secretos, rutas/direcciones privadas y errores internos no aparecen en respuestas.
- [ ] 3.4 Ejecutar Terraform solo con módulo, directorio, variables y argumentos fijos; nunca aceptar comandos, rutas ni configuración Terraform arbitrarios del portal. No abrir el socket Docker por TCP.

## 4. Verificación integrada

- [ ] 4.1 Ejecutar OpenSpec estricto, pruebas, `terraform fmt`/`validate`, planes sin recursos y `git diff --check`; registrar limitaciones de herramientas o gates pendientes.
- [ ] 4.2 Tras pruebas aisladas, hacer solo preflight de lectura en Kingu para montaje, capacidad y coincidencia con el daemon Docker; no instalar ni montar recursos durante el preflight. No declarar cuota operativa hasta probar llenado, reinicio y recuperación.
- [ ] 4.3 La plantilla está aplazada por decisión del dueño; no elegir ni desplegar WordPress, escritorio u otra carga por inferencia. Antes de habilitar una, revisar digest, `VOLUME`, rutas escribibles, red y aceptación explícita.

## Workflow follow-up

- Archivar el cambio cuando la implementación esté completa y las validaciones requeridas pasen.
- El `apply` piloto permanece bloqueado hasta contar con identidad autorizada, ACL Guacamole verificada y backend remoto con lock.