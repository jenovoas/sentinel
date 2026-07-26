# Tarea: Sincronización de Repositorio GitHub (Fenix/Sentinel)

## Estado Inicial
- La rama `main` local y `origin/main` han divergido.
- Local tiene 3 commits nuevos (incluyendo implementación eBPF LSM).
- Remoto tiene 1 commit de Merge PR (#36 Performance Metrics).
- Hay archivos modificados no rastreados (`backend/logs/sentinel.log`).

## Plan de Acción
- [x] Guardar cambios locales temporales (logs) con `git stash` o ignorarlos si no son necesarios.
- [x] Realizar un rebase interactivo o `git pull --rebase origin main` para alinear los historiales y mantener una línea pura evitando 'merge commits' ruidosos.
- [x] Resolver conflictos si existieran durante el rebase.
- [x] Sincronizar (push) los cambios locales ahora alineados hacia `origin/main`.
- [x] Restaurar cualquier archivo desde stash si fue guardado.

## Notas de Operación (YATRA)
- Minimizar el impacto: los logs modificados en `backend/logs/` usualmente no deberían trackearse o son efímeros.
- Mantener la limpieza del historial.

## Tarea: Diagnóstico de Warnings en Contenedores Sentinel

## Estado Inicial
- El usuario reporta warnings en los contenedores `sentinel_nginx` y `sentinel_backend`.
- Visualización en IDE confirma iconos de advertencia.

## Plan de Acción
- [x] Ejecutar `podman ps --all` para verificar estados y salud de los contenedores.
- [x] Inspeccionar logs de `sentinel_nginx` para identificar errores de inicio o configuración.
- [x] Inspeccionar logs de `sentinel_backend` para identificar errores de ejecución o fallos de salud.
- [x] Verificar estados de salud (`HealthStatus`) y causas de reinicio.
- [x] Aplicar correcciones siguiendo principios de "Impacto Mínimo" (ej. flags `:z` de SELinux si aplica).
- [x] Verificar empíricamente la resolución de los warnings.

## Notas de Operación (YATRA)
- OBLIGATORIO: No reiniciar servicios de SLA (Traefik, PinguinoSeguro) a menos que sea estrictamente necesario.
- Verificar si el problema es de permisos (SELinux) según lecciones aprendidas.

## Tarea: Persistencia de Configuración tras Reinicio (Sentinel)

## Estado Inicial
- Las correcciones manuales funcionan, pero se pierden o fallan tras reiniciar el servidor.
- Los servicios de systemd para Sentinel están en estado `failed`.
- Podman no está recreando los contenedores con las configuraciones corregidas automáticamente.

## Plan de Acción
- [x] Reconstruir las imágenes de `backend` y `nginx` para asegurar que los cambios de código y upstream estén integrados.
- [x] Validar que la pila completa levante correctamente con `podman-compose up -d`.
- [x] Generar nuevos archivos de unidad systemd para los contenedores corregidos (`podman generate systemd`).
- [x] Actualizar las unidades en `~/.config/systemd/user/`.
- [x] Recargar systemd y habilitar los servicios para inicio automático.
- [x] Verificar persistencia simulando una parada/arranque vía systemd.

## Notas de Operación (YATRA)
- OBLIGATORIO: No purgar volúmenes de datos (`postgres_data`, `redis_data`).
- Asegurar que el archivo `.env` sea accesible por las unidades de systemd.
## Tarea: Restauración de Especificación de Hardware S60

## Estado Inicial
- El documento `docs/S60_HARDWARE_SPEC.md` había sido eliminado en un commit anterior.
- Tras auditar el historial de Git, fue recuperado desde el commit `76c17070` y se encuentra staged.

## Plan de Acción
- [x] Auditar e identificar el commit con la versión pura de `docs/S60_HARDWARE_SPEC.md`.
- [x] Restaurar el archivo al directorio de trabajo.
- [x] Realizar commit y push de `docs/S60_HARDWARE_SPEC.md`.
- [x] Verificar empíricamente que el estado de Git quede limpio.

## Notas de Operación (YATRA)
- Documentación preservada según especificación de arquitectura Sovereign S60.

## Tarea: Limpieza de Skills y MCP para Economía de Tokens

## Estado Inicial
- En `~/.gemini/config/skills/` existen 26 habilidades (Skills) de GCP/DataCloud (BigQuery, Dataflow, Composer, Dataproc, dbt, Lakehouse, etc.) inyectando miles de tokens en el prompt global en cada turno.
- En `~/.gemini/config/mcp_config.json` hay 3 servidores MCP (`notebooks`, `visualization`, `context`).
- En `~/.gemini/config/plugins/` existe 1 plugin (`googlecloudtools.datacloud_telemetry`).

## Plan de Acción
- [x] Auditar inventario completo de skills, plugins y servidores MCP activos.
- [x] Trasladar skills de GCP no relacionados con Sentinel a `~/.gemini/config/skills_disabled/` (conservando solo `accidental-data-loss-prevention`, `managing-python-dependencies`, `skill-repair` y `react-doctor`).
- [x] Desactivar/desplazar plugin `googlecloudtools.datacloud_telemetry` a `~/.gemini/config/plugins_disabled/`.
- [x] Respaldar y deshabilitar/limpiar servidores MCP innecesarios en `~/.gemini/config/mcp_config.json`.
- [x] Validar que la estructura quede limpia y documentar el ahorro de tokens generado.

- [x] Removidos esquemas y servidor MCP de `notebooks` (junto con `visualization` y `context`) hacia `~/.gemini/antigravity-ide/mcp_disabled/`.

## Notas de Operación (YATRA)
- Mantener copia de seguridad en `_disabled` para fácil restauración si se requiere en el futuro.
- Preservar las skills del workspace (`.agents/skills/react-doctor`).
