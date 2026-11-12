# Recuperación del pulso de CrystalRuntime — 2026-11-12

## Evidencia previa al cambio

- En Fénix, `PULSE CHECK` se mantuvo en `Valid=false`, `Coherence=False raw=0` durante toda la ventana observada. `/health` informó `dtc_ticks=0`, energía del cristal `0` y QHC conectado.
- MyCNet registró `CrystalRuntime input channel disconnected`, señal de que el receptor del worker había terminado.
- El checkpoint de dos lanes sí se restauró: 67.951 nodos, tick guardado 47.350.973.
- El encabezado de `/dev/shm/me60os_fractal_seeds` en Fénix era `0x000000015346528c` (versión 1); el inicializador solo aceptaba `0x0000000153465231` (`SFR1`) o cero y devolvía error para el valor observado. El error de inicio se almacenaba en el endpoint autenticado, sin aparecer en el journal.

## Cambio local

- `CrystalRuntime` reconoce el encabezado legado exacto observado, verifica que `tail <= head`, normaliza únicamente el campo `magic` y conserva los cursores del ring.
- Los errores de inicialización, tick DTC, paso del cristal y cierre inesperado del canal se registran en el journal para que una futura caída no quede invisible.
- No se alteró la aritmética SPA/S60 ni se introdujeron tipos o literales de punto flotante.
- Validación local: `cargo check -p sentinel-cortex --bin sentinel-cortex` terminó correctamente; `git diff --check` sin errores.

## Estado operativo

- Preparación local: validada con `cargo check -p sentinel-cortex --bin sentinel-cortex` y `git diff --check`.
- Publicación: commit `7b107e72` en `main`, `origin/main`.
- Despliegue realizado en Fénix: imagen `sentinel-cortex:7b107e72`, ID `sha256:131c965b18172fe6da9817c0ec73da0b36cc86ad84b268e7dfbc50900b49aadc`. Se respaldó `/etc/sentinel/backend.env` en `/etc/sentinel/backend.env.pre-cortex-uplink-20261112T094217Z`; Compose se validó y se recreó solo Cortex.
- El journal confirmó la migración del encabezado con `head=13956761`, `tail=0`, luego `CrystalRuntime activo` con 67.951 nodos y MyCNet WebSocket 101.
- Aceptación en vivo: tres pulsos sucesivos `Valid=true`, `Coherence=Unison raw=12960000` a las 09:42:57, 09:43:23 y 09:43:34 UTC; cada uno produjo `PROCESSOR RESULT: True`. `/health` devolvió HTTP 200, contenedor `running/healthy`, `restarts=0`, `dtc_ticks=2959`, energía `lattice_energy_raw=605207215710`, QHC `connected=true` y `stale=false`.
