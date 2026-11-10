# Tasks

## 1. Conversiones enteras seguras

- [x] 1.1 Reemplazar los casts enteros señalados por Clippy en los módulos de medición, lattice, DSP, física orbital y scheduler; DSP conserva ampliaciones exactas y límites comprobados. Verificado con pruebas de límites y Clippy estricto.
- [x] 1.2 Revisar las conversiones SPA `i128 → i64`: `Mul`/`Div` saturan según el contrato previo; `to_raw` falla explícitamente y `div_safe` devuelve `SPAError::Overflow`. Verificados valores representables y desbordados.
- [x] 1.3 Corregir el cast bajo `cfg(test)` y ejecutar `cargo test -p me60os --lib`.

## 2. Eliminar floats de las APIs del core

- [x] 2.1 Auditar el importador decimal `f64` y aliases PyO3: no existen en el Rust activo, por lo que no se requiere migración ni caller nuevo. La entrada S60 existente conserva exactamente los enteros; verificación de roundtrip y límites en `spa.rs`.
- [x] 2.2 Migrar el scheduler SOMA a tiempo/duración enteros y eficiencia de razón entera; verificar escenarios de ventana, tiempo monotónico y eficiencia 0/100 %.
- [x] 2.3 Migrar el detector SOMA a métricas enteras con escalas declaradas, estadística y umbrales sin float; verificar límites y detección contra casos de referencia.
- [x] 2.4 Actualizar los callers Python afectados y añadir pruebas de integración de unidad/escala en las fronteras; verificar los tests Python pertinentes y carga del módulo PyO3.

## 3. Verificación integrada y registro

- [x] 3.1 Ejecutar `cargo clippy -p me60os --all-targets --all-features -- -D warnings`, `cargo test -p me60os --all-targets --all-features` y `git diff --check`; registrar y resolver cada fallo sin relajar lints.
- [x] 3.2 Ejecutar `openspec validate remediacion-alertas-clippy --strict` y documentar los cambios y evidencia local en Sentinel y `personalvault`, distinguiéndolos de cualquier despliegue.

## Evidencia de ejecución — 2026-11-03

- Estado: cambios locales en el árbol de trabajo; sin commit, push ni despliegue.
- `cargo fmt -p me60os -- --check`, `cargo clippy -p me60os --all-targets --all-features -- -D warnings` y `cargo test -p me60os --all-targets --all-features`: pasaron; 109 pruebas de biblioteca y las pruebas disponibles de los binarios.
- La extensión PyO3 se compiló con `backend/.venv/bin/python`; `backend/tests/test_soma_migration.py` pasó (1 prueba), y se verificaron desde Python las llamadas a `phi`, `phi_now`, `is_portal_open`, tamaño adaptativo y espera al portal.
- `openspec validate remediacion-alertas-clippy --strict` y `git diff --check`: pasaron. La inspección de `me-60os-core/src/soma` no encontró firmas ni operaciones float.
- Pendiente: cerrar tareas 1.1–1.3 y 2.1 contra sus pruebas de límites, completar el registro externo de vault en 3.2 y revalidar las alertas remotas/de correo; no se han silenciado ni resuelto alertas en GitHub.

## Verificación local — 2026-11-10

- `cargo fmt -p me60os -- --check`: pasó.
- `cargo test -p me60os --lib`: 133 pruebas aprobadas.
- `cargo clippy -p me60os --lib --tests -- -D warnings`: pasó.
- Pruebas de límites añadidas para sector `u8` (0/255), roundtrip SPA `i64::MIN/MAX`, saturación de `Mul`/`Div`, overflow de `div_safe` y fallo explícito de `to_raw`.
- El cast `i as i64` del test de `buffer.rs` se sustituyó por `i64::from(i)`.
- Sin commit, push ni despliegue. 2.1 se cerró tras confirmar ausencia del importador/aliases objetivo y verificar el contrato entero existente; quedan usos `f64`/`f32` de bins fuera de esa API y no se modificaron. 3.2 quedó documentada en `Pendientes.md`; la validación OpenSpec estricta y `git diff --check` pasaron.

## Workflow follow-up

- Archivar el cambio OpenSpec cuando la implementación y sus verificaciones estén completas.
