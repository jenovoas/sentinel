# Tasks

## 1. Alcance, preflight y preservación

- [x] 1.1 Añadir T10 a `docs/ops/fase0-tareas.md` para autorizar solo gestión de logs del sistema en los seis hosts; `git diff --check` y `openspec validate limite-agregado-logs --strict` pasan, y la excepción de Hércules/Ocean excluye DNS, AD, firewall y Sentinel.
- [x] 1.2 Revalidar en solo lectura los seis hosts, rutas, filesystems, tamaños, descriptores abiertos, espacio y servicios; evidencia en `Cloud/AUDITORIA_RETENCION_LOGS_2026-11-05.md`. Todos los paths comprobados comparten root ext4; Ocean se revisó vía `/proc/*/fd` porque no tiene `lsof`.
- [ ] 1.3 Medir bytes transferidos por Alloy→Loki y revisar las métricas/consultas de ingestión; identificar el escritor del CSV y verificar respaldo/restauración antes de cualquier cambio, sin truncar ni rotar el archivo.

## 2. Cuota física agregada

- [ ] 2.1 En VM/imagen descartable, probar filesystem ext4 fijo de 1 GiB, bind mounts de todas las rutas de logs, persistencia tras reinicio, rechazo de escrituras excedentes incluso como root y rollback. La prueba aislada de 64 MiB rechazó escrituras de root con `ENOSPC`; una segunda confirmó separación de datos no-log. El 2026-11-06 otra imagen ext4 desechable de 1 GiB se llenó como root: un bloque adicional falló con `ENOSPC`, `e2fsck -fn` terminó limpio y se retiraron imagen/montaje temporales. En Fénix, `systemd-analyze verify` validó las unidades y `/var/log` reportó la imagen de 1 GiB. El reboot real de Fénix del 2026-11-06 confirmó el montaje; todavía falta la prueba descartable con todas las rutas bind y el rollback integral.
- [ ] 2.2 Definir arranque/recuperación de imágenes fijas por host. Las seis raíces son ext4; `/var/log` y el volumen Loki en Marte comparten root. En Fénix, el reboot real del 2026-11-06 (19:45:11 UTC) montó las unidades habilitadas `var-lib-sentinel-logquota-fs.mount` y `var-log.mount`; ambas estaban activas a las 19:45:16 UTC, antes de Docker (19:45:35) y Samba (19:45:36). La imagen de 1.073.741.824 bytes persistió y `/var/log` quedó en ext4 sobre `/dev/loop0`. Falta documentar y verificar el rollback operativo; los otros cinco hosts no cambiaron. El CSV científico de Kingu sigue intacto y fuera del alcance de este piloto.
- [ ] 2.3 Aplicar capacidad física agregada máxima de 1 GiB por host: `/var/log` con 1 GiB en Fénix, Kingu, Hércules, Ocean e ifenix; `/var/log` 512 MiB + Loki 512 MiB en Marte. En Fénix está activa la imagen ext4 de 1 GiB sobre `/var/log`; tras reiniciar firewalld el 2026-11-06, se verificó por dispositivo/inode que su descriptor apunta a esa imagen. Los logs antiguos del root se compararon con SHA-256: 10 versiones divergentes se archivaron dentro de la cuota y se retiraron 51 archivos idénticos o archivados (98.717.057 bytes); se preservan el `cloud-init.log` abierto en la sesión de monitoreo y `image_build_date`. Tras el reboot, `/var/log` reportó 112 MiB usados y 794 MiB disponibles. La cuota de 1 GiB sigue aplicada solo en Fénix; los otros cinco nodos no cambiaron.

## 3. Límites por fuente y filtrado remoto

- [ ] 3.1 Mantener journald, archivos del sistema, logs de contenedores y Loki dentro del filesystem agregado. En Fénix se reiniciaron journald, Samba y, con aprobación explícita, firewalld para reabrir logs tras el mount; dispositivo/inode confirma que firewalld escribe en `/var/log` sobre `/dev/loop0`. AD trust, consulta SOA local y 20/20 contenedores se verificaron sanos; `docker info` muestra `journald` predeterminado y `live-restore=true`; todos los contenedores activos usan `journald` no bloqueante con búfer de 4 MiB, sin `8m×2`. Se preservaron los volúmenes. La sesión `less` que monitorea `cloud-init.log` mantiene lectura al archivo antiguo; no escribe. Marte conserva 10 contenedores JSON; no se tocó.
- [ ] 3.2 Actualizar Alloy para exportar exclusivamente eventos de seguridad/errores verificables; probar muestras reales de cada fuente y confirmar que eventos sin clasificación no salen a Loki.
- [x] 3.3 Excluir `/var/log/sentinel/phonon_data.csv` de la cuota como dato científico y preservar sus bytes y ruta visible. Lectura actual en Kingu: 1.726.506.558 bytes; no se modificó. El estado puntual de `lsof` no mostró un escritor abierto, pero no demuestra que nunca exista.

## 4. Piloto, despliegue y cierre

- [ ] 4.1 Completar el piloto Fénix y verificar cuota, servicios, historial retenido, eventos Loki y bytes transmitidos antes/después. El reboot real del 2026-11-06 confirmó la imagen de 1 GiB, el orden de montaje previo a Docker/Samba, 20/20 contenedores activos (todos con journald no bloqueante y búfer de 4 MiB), firewalld activo con 73 rich rules runtime/permanentes coincidentes, trust Samba correcto y SOA local. A las 19:55 UTC Alloy reportó 643.559 bytes enviados desde su arranque tras el reboot y cero bytes descartados; Loki respondió 200 en `10.88.0.6:3100/ready`. El endpoint de consulta Loki devolvió 401 sin identidad, por lo que no se afirma verificación del contenido ingerido ni comparación válida con el contador previo (reiniciado con Alloy). Falta validar rollback integral y consulta autenticada de ingestión; no se llenó `/var/log` productivo.
- [ ] 4.2 Desplegar gradualmente en los nodos restantes, con backup previo, validación de configuración, smoke test y rollback por nodo; respetar exclusiones de DMZ.
- [ ] 4.3 Ejecutar `openspec validate --strict`, registrar evidencias/limitaciones en repo y vault, y completar el checklist solo para trabajo efectivamente probado o desplegado.

## Workflow follow-up

- Archivar este cambio cuando las tareas operativas y validaciones requeridas hayan concluido; no archivar mientras el límite agregado siga pendiente en producción.
