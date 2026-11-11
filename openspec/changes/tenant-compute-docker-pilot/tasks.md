# Tasks

## 1. Almacenamiento con cuota dura

- [x] 1.1 Aprovisionador en runner Rust verificado: imagen ext4 loop 32 MiB, `ENOSPC`, remonte persistente, unidad systemd generada y 12/12 tests. Límite físico demostrado localmente; Kingu/reinicio VM quedan en 4.2.
- [x] 1.2 Preflight 100% Rust con `fmt`/`init -backend=false`/`validate` OK y bloqueo end-to-end verificado (plan rechazado con gates en `false`). Kingu/VM descartable quedan en 4.2.

## 2. Módulo Terraform Docker

- [x] 2.1 Módulo con proveedor Docker local, validaciones y `fmt`/`init -backend=false`/`validate` OK; plan sin recursos ejecutado 2026-11-11 con gates autorizados: 4 a crear (`docker_image/network/container` + `deployment_gates`), 0 cambios, 0 destrucciones; recursos nombrados `laespiguita-<operation_id>`. Sin apply.
- [x] 2.2 Red interna dedicada por operación, sin puertos publicados, rootfs de solo lectura, límites CPU/RAM efectivos en el plan, volumen ext4 a `/workspace`, `tmpfs` acotado y logs con rotación; executor exige mismo host que el daemon y rechaza imágenes con digest no sha256. Límites efectivos bajo carga y rutas escribibles por imagen quedan para plantilla aprobada + Docker real.
- [x] 2.3 Destrucción acotada verificada por diseño: el plan de creación solo contiene 4 recursos `tenant+operation`; `terraform plan -destroy` sobre estado vacío confirma 0 cambios ajenos. La imagen ext4 es tenant-scoped y se preserva; el purge requiere comando operador aparte. Falta probar destroy real contra Docker (requiere plantilla + daemon).
- [x] 2.4 Purge implementado como comando operador local (`purge-tenant --confirm-tenant=`), con root, DSN, cero referencias activas/contenedores y verificación de unidad/loop/imagen; 12/12 tests unitarios. Falta ejecución real (requiere root + almacenamiento montado).

## 3. Runner separado y estado

- [x] 3.1 Runner Rust con idempotencia concurrente 5→1, conflicto 409, aislamiento cross-tenant y 12/12 tests en PostgreSQL TLS aislado.
- [x] 3.2 Backend `http` con roundtrip cifrado 3 MiB, contención LOCK/UNLOCK/DELETE y `sslmode=verify-full` en DB aislada. Backend remoto operativo e identidad piloto quedan como gates de despliegue, no de código.
- [x] 3.3 Estados monotónicos y respuestas saneadas verificados en entorno aislado (sin secretos/rutas internas en respuestas).
- [x] 3.4 Wrapper fijo validado con plan sin recursos; socket Unix explícito y env limpiado.

## 4. Verificación integrada

- [x] 4.1 OpenSpec válido, `cargo test` 12/12, portal completo 344/344, Terraform `fmt -check`/`validate`, plan sin recursos y `diff --check` OK. Sin apply.
- [x] 4.2 Preflight de solo lectura en Kingu ejecutado 2026-11-11 (autorización explícita del dueño): Docker 29.9.3 local (`unix:///var/run/docker.sock`, 0 contenedores/imágenes), root ext4 sin cuotas nativas (128 GB libres), sin `/srv/sentinel/tenants` (nada aprovisionado). El daemon Docker y el preflight correrían en el mismo host. Cuota operativa sigue sin declararse hasta llenado/reinicio/recuperación con plantilla aprobada.
- [ ] 4.3 La plantilla está aplazada por decisión del dueño; no elegir ni desplegar WordPress, escritorio u otra carga por inferencia. Antes de habilitar una, revisar digest, `VOLUME`, rutas escribibles, red y aceptación explícita.

## Workflow follow-up

- Archivar el cambio cuando la implementación esté completa y las validaciones requeridas pasen.
- El `apply` piloto permanece bloqueado hasta contar con identidad autorizada, ACL Guacamole verificada y backend remoto con lock.