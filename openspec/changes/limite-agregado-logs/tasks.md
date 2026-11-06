# Tasks

## 1. Alcance, preflight y preservación

- [x] 1.1 Añadir T10 a `docs/ops/fase0-tareas.md` para autorizar solo gestión de logs del sistema en los seis hosts; `git diff --check` y `openspec validate limite-agregado-logs --strict` pasan, y la excepción de Hércules/Ocean excluye DNS, AD, firewall y Sentinel.
- [x] 1.2 Revalidar en solo lectura los seis hosts, rutas, filesystems, tamaños, descriptores abiertos, espacio y servicios; evidencia en `Cloud/AUDITORIA_RETENCION_LOGS_2026-11-05.md`. Todos los paths comprobados comparten root ext4; Ocean se revisó vía `/proc/*/fd` porque no tiene `lsof`.
- [ ] 1.3 Medir bytes transferidos por Alloy→Loki y revisar las métricas/consultas de ingestión; identificar el escritor del CSV y verificar respaldo/restauración antes de cualquier cambio, sin truncar ni rotar el archivo.

## 2. Cuota física agregada

- [ ] 2.1 En VM/imagen descartable, probar filesystem ext4 fijo de 1 GiB, bind mounts de todas las rutas de logs, persistencia tras reinicio, rechazo de escrituras excedentes incluso como root y rollback. La prueba desechable ext4 de 64 MiB rechazó escrituras de root con `ENOSPC`; una segunda confirmó separación de datos no-log. En Fénix, `systemd-analyze verify` validó las unidades y el montaje en vivo reportó la imagen de 1 GiB en `/var/log`. Sigue pendiente probar arranque real/reinicio y rollback integral en un entorno descartable; no marcar esta tarea completa.
- [ ] 2.2 Definir arranque/recuperación de imágenes fijas por host. Las seis raíces son ext4; `/var/log` y el volumen Loki en Marte comparten root. En Fénix están instaladas y habilitadas las unidades systemd para montar la imagen antes de journald, Docker y Samba. No hubo reinicio del host; falta validar el arranque y documentar rollback operativo. El CSV científico de Kingu sigue sin cambio y fuera del alcance de este piloto.
- [ ] 2.3 Aplicar capacidad física agregada máxima de 1 GiB por host: `/var/log` con 1 GiB en Fénix, Kingu, Hércules, Ocean e ifenix; `/var/log` 512 MiB + Loki 512 MiB en Marte. En Fénix solo está activa la imagen de 1 GiB sobre `/var/log`; la cuota agregada sigue incompleta porque firewalld mantiene un descriptor al árbol original. No borrar el original ni declarar el techo cumplido hasta cerrar esa excepción y medir rechazo excedente en producción. Los otros cinco nodos no cambiaron.

## 3. Límites por fuente y filtrado remoto

- [ ] 3.1 Mantener journald, archivos del sistema, logs de contenedores y Loki dentro del filesystem agregado. En Fénix se reinició journald y Samba para reabrir los logs tras el mount; AD trust, consulta SOA local y los servicios Docker se verificaron sanos. `docker info` muestra `journald` como predeterminado, `live-restore=true`; los 20/20 contenedores activos usan `journald` no bloqueante con búfer de 4 MiB, sin `8m×2`. Se preservaron los volúmenes; PostgreSQL `laespiguita-db` quedó `healthy` con su volumen original. Sin embargo firewalld aún escribe en un descriptor del filesystem raíz original, por lo que Fénix no cumple aún el agregado físico. Marte conserva 10 contenedores JSON; no se tocó.
- [ ] 3.2 Actualizar Alloy para exportar exclusivamente eventos de seguridad/errores verificables; probar muestras reales de cada fuente y confirmar que eventos sin clasificación no salen a Loki.
- [x] 3.3 Excluir `/var/log/sentinel/phonon_data.csv` de la cuota como dato científico y preservar sus bytes y ruta visible. Lectura actual en Kingu: 1.726.506.558 bytes; no se modificó. El estado puntual de `lsof` no mostró un escritor abierto, pero no demuestra que nunca exista.

## 4. Piloto, despliegue y cierre

- [ ] 4.1 Completar el piloto Fénix y verificar cuota, servicios, historial retenido, eventos Loki y bytes transmitidos antes/después. Montaje y Docker están activos, pero falta cerrar el descriptor de firewalld y comprobar el límite agregado; está pendiente la aprobación explícita del reinicio controlado de ese servicio.
- [ ] 4.2 Desplegar gradualmente en los nodos restantes, con backup previo, validación de configuración, smoke test y rollback por nodo; respetar exclusiones de DMZ.
- [ ] 4.3 Ejecutar `openspec validate --strict`, registrar evidencias/limitaciones en repo y vault, y completar el checklist solo para trabajo efectivamente probado o desplegado.

## Workflow follow-up

- Archivar este cambio cuando las tareas operativas y validaciones requeridas hayan concluido; no archivar mientras el límite agregado siga pendiente en producción.
