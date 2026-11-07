# Design

## Context

Ver `proposal.md` para la motivación y `specs/log-retention/spec.md` para los contratos observables. La auditoría localizó fuentes bajo `/var/log` y `/var/lib/docker`; en Fénix/Marte Loki persiste en volumen Docker. Los seis roots inspeccionados son ext4 sin funciones de cuota de proyecto habilitadas. El CSV de Kingu se escribe en modo append y contiene historial que no se truncará durante el cambio.

## Goals / Non-Goals

**Goals:**
- Aplicar un límite físico agregado duro de 1 GiB en Fénix, Kingu, Hércules, Ocean e ifenix, y de 2 GiB solo en Marte.
- Reducir la exportación de Fénix/Marte a eventos con clasificación verificable de seguridad o error.
- Evitar pérdida de historial durante migración o rotación no respaldada.

**Non-Goals:**
- Cambiar AD, DNS, firewalls, servicios Sentinel ni funciones de red en Hércules/Ocean.
- Declarar reducción de facturación sin medición de transferencia y datos del proveedor.
- Truncar el CSV o purgar logs históricos para forzar el cumplimiento del límite.

## Decisions

- **Filesystem dedicado de tamaño fijo por host.** En Fénix, Kingu, Hércules, Ocean e ifenix, crear una imagen ext4 de capacidad máxima de 1 GiB y bind-montar su árbol de logs en `/var/log`. Solo en Marte, asignar una imagen de 1 GiB a `/var/log` y otra de 1 GiB al volumen de datos de Loki, para un máximo agregado de 2 GiB. Los límites de capacidad de los filesystems no se pueden superar con `CAP_SYS_RESOURCE`. No incluir volúmenes de bases de datos, métricas ni otros datos de aplicaciones.
- **Datos no log preservados fuera de la cuota.** En Kingu, `/var/log/sentinel/phonon_data.csv` (~1,61 GiB) está clasificado como dato científico. Mantener sus bytes y el path visible con un bind mount desde el archivo original fuera del filesystem de logs; no mover, truncar ni contar ese archivo como log. Los demás logs Sentinel sí entran en el filesystem limitado.
- **Logs de contenedores a journald.** Fénix y Marte cambiarán el controlador predeterminado de Docker a `journald` con `mode=non-blocking` y un búfer finito; `/var/log/journal` comparte la capacidad asignada a `/var/log`. Así se evita poner límites pequeños independientes en cada contenedor y no se mueve la metadata bajo `/var/lib/docker/containers`. Los contenedores existentes se recrearán uno por uno para adoptar el controlador nuevo; sus volúmenes de datos permanecen intactos.
- **Gate de montajes y recuperación.** Probar en entorno descartable tamaño, persistencia al reinicio, bind mounts, rechazo de escrituras excedentes y rollback. Los mounts deben preceder a journald, rsyslog, Docker y Loki para que ningún escritor mantenga descriptores al filesystem antiguo. Respaldar configuraciones y validar montajes antes de recargar. El cambio requiere interrupción controlada de los escritores; desplegar nodo por nodo y verificar recuperación antes de avanzar.
- **Inventario antes de asignar cuota.** Revalidar rutas y filesystems en vivo. Incluir journal, syslog, audit, Sentinel y volumen Loki; los logs Docker se enrutan a journald. Excluir volúmenes de bases de datos, metadata de Docker, métricas y datos científicos. La cuota limita los bloques disponibles en el filesystem dedicado, incluidos sus metadatos.
- **Controles por fuente.** Añadir límites/rotación en journald, rsyslog/logrotate y Docker como defensa adicional y para mantener historial útil, no como prueba del techo total. Mantener retención temporal de Loki junto a la cuota física.
- **Filtrado en origen.** Aplicar reglas por fuente antes de la escritura remota a Loki. Solo clasificaciones de seguridad/error verificadas pasan; eventos sin nivel o parseo verificable se excluyen del envío remoto. Los datos locales siguen la política local; el CSV de Kingu no se envía ni rota hasta definir retención y verificar un respaldo.
- **Separación de alcance DMZ.** `hercules` y `ocean` se tratan exclusivamente como hosts DNS externos para esta política del sistema operativo: no cambiar su DNS, AD, firewall ni instalar/modificar Sentinel.

## Risks / Trade-offs

- [La imagen/mount no está lista cuando comienza un escritor] → declarar dependencias systemd, fallar cerrado y verificar en arranque controlado antes de seguir.
- [Una app conserva un descriptor abierto hacia el filesystem antiguo] → ventana de mantenimiento por host; reiniciar solo los escritores necesarios y validar sus rutas posteriores.
- [Una fuente monopoliza su capacidad asignada] → en Marte separar `/var/log` (1 GiB) de Loki (1 GiB); cada uno de los otros hosts reserva hasta 1 GiB para `/var/log`.
- [Cuota llena impide nuevas escrituras] → elegir presupuestos/retención por fuente y verificar comportamiento; mantener margen de filesystem ajeno a la cuota para operación del host.
- [Clasificación inconsistente omite errores o envía ruido] → probar muestras reales por fuente, rechazar por defecto eventos no clasificados y medir bytes enviados antes/después.
- [Rotar el CSV altera datos de Sentinel] → investigar el proceso escritor, respaldar y verificar restauración, y no truncar hasta aprobar explícitamente la retención.

## Migration Plan

1. Completar OpenSpec y agregar tarea operativa para limitar logs en los seis hosts, preservando las exclusiones de AD/DNS/firewall/Sentinel en la DMZ.
2. Preflight de solo lectura en cada host: branch/estado, conectividad, servicios, uso y filesystem, rutas abiertas, espacio disponible y política de recuperación. Cuantificar transferencia a Loki; anotar que la facturación no se verificó.
3. Preparar y probar en VM/imagen descartable las imágenes ext4 fijas, los bind mounts de rutas de logs, la persistencia al reinicio, el rechazo de escrituras excedentes como root y el rollback. Validar la excepción del CSV científico de Kingu y las capacidades 1+1 GiB de Marte.
4. Con los gates aprobados, desplegar un nodo piloto tras respaldo verificable y ventana de mantenimiento; validar filesystem, escritores y servicios antes de avanzar.
5. Avanzar nodo por nodo con respaldo y rollback antes de cada cambio; medir cuota y egreso.
6. Rollback: restaurar configuraciones previas y rutas desde respaldos; no desactivar/retirar cuota si eso permite crecimiento sin límite; no borrar datos de logs o CSV como parte de la reversión.
7. Registrar preparación, pruebas y despliegue real por separado en el repositorio y vault.

## Open Questions

- El CSV de Kingu se clasifica como dato científico y queda excluido de la cuota; se preservan su contenido y ruta visible.
