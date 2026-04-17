# Tarea: Reparación de Contenedores y Estabilización (Fenix)

## Estado Post-Diagnóstico
- `pinguinoseguro_db` ocupa el puerto 5432 (Host).
- `impacta_db` falla por colisión en puerto 5432.
- `impacta_redis` falla por falta de `redis.conf`.
- `pinguinoseguro_uptime` y `jaime-portfolio` salen con código 0.

## Plan de Acción
- [ ] Localizar y editar el `docker-compose.yml` de Impacta.
- [ ] Cambiar puerto externo de `impacta_db` (ej. 5433).
- [ ] Verificar existencia o crear `redis.conf` básico para `impacta_redis`.
- [ ] Investigar entrypoint de `pinguinoseguro_uptime` y `jaime-portfolio`.
- [ ] Aplicar cambios sin borrar volúmenes ni datos existentes.
- [ ] Reiniciar contenedores afectados y verificar estado `Up`.

## Notas de Operación
- **SLA Freeze**: No tocar nada de `pinguinoseguro.cl` que esté funcionando (web/db) a menos que sea estrictamente necesario.
- **Impacto Mínimo**: Solo modificar mapeos de puertos y archivos de configuración faltantes.
