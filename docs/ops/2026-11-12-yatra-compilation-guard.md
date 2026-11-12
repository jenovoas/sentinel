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
- Commit publicado en `main`: `0b3c3339` (`fix(yatra): bloquear punto flotante en compilaciones`). `Rust CI` `43173162425` está en ejecución; eBPF Build CI y React Doctor aprobaron.
- No se ha desplegado. El preflight requerido detectó `hercules` inaccesible por SSH en los puertos 4222 y 22; el procedimiento estándar §3 ordena detenerse si falla cualquier preflight. No se modificó ningún servicio.

## Historial YATRA revisado

- `e4853550`: introdujo la prohibición de floats en el workspace.
- `77b6ccc7`: endureció los lints Clippy del workspace.
- `27b9c013`: debilitó `float_arithmetic` y permitió `cast_precision_loss`.
- `9bc17afe`: restauró la prohibición el 2026-11-02.
- `9025dca8`: corrigió Clippy sin debilitar YATRA.

El historial confirma una relajación y su restauración posterior; no permite inferir intención de sabotaje.

## Alcance

La regla cubre las compilaciones Cargo de estos crates y detecta tokens de punto flotante en las fuentes del espacio de trabajo. No modifica el binario global `rustc` ni inspecciona código generado internamente por macros de dependencias externas.
