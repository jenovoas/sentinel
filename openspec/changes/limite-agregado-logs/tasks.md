# Tasks

## 1. Alcance, preflight y preservación

- [x] 1.1 Añadir T10 a `docs/ops/fase0-tareas.md` para autorizar solo gestión de logs del sistema en los seis hosts; `git diff --check` y `openspec validate limite-agregado-logs --strict` pasan, y la excepción de Hércules/Ocean excluye DNS, AD, firewall y Sentinel.
- [x] 1.2 Revalidar en solo lectura los seis hosts, rutas, filesystems, tamaños, descriptores abiertos, espacio y servicios; evidencia en `Cloud/AUDITORIA_RETENCION_LOGS_2026-11-05.md`. Todos los paths comprobados comparten root ext4; Ocean se revisó vía `/proc/*/fd` porque no tiene `lsof`.
- [ ] 1.3 Medir bytes transferidos por Alloy→Loki y revisar las métricas/consultas de ingestión; identificar el escritor del CSV y verificar respaldo/restauración antes de cualquier cambio, sin truncar ni rotar el archivo.

## 2. Cuota física agregada

- [ ] 2.1 En VM/imagen descartable, probar cuota ext4 de proyecto común sobre varios árboles de logs, herencia a archivos/directorios recreados, persistencia tras reinicio, rechazo de escrituras al superar 5 GiB y rollback; documentar comandos y salidas reproducibles. Evidencia parcial 2026-11-06: la prueba aislada se ejecutó en Fénix (host confirmado), tras instalar `quota` y cargar/retirar temporalmente el módulo loop; imagen ext4 desechable de 7 GiB, ID 4242 heredado, hard limit 5 GiB persistente tras desmontar/remontar, escrituras como root sin `CAP_SYS_RESOURCE` detenidas con `Disk quota exceeded`, uso final 5.241.864 KiB frente a 5.242.880 KiB, `e2fsck -fn` limpio e imagen eliminada. Pendientes: reinicio real de VM y automatización reproducible del ensayo. Hallazgo de seguridad: root con `CAP_SYS_RESOURCE` superó una cuota de prueba de 32 MiB; verificar el comportamiento de los escritores reales antes de desplegar.
- [ ] 2.2 Determinar y documentar el procedimiento seguro para habilitar la cuota agregada de 1 GiB en cada host. Evidencia 2026-11-06: las seis raíces son ext4 y no tienen activa la función `project`; en una imagen desechable, `tune2fs -O project` falló mientras el sistema de archivos estaba montado (`The quota feature may only be changed when the filesystem is unmounted and not in use`). No se modificó ningún sistema de archivos real. Hace falta respaldo recuperable y ventana de mantenimiento fuera de línea.
- [ ] 2.3 Con gates aprobados, aplicar y verificar el límite duro agregado de 1 GiB por host a todas las rutas inventariadas; confirmar cobertura/herencia y que ningún escritor pueda eludirlo. Preflight de capacidades 2026-11-06: `dockerd`/`containerd` tienen `CAP_SYS_RESOURCE` en Fénix, Kingu, Marte e ifenix; `rsyslogd` en Hércules y `guardian-uplink`, `sentinel-pai-ne` y `sentinel-securi` en Marte también lo tienen. La prueba en imagen mostró que ese privilegio puede eludir una cuota ext4 de proyecto; el diseño debe usar un límite de filesystem que no admita bypass o retirar y validar esas capacidades. No se aplicó cuota agregada en producción.

## 3. Límites por fuente y filtrado remoto

- [ ] 3.1 Distribuir el presupuesto de 1 GiB entre journald, archivos del sistema, registros de contenedores y Loki; validar el límite agregado, no un tope aislado por contenedor. Estado observado 2026-11-06: después del vacuum, journald informa Fénix 50,6 MiB, Kingu 33,1 MiB, Marte 49,5 MiB, Hércules 38,3 MiB, Ocean 49,2 MiB e ifenix 19,6 MiB. En Fénix, 17/20 contenedores activos carecen de rotación y tres tienen `json-file` `8m × 2`; en Marte, ocho de diez tienen `8m × 2` y los dos contenedores de réplica carecen de opciones. Esos topes son por contenedor y no equivalen al presupuesto total del servidor. Docker documenta que los contenedores existentes no heredan cambios de configuración y que sus archivos JSON no deben manipularse desde herramientas externas. El total agregado sigue sin cuota.
- [ ] 3.2 Actualizar Alloy para exportar exclusivamente eventos de seguridad/errores verificables; probar muestras reales de cada fuente y confirmar que eventos sin clasificación no salen a Loki.
- [ ] 3.3 Definir rotación del CSV solo después de identificar el escritor, aprobar retención y verificar copia restaurable; probar continuidad de escritura y preservar el historial previo.

## 4. Piloto, despliegue y cierre

- [ ] 4.1 Desplegar un nodo piloto solo después de aprobar gates de filesystem; verificar cuota, servicios, historial retenido, eventos Loki y bytes transmitidos antes/después.
- [ ] 4.2 Desplegar gradualmente en los nodos restantes, con backup previo, validación de configuración, smoke test y rollback por nodo; respetar exclusiones de DMZ.
- [ ] 4.3 Ejecutar `openspec validate --strict`, registrar evidencias/limitaciones en repo y vault, y completar el checklist solo para trabajo efectivamente probado o desplegado.

## Workflow follow-up

- Archivar este cambio cuando las tareas operativas y validaciones requeridas hayan concluido; no archivar mientras el límite agregado siga pendiente en producción.
