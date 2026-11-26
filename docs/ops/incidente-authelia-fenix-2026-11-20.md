# Incidente de Authelia en Fénix — 2026-11-20

Authelia fallaba durante la comprobación LDAPS a `10.88.0.1:636` y Docker lo reiniciaba. `ip route get 172.19.0.3` seleccionaba `br-cbd16f207701`, un puente caído sin interfaces conectadas y ausente del inventario de redes de Docker.

Se retiró en vivo la dirección duplicada `172.19.0.1/16` del puente caído. La ruta pasó a `br-1b8eeb2333da`, se comprobó TCP 636 desde la red de Docker y Authelia volvió a arrancar por su política automática. A las 23:23:30 UTC completó el arranque. Después Docker informó estado saludable con el contador en 577 y `/api/health` respondió HTTP 200.

## Recurrencia y corrección persistente — 2026-11-26

**Recurrencia.** El servidor se reinició el 2026-11-23 01:51 y Docker arrancó a las 01:52. Restauró el puente `br-cbd16f207701` con `172.19.0.1/16`, duplicado de `br-1b8eeb2333da`. `ip route get 172.19.0.2` salía por el puente caído y Authelia fallaba con `no route to host` hacia `10.88.0.1:636`: 4891 reinicios hasta la corrección.

**Alivio en vivo.** Jaime ejecutó `ip addr del 172.19.0.1/16 dev br-cbd16f207701`. Ruta por `br-1b8eeb2333da`, `10.88.0.1:636` abierto desde la red Docker y Authelia arrancó.

**Corrección persistente (realizada).** Con `live-restore: true`, que mantiene los contenedores vivos con el demonio parado:
1. Se compiló `bbolt` y una herramienta mínima de borrado en un contenedor `golang` temporal, y se probó el borrado sobre una copia (149 → 148 claves, `bbolt check` OK, 0 claves `cbd16f`). `bbolt` no incluye subcomando `delete`.
2. `systemctl stop docker.socket docker`; respaldo `/var/lib/docker/network/files/local-kv.db.bak-2026-11-26-cbd16f`; borrado de la única clave `docker/network/v1.0/bridge/cbd16f207701…/` (huérfana: sin `network/<id>/` asociado); `bbolt check` OK; `systemctl start docker`.
3. `ip link del br-cbd16f207701` (interfaz huérfana).
4. Segundo `systemctl restart docker`: el puente no reapareció; 24/24 contenedores; Authelia `healthy`; ruta por `br-1b8eeb2333da`; `10.88.0.1:636` abierto.

**Verificación final.** El reinicio completo del 2026-11-26 22:59 UTC quedó verificado (el puente no reapareció, 24/24 contenedores, Authelia `healthy`). El respaldo `local-kv.db.bak-2026-11-26-cbd16f` se eliminó después, por lo que ya no hay vuelta atrás por esa vía.

Nota del 2026-11-20 (histórica): corrección persistente pendiente. Una lectura de las páginas activas de la base local de redes de Docker confirmó la entrada del controlador `docker/network/v1.0/bridge/cbd16f207701a6124441680818c895f8d03dec469aed3e552b58c6f6d647b42b/`. Moby restaura estas entradas al iniciar. Para retomar, verificar la clave y la ruta, y coordinar la limpieza de los metadatos con Docker detenido durante una ventana autorizada. La base de Docker no fue modificada.
