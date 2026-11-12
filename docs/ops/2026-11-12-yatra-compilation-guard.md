# Candado YATRA en la compilación Rust — 2026-11-12

## Regla

Los crates Rust del workspace Sentinel solo usan aritmética entera escalada SPA/S60 o SPAMath. Los tipos `f32`, `f64` y literales de punto flotante en código Rust bloquean la compilación. La revisión cubre fuentes, pruebas, binarios, ejemplos y `build.rs` de todos los miembros del espacio de trabajo, incluidos los tokens de macros.

## Implementación

- `scripts/yatra_build_guard.rs` recorre los miembros declarados en `Cargo.toml`, analiza cada `.rs` con `syn` e inspecciona rutas de tipos y expresiones, literales y tokens de macros.
- Cada crate incorpora el guard mediante su `build.rs`; por ello la verificación corre al compilar cualquier crate miembro con Cargo, aunque se solicite un único paquete.
- Los errores al enumerar, leer o analizar fuentes bloquean la compilación. Las reglas Clippy existentes (`float_arithmetic`, `float_cmp`, `cast_precision_loss`, `cast_possible_truncation`) continúan como `forbid` donde ya estaban declaradas.
- Se migraron los valores de punto flotante encontrados a SPA/S60 o enteros escalados. También se repararon las conversiones con truncamiento que hacían fallar Clippy y se movió `main` debajo del módulo de pruebas para resolver la regla de orden.

## Evidencia local

- `cargo check --workspace --all-targets` — aprobado.
- `cargo clippy --workspace --all-targets -- -D warnings` — aprobado.
- La primera compilación bajo la regla reportó valores de punto flotante existentes en varios módulos; tras migrarlos, la pasada completa terminó sin infracciones.
- Commit publicado en `main`: `0b3c3339` (`fix(yatra): bloquear punto flotante en compilaciones`). Rust CI `43173162425`, CodeQL `43173162435`, eBPF Build CI y React Doctor aprobaron para ese SHA.
- Desplegado en Fénix el 2026-11-12: checkout limpio `main` `5d229625` (código YATRA `0b3c3339`), imagen `sentinel-cortex:5d229625`, ID `sha256:9eea45299ec4d9ddbf9ea7846e044b746d77948d2c80e69f64850d697ef4dc06`. Se actualizó solo Cortex; respaldo de `/etc/sentinel/backend.env` en `/etc/sentinel/backend.env.pre-yatra-redeploy-20261112T080034Z`. Compose validado antes/después; contenedor `healthy`, `/health` 200, QHC conectado/no stale, restauró checkpoint (67.951 nodos), MyCNet WebSocket 101 y métricas de lattice crecientes. Imagen anterior `sentinel-cortex:gap-real-20261105` conservada.
- Incidente de pulso resuelto: `CrystalRuntime` rechazaba el encabezado legado `0x000000015346528c` de `/dev/shm/me60os_fractal_seeds`, por lo que el worker no iniciaba, el canal de entrada se desconectaba y el PULSE CHECK caía al reloj QHC con energía cero. Commit `7b107e72` normaliza solo el magic tras validar versión/cursor y conservar `head`/`tail`; también deja errores del worker en el journal. Desplegado solo Cortex en Fénix como `sentinel-cortex:7b107e72` (ID `sha256:131c965b18172fe6da9817c0ec73da0b36cc86ad84b268e7dfbc50900b49aadc`), backup `/etc/sentinel/backend.env.pre-cortex-uplink-20261112T094217Z`. Verificación: `running/healthy`, `dtc_ticks=2959`, QHC conectado/fresco, y tres `PULSE CHECK Valid=true, Coherence=Unison raw=12960000` con `PROCESSOR RESULT: True`. Detalle: [recuperación del pulso CrystalRuntime](crystal-runtime-pulse-fix-2026-11-12.md).

## Historial YATRA revisado

- `e4853550`: introdujo la prohibición de floats en el workspace.
- `77b6ccc7`: endureció los lints Clippy del workspace.
- `27b9c013`: debilitó `float_arithmetic` y permitió `cast_precision_loss`.
- `9bc17afe`: restauró la prohibición el 2026-11-02.
- `9025dca8`: corrigió Clippy sin debilitar YATRA.

El historial confirma una relajación y su restauración posterior; no permite inferir intención de sabotaje.

## Alcance

La regla cubre las compilaciones Cargo de estos crates y detecta tokens de punto flotante en las fuentes del espacio de trabajo. No modifica el binario global `rustc` ni inspecciona código generado internamente por macros de dependencias externas.
