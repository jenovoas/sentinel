# Design

## Context

Ver `proposal.md` para la motivación y `specs/log-retention/spec.md` para los contratos observables. La auditoría localizó fuentes bajo `/var/log` y `/var/lib/docker`; en Fénix/Marte Loki persiste en volumen Docker. Los seis roots inspeccionados son ext4 sin funciones de cuota de proyecto habilitadas. El CSV de Kingu se escribe en modo append y contiene historial que no se truncará durante el cambio.

## Goals / Non-Goals

**Goals:**
- Aplicar un límite agregado duro común a las rutas de logs identificadas en cada host.
- Reducir la exportación de Fénix/Marte a eventos con clasificación verificable de seguridad o error.
- Evitar pérdida de historial durante migración o rotación no respaldada.

**Non-Goals:**
- Cambiar AD, DNS, firewalls, servicios Sentinel ni funciones de red en Hércules/Ocean.
- Declarar reducción de facturación sin medición de transferencia y datos del proveedor.
- Truncar el CSV o purgar logs históricos para forzar el cumplimiento del límite.

## Decisions

- **Cuota ext4 de proyecto agregada por host.** Asignar un mismo project ID y límite duro a todas las raíces de logs incluidas en el mismo filesystem, con herencia para archivos y directorios nuevos. Se prefiere a límites aislados por servicio porque estos no limitan el agregado, y a reubicar todas las fuentes a un filesystem nuevo porque las rutas de Docker, journal y Loki requieren migraciones coordinadas. El valor se establecerá en 5 GiB por host, con `project` y cuotas de filesystem habilitados únicamente después de probar la operación en una imagen/VM descartable. La prueba local mostró que un escritor con `CAP_SYS_RESOURCE` puede superar la cuota; por tanto, no se desplegará este mecanismo hasta verificar que todos los escritores cubiertos carecen de esa capacidad o que otro control impide el bypass.
- **Gate de filesystem.** No asumir que la función puede activarse en línea. Documentar el procedimiento compatible con cada versión de ext4, probar remonte, reinicio, escritura excedente denegada y recuperación en entorno descartable. Si requiere desmontaje, `e2fsck`, reinicio o recuperación fuera de banda, no ejecutar hasta aprobación explícita de ventana, consola de recuperación y respaldo verificado por host. Si no puede garantizarse la cobertura agregada sin operación offline, mantener el despliegue bloqueado en vez de aplicar cuotas parciales.
- **Inventario antes de asignar cuota.** Revalidar paths y filesystems en vivo. Incluir `/var/log` (journal, syslog, audit y Sentinel), logs Docker `json-file`, volumen Loki y cualquier log identificado fuera de esos árboles. Evitar imponer el project ID a capas o datos Docker ajenos al alcance; si un montaje compartido impide aislar Loki, rediseñar la ruta de persistencia primero. La cuota representa bloques asignados por el filesystem, no un recuento idéntico al tamaño lógico de archivos.
- **Controles por fuente.** Añadir límites/rotación en journald, rsyslog/logrotate y Docker como defensa adicional y para mantener historial útil, no como prueba del techo total. Mantener retención temporal de Loki junto a la cuota física.
- **Filtrado en origen.** Aplicar reglas por fuente antes de la escritura remota a Loki. Solo clasificaciones de seguridad/error verificadas pasan; eventos sin nivel o parseo verificable se excluyen del envío remoto. Los datos locales siguen la política local; el CSV de Kingu no se envía ni rota hasta definir retención y verificar un respaldo.
- **Separación de alcance DMZ.** `hercules` y `ocean` se tratan exclusivamente como hosts DNS externos para esta política del sistema operativo: no cambiar su DNS, AD, firewall ni instalar/modificar Sentinel.

## Risks / Trade-offs

- [La extensión `project` o cuotas requiere mantenimiento offline] → probar en entorno descartable; bloquear cambios reales hasta autorización específica, backup y recuperación fuera de banda.
- [Una ruta nueva o un archivo recreado no hereda el project ID] → validar herencia tras recreaciones de contenedor, reinicio y rotación; auditar periódicamente todas las rutas con `stat`/herramientas de cuota antes de declarar el límite efectivo.
- [Compartir proyecto con datos no-log hace que consuman el límite] → aislar el volumen Loki/rutas Docker pertinentes; detenerse si el límite afectaría datos fuera del alcance.
- [Cuota llena impide nuevas escrituras] → elegir presupuestos/retención por fuente y verificar comportamiento; mantener margen de filesystem ajeno a la cuota para operación del host.
- [Clasificación inconsistente omite errores o envía ruido] → probar muestras reales por fuente, rechazar por defecto eventos no clasificados y medir bytes enviados antes/después.
- [Rotar el CSV altera datos de Sentinel] → investigar el proceso escritor, respaldar y verificar restauración, y no truncar hasta aprobar explícitamente la retención.

## Migration Plan

1. Completar OpenSpec y agregar tarea operativa explícita que permita únicamente límites de logs en los seis hosts, preservando las exclusiones de AD/DNS/firewall/Sentinel en la DMZ.
2. Preflight de solo lectura en cada host: branch/estado, conectividad, servicios, uso y filesystem, rutas abiertas, espacio disponible y política de recuperación. Cuantificar transferencia a Loki; anotar que la facturación no se verificó.
3. Preparar y probar en VM descartable la asignación de cuotas a un ID común, herencia, reinicio, fallo al superar 5 GiB y restauración. Validar cobertura del árbol de logs frente a rutas reales.
4. Si el gate de filesystem requiere cambio offline, detener el flujo de despliegue y solicitar autorización específica para ventana y recuperación. Sin ese permiso, no presentar el límite duro como desplegado.
5. Con gates aprobados, desplegar un host piloto, validar sistema y servicios, observar cuota y egreso; después avanzar nodo por nodo con respaldo y rollback configurado antes de cada cambio.
6. Rollback: restaurar configuraciones previas y rutas desde respaldos; no desactivar/retirar cuota si eso permite crecimiento sin límite; no borrar datos de logs o CSV como parte de la reversión.
7. Registrar preparación, pruebas y despliegue real por separado en el repositorio y vault.

## Open Questions

- ¿La prueba en entorno descartable demuestra que la capacidad actual de ext4 permite habilitar `project` sin una intervención offline? Esta respuesta puede resolverse en la fase de diseño/prueba; una respuesta negativa bloquea el despliegue hasta la autorización definida arriba.
- ¿Qué retención se aprobará para el CSV de Kingu? Hasta resolverla, se mantiene íntegro y no se incluye en una rotación destructiva.
