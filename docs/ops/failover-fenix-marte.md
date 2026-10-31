# Procedimiento de promoción y failback Fenix ↔ Marte — `agente:infra-ha`

> Estado 2026-10-31: procedimiento escrito y validado en seco. Ensayo real de promoción pendiente de ventana autorizada. NO ejecutar fuera de ventana: la promoción es disruptiva (split-brain si Fenix sigue escribiendo).

## Topología

| Rol | Nodo | PostgreSQL | Redis | Backend |
| --- | --- | --- | --- | --- |
| Primario | Fenix `10.88.0.1` | `sentinel-postgres` escritura | `sentinel-redis` escritura | `sentinel-backend` puerto WG 8000 |
| Espera | Marte `10.88.0.6` | `sentinel-postgres-standby` streaming | `sentinel-redis-replica` réplica | `sentinel-backend-standby` loopback, health 503 esperado |

## Precondiciones de promoción (Fenix → Marte)

1. Fenix declarado caído o degradado por Jaime. Si Fenix sigue escribiendo, detener escrituras primero (detener `sentinel-backend` en Fenix) para evitar split-brain.
2. Standby PostgreSQL al día: `pg_stat_replication` en Fenix con `flush_lsn` cercano, o si Fenix está caído, aceptar pérdida async documentando el último WAL recibido (`pg_last_wal_receive_lsn()` en Marte).
3. Réplica Redis al día: `master_link_status:up`, `lag=0` en el último dato conocido.

## Promoción a Marte (comandos exactos)

```sh
# 1. Detener escrituras en Fenix (si Fenix responde).
sudo -n docker stop sentinel-backend

# 2. Promover PostgreSQL standby a primaria (en Marte; usar POSTGRES_USER/PASSWORD de /etc/sentinel/backend-standby.env).
PW=$(sudo -n grep '^POSTGRES_PASSWORD=' /etc/sentinel/backend-standby.env | cut -d= -f2-)
USER=$(sudo -n grep '^POSTGRES_USER=' /etc/sentinel/backend-standby.env | cut -d= -f2-)
sudo -n docker exec -e PGPASSWORD="$PW" sentinel-postgres-standby psql -h 127.0.0.1 -U "$USER" -d sentinel_db -c "SELECT pg_promote();"
# Verificar: pg_is_in_recovery() = false.

# 3. Promover Redis réplica a maestra (en Marte).
sudo -n docker exec sentinel-redis-replica redis-cli REPLICAOF NO ONE

# 4. Reapuntar backend standby a primaria local y publicar WG (en Marte).
# Editar /etc/sentinel/backend-standby.env:
#   DATABASE_URL → postgresql+asyncpg://USER:PASS@10.88.0.6:5432/DB
#   REDIS_URL/SENTINEL_REDIS_URL → redis://10.88.0.6:6379 (ya es local)
sudo -n docker rm -f sentinel-backend-standby
sudo -n docker run -d --name sentinel-backend-standby --network host \
  --env-file /etc/sentinel/backend-standby.env \
  --add-host postgres:10.88.0.6 --add-host redis:10.88.0.6 \
  -p 10.88.0.6:8000:8000 --restart unless-stopped --memory 768m \
  sentinel-backend:dd532f7a-gamma-review-1
# Verificar: GET http://10.88.0.6:8000/api/v1/health → 200.
# 5. Redirigir tráfico: en Kingu, nginx es el frontal (no hay Traefik activo).
#    Cambiar en el server sentinel.pinguinoseguro.cl:
#      `proxy_pass http://10.88.0.1:8001` → `http://10.88.0.6:8000`
#    (telemetría apunta a Cortex 8001 en Fenix; el backend promovido escucha en 8000).
#    `sudo -n nginx -t && sudo -n systemctl reload nginx`.
#    DNS no cambia: sentinel/dns1/dns2 apuntan a la IP pública de Kingu (64.176.8.191).
```

## Failback a Fenix (vuelta)

# 1. Detener escrituras en Marte.
# 2. pg_basebackup nuevo desde Marte hacia Fenix (Fenix como standby),
#    o restore del backup diario + rebuildeo de réplica.
# 3. Redis en Fenix como réplica de Marte (REPLICAOF 10.88.0.6 6379),
#    luego promover según el mismo esquema.
# 4. Backend Fenix a primaria, backend Marte a espera (quitar -p WG).
# 5. Nginx de vuelta a 10.88.0.1 + reload.
```

## Ensayo 2026-10-31 ~07:13–07:17 UTC (ventana autorizada, sin servicios en producción)

- Promoción Marte: LSN recibido `0/822D420` = LSN primario, **pérdida cero**.
- `pg_promote=t`, escritura OK, Redis `role:master`, backend Marte `healthy/is_primary:true`.
- Failback Fenix: basebackup inverso, Fenix primaria timeline 3, Marte reconstruido como standby (streaming timeline 3), Redis re-esclavizado (`up`), backend Fenix 200, backend Marte 503 (espera).
- Tablas y claves de ensayo eliminadas en ambos extremos.
- Lección: el contenedor return necesita red con salida (`monitoring_exposure`, no `internal`) y el slot debe crearse en la primaria vigente de cada timeline.

## RPO/RTO estimados (no medidos)

- RPO: segundos (async) salvo caída súbita: últimas transacciones no replicadas.
- RTO: minutos (promoción manual). Sin automatización hasta ensayo + alertas.

## Registro obligatorio

Cada promoción/failback real: fecha, causa, LSN último replicado, pérdida estimada, verificaciones y commit de actualización de este documento.
