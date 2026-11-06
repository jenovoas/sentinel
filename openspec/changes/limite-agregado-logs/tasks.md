# Tasks

## 1. Alcance, preflight y preservación

- [x] 1.1 Añadir T10 a `docs/ops/fase0-tareas.md` para autorizar solo gestión de logs del sistema en los seis hosts; `git diff --check` y `openspec validate limite-agregado-logs --strict` pasan, y la excepción de Hércules/Ocean excluye DNS, AD, firewall y Sentinel.
- [x] 1.2 Revalidar en solo lectura los seis hosts, rutas, filesystems, tamaños, descriptores abiertos, espacio y servicios; evidencia en `Cloud/AUDITORIA_RETENCION_LOGS_2026-11-05.md`. Todos los paths comprobados comparten root ext4; Ocean se revisó vía `/proc/*/fd` porque no tiene `lsof`.
- [ ] 1.3 Medir bytes transferidos por Alloy→Loki y revisar las métricas/consultas de ingestión; identificar el escritor del CSV y verificar respaldo/restauración antes de cualquier cambio, sin truncar ni rotar el archivo.

## 2. Cuota física agregada

- [ ] 2.1 En VM/imagen descartable, probar cuota ext4 de proyecto común sobre varios árboles de logs, herencia a archivos/directorios recreados, persistencia tras reinicio, rechazo de escrituras al superar 5 GiB y rollback; documentar comandos y salidas reproducibles. Evidencia parcial 2026-11-06: la prueba aislada se ejecutó en Fénix (host confirmado), tras instalar `quota` y cargar/retirar temporalmente el módulo loop; imagen ext4 desechable de 7 GiB, ID 4242 heredado, hard limit 5 GiB persistente tras desmontar/remontar, escrituras como root sin `CAP_SYS_RESOURCE` detenidas con `Disk quota exceeded`, uso final 5.241.864 KiB frente a 5.242.880 KiB, `e2fsck -fn` limpio e imagen eliminada. Pendientes: reinicio real de VM y automatización reproducible del ensayo. Hallazgo de seguridad: root con `CAP_SYS_RESOURCE` superó una cuota de prueba de 32 MiB; verificar el comportamiento de los escritores reales antes de desplegar.
- [ ] 2.2 Determinar y documentar el procedimiento seguro para habilitar cuotas `project` en cada root ext4; si requiere desmontaje, `e2fsck`, reinicio o acceso de recuperación, detener cambios de host y obtener autorización explícita de ventana, consola fuera de banda y backup verificable. Evidencia Fénix 2026-11-06: `/dev/vda2` es ext4 y `tune2fs -l` no muestra la función `project`; no se habilitó ni modificó el filesystem.
- [ ] 2.3 Con gates aprobados, aplicar y verificar el mismo límite duro de 5 GiB por host a todas las rutas inventariadas; confirmar asignaciones/herencia, probar escritura excedente denegada con las capacidades efectivas de cada escritor y demostrar que ningún proceso con `CAP_SYS_RESOURCE` puede eludir el techo; no afectar datos fuera del alcance. Preflight de capacidades 2026-11-06: `dockerd`/`containerd` tienen `CAP_SYS_RESOURCE` en Fénix, Kingu, Marte e ifenix; `rsyslogd` en Hércules y `guardian-uplink`, `sentinel-pai-ne` y `sentinel-securi` en Marte también lo tienen. `systemd-journal`, Alloy y Loki no lo muestran. No se aplicó cuota agregada en producción: la función `project` falta en `/dev/vda2` y sigue pendiente el gate de recuperación/autorización para filesystem.

## 3. Límites por fuente y filtrado remoto

- [ ] 3.1 Definir por host los sublímites de journald, rsyslog/logrotate, Docker y Loki según el inventario, preservando logs existentes; validar cada configuración antes de recargar servicios. Evidencia Fénix 2026-11-06: journald tiene `SystemMaxUse=512M` y `SystemKeepFree=5G` en `/etc/systemd/journald.conf.d/90-log-limits.conf`; respaldo `/var/backups/journald.conf.pre-log-limits.2026-11-06`; servicio `active`, uso observado 505,4M, sin vacuum. Los 20 contenedores activos muestran `json-file`, `max-size=8m`, `max-file=2`; se respaldaron 21 archivos previos en `/var/backups/fenix-docker-json-logs.2026-11-06.tar.gz` (27.514.640 bytes; lectura del tar verificada) antes de recrearlos; Jaime pidió borrarlo para recuperar espacio y se confirmó su eliminación. `laespiguita-db` conserva el volumen `laespiguita_pgdata` y está saludable. Consumo observado tras recrear: `/var/log` 528M y `/var/lib/docker/containers` 1,0M. Quedan sin límite por fuente los demás hosts y las rutas rsyslog/Loki; esto no garantiza un máximo agregado de 5 GiB. No inferir que `stderr` equivale a todos los errores ni que journald filtra por sí solo la exportación.
- [ ] 3.2 Actualizar Alloy para exportar exclusivamente eventos de seguridad/errores verificables; probar muestras reales de cada fuente y confirmar que eventos sin clasificación no salen a Loki.
- [ ] 3.3 Definir rotación del CSV solo después de identificar el escritor, aprobar retención y verificar copia restaurable; probar continuidad de escritura y preservar el historial previo.

## 4. Piloto, despliegue y cierre

- [ ] 4.1 Desplegar un nodo piloto solo después de aprobar gates de filesystem; verificar cuota, servicios, historial retenido, eventos Loki y bytes transmitidos antes/después.
- [ ] 4.2 Desplegar gradualmente en los nodos restantes, con backup previo, validación de configuración, smoke test y rollback por nodo; respetar exclusiones de DMZ.
- [ ] 4.3 Ejecutar `openspec validate --strict`, registrar evidencias/limitaciones en repo y vault, y completar el checklist solo para trabajo efectivamente probado o desplegado.

## Workflow follow-up

- Archivar este cambio cuando las tareas operativas y validaciones requeridas hayan concluido; no archivar mientras el límite agregado siga pendiente en producción.
