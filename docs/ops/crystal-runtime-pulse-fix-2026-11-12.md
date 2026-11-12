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

- Preparación local: cambio compilado; despliegue pendiente.
- Despliegue realizado: pendiente.
- Aceptación pendiente: `CrystalRuntime` activo, `dtc_ticks` avanzando, energía de lanes observada y `PULSE CHECK Valid=true` en logs posteriores al reinicio.
