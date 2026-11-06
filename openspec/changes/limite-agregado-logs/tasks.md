# Tasks

## 1. Alcance, preflight y preservación

- [x] 1.1 Añadir T10 a `docs/ops/fase0-tareas.md` para autorizar solo gestión de logs del sistema en los seis hosts; `git diff --check` y `openspec validate limite-agregado-logs --strict` pasan, y la excepción de Hércules/Ocean excluye DNS, AD, firewall y Sentinel.
- [x] 1.2 Revalidar en solo lectura los seis hosts, rutas, filesystems, tamaños, descriptores abiertos, espacio y servicios; evidencia en `Cloud/AUDITORIA_RETENCION_LOGS_2026-11-05.md`. Todos los paths comprobados comparten root ext4; Ocean se revisó vía `/proc/*/fd` porque no tiene `lsof`.
- [ ] 1.3 Medir bytes transferidos por Alloy→Loki y revisar las métricas/consultas de ingestión; identificar el escritor del CSV y verificar respaldo/restauración antes de cualquier cambio, sin truncar ni rotar el archivo.

## 2. Cuota física agregada

- [ ] 2.1 En VM/imagen descartable, probar filesystem ext4 fijo de 1 GiB, bind mounts de todas las rutas de logs, persistencia tras reinicio, rechazo de escrituras excedentes incluso como root y rollback. Evidencia parcial 2026-11-06: en Fénix se creó una imagen ext4 loop desechable de 64 MiB en `/dev/shm`; se montó como `upperdir` de OverlayFS y un proceso root con privilegios escribió hasta `ENOSPC`. `df` mostró cero bloques disponibles, sin posibilidad de superar la capacidad del filesystem. La imagen, los mounts y el loop se retiraron; no se modificaron servicios. Pendientes: validar el arranque real con unidades systemd y recuperación tras reinicio. La prueba anterior de cuotas de proyecto queda como historial; ese método se descarta porque `CAP_SYS_RESOURCE` lo elude y el root real requeriría desmontaje.
- [ ] 2.2 Definir arranque/recuperación de imágenes fijas por host. Las seis raíces son ext4; `/var/log` y el volumen Loki en Marte comparten root. Montar antes de iniciar escritores. Mantener el CSV científico de Kingu fuera de la imagen con bind mount al mismo path visible, sin alterar sus bytes. Respaldar configuraciones previas y validar rollback.
- [ ] 2.3 Con gates aprobados, aplicar y verificar capacidad física agregada máxima de 1 GiB por host: `/var/log` con 1 GiB en Fénix, Kingu, Hércules, Ocean e ifenix; `/var/log` 512 MiB + Loki 512 MiB en Marte. Enviar logs de contenedores a journald y excluir metadata Docker, volúmenes de bases de datos, métricas y datos Sentinel que no sean logs. Confirmar en vivo mounts y rechazo de escritura excedente. No se ha aplicado en producción.

## 3. Límites por fuente y filtrado remoto

- [ ] 3.1 Mantener journald, archivos del sistema, logs de contenedores y Loki dentro del filesystem agregado. Estado observado 2026-11-06: journald informa Fénix 50,6 MiB, Kingu 33,1 MiB, Marte 49,5 MiB, Hércules 38,3 MiB, Ocean 49,2 MiB e ifenix 19,6 MiB. En Fénix, 3/20 contenedores tienen `json-file 8m×2` y 17 no tienen opciones; en Marte, 8/10 tienen `8m×2` y 2 no tienen opciones. Fénix y Marte configurarán Docker para enviar logs a journald en modo no bloqueante; los contenedores existentes deben recrearse uno por uno para adoptar el cambio. El filesystem agregado, no una opción por contenedor, es el límite de 1 GiB.
- [ ] 3.2 Actualizar Alloy para exportar exclusivamente eventos de seguridad/errores verificables; probar muestras reales de cada fuente y confirmar que eventos sin clasificación no salen a Loki.
- [x] 3.3 Excluir `/var/log/sentinel/phonon_data.csv` de la cuota como dato científico y preservar sus bytes y ruta visible. Lectura actual en Kingu: 1.726.506.558 bytes; no se modificó. El estado puntual de `lsof` no mostró un escritor abierto, pero no demuestra que nunca exista.

## 4. Piloto, despliegue y cierre

- [ ] 4.1 Desplegar un nodo piloto solo después de aprobar gates de filesystem; verificar cuota, servicios, historial retenido, eventos Loki y bytes transmitidos antes/después.
- [ ] 4.2 Desplegar gradualmente en los nodos restantes, con backup previo, validación de configuración, smoke test y rollback por nodo; respetar exclusiones de DMZ.
- [ ] 4.3 Ejecutar `openspec validate --strict`, registrar evidencias/limitaciones en repo y vault, y completar el checklist solo para trabajo efectivamente probado o desplegado.

## Workflow follow-up

- Archivar este cambio cuando las tareas operativas y validaciones requeridas hayan concluido; no archivar mientras el límite agregado siga pendiente en producción.
