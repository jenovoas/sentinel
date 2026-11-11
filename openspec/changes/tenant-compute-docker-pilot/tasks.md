# Tasks

## 1. Almacenamiento con cuota dura

- [x] 1.1 El aprovisionador idempotente y la unidad systemd están implementados en el runner Rust (`services/deployment-orchestrator/src/storage.rs`); el módulo Terraform ya no usa `external`/Python y consume evidencia tipada (`verified`, bytes del filesystem y margen libre). Verificación local 2026-11-11: imagen ext4 loop de 32 MiB, preflight real con 26 464 256 B, `ENOSPC` en llenado y persistencia tras desmontaje/remontaje; `cargo test -p deployment-orchestrator` 12/12. Falta unidad persistente/recuperación tras reinicio de VM, destrucción segura y Kingu. No ejecutar en Kingu.
- [x] 1.2 El preflight en runtime es 100% Rust y alimenta variables fail-closed del módulo; Terraform 1.9.8 validó `fmt`, `init -backend=false` y `validate` en ambos módulos el 2026-11-11. Quedan VM descartable, fallos de bloqueo end-to-end y Kingu.

## 2. Módulo Terraform Docker

- [x] 2.1 El módulo fija proveedor Docker local con socket Unix validado, valida tenant/UUID/digest/límites y preflight tipado; `terraform fmt`, `init -backend=false` y `validate` pasaron el 2026-11-11 en `modules/tenant-compute` y en el wrapper del runner. No se ejecutó plan con recursos ni apply.
- [ ] 2.2 Verificar red interna, ausencia de puertos publicados, rootfs de solo lectura, límites CPU/RAM efectivos, volumen ext4, `tmpfs` y rotación de logs. El executor debe usar el mismo host que el daemon Docker y rechazar imágenes con `VOLUME` o rutas escribibles fuera de almacenamiento limitado.
- [ ] 2.3 Implementar destrucción acotada a tenant+solicitud; probar planes que eliminen solo contenedor/red de esa operación. Preservar la imagen ext4 compartida por tenant; cualquier purga requiere operación tenant-level separada, autorización explícita y cero referencias activas.
- [ ] 2.4 Implementar purge tenant-level solo como comando de operador local, no endpoint público: requiere root y confirmación explícita, DSN/consulta sin operaciones activas ni contenedores que monten la ruta. Validar tenant_id y derivar paths/unidad de forma fija; rechazar enlaces simbólicos o unidades/imágenes incompatibles y fallar cerrado si no puede verificar el loop mount.

## 3. Runner separado y estado

- [x] 3.1 Runner Rust implementado en `services/deployment-orchestrator`: API privada autenticada, idempotencia por `(tenant_id,idempotency_key)` con huella SHA-256 canónica, leases/exclusión, recuperación por etapa y catálogo cerrado vacío por defecto. Verificación 2026-11-11: idempotencia concurrente 5→1 operación, conflicto por contenido distinto, aislamiento cross-tenant y `cargo test -p deployment-orchestrator` 12/12.
- [x] 3.2 Backend Terraform `http` implementado con PostgreSQL verificado por hostname (`sslmode=verify-full` + CA opcional), estado cifrado por operación y lock/unlock transaccionales con auth por entorno. Verificación 2026-11-11 en PostgreSQL TLS temporal aislado: roundtrip de 3 MiB, contención LOCK/UNLOCK, sin local state; no se añadió base local ni configuración de producción.
- [x] 3.3 Estados `preparing/deploying/verifying/available/blocked/failed` monotónicos, consulta por tenant+operación y respuestas saneadas. El runner no expone secretos, rutas privadas ni errores internos.
- [x] 3.4 Terraform se ejecuta desde el wrapper fijo con backend `http`, variables/args fijos, socket Docker Unix local explícito y entorno limpiado. No acepta comandos/rutas/config Terraform arbitrarios ni expone Docker por TCP/creds en CLI.

## 4. Verificación integrada

- [x] 4.1 OpenSpec estricto válido en Sentinel y portal el 2026-11-11; `cargo test -p deployment-orchestrator` 12/12; portal focalizado 25/25; `terraform fmt -check`, `init -backend=false`, `validate` y `git diff --check` pasados. No se ejecutó plan con recursos ni apply; la suite completa del portal se mantiene sin repetir por no haber cambiado su código en esta fase.
- [ ] 4.2 Tras pruebas aisladas, hacer solo preflight de lectura en Kingu para montaje, capacidad y coincidencia con el daemon Docker; no instalar ni montar recursos durante el preflight. No declarar cuota operativa hasta probar llenado, reinicio y recuperación.
- [ ] 4.3 La plantilla está aplazada por decisión del dueño; no elegir ni desplegar WordPress, escritorio u otra carga por inferencia. Antes de habilitar una, revisar digest, `VOLUME`, rutas escribibles, red y aceptación explícita.

## Workflow follow-up

- Archivar el cambio cuando la implementación esté completa y las validaciones requeridas pasen.
- El `apply` piloto permanece bloqueado hasta contar con identidad autorizada, ACL Guacamole verificada y backend remoto con lock.