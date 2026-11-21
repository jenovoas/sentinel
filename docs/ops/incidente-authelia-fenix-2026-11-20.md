# Incidente de Authelia en Fénix — 2026-11-20

Authelia fallaba durante la comprobación LDAPS a `10.88.0.1:636` y Docker lo reiniciaba. `ip route get 172.19.0.3` seleccionaba `br-cbd16f207701`, un puente caído sin interfaces conectadas y ausente del inventario de redes de Docker.

Se retiró en vivo la dirección duplicada `172.19.0.1/16` del puente caído. La ruta pasó a `br-1b8eeb2333da`, se comprobó TCP 636 desde la red de Docker y Authelia volvió a arrancar por su política automática. A las 23:23:30 UTC completó el arranque. Después Docker informó estado saludable con el contador en 577 y `/api/health` respondió HTTP 200.

Corrección persistente pendiente. Una lectura de las páginas activas de la base local de redes de Docker confirmó la entrada del controlador `docker/network/v1.0/bridge/cbd16f207701a6124441680818c895f8d03dec469aed3e552b58c6f6d647b42b/`. Moby restaura estas entradas al iniciar. Para retomar, verificar la clave y la ruta, y coordinar la limpieza de los metadatos con Docker detenido durante una ventana autorizada. La base de Docker no fue modificada.
