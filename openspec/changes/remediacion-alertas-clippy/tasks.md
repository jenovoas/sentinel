# Tasks

## 1. Conversiones enteras seguras

- [ ] 1.1 Reemplazar los casts enteros señalados por Clippy en los módulos de medición, lattice, DSP, física orbital y scheduler; verificar con pruebas de límites y `cargo clippy -p me60os --lib -- -D warnings`.
- [ ] 1.2 Revisar cada conversión SPA `i128 → i64` y elegir error, límite o fallo explícito según el contrato; verificar con pruebas de valores representables y desbordados.
- [ ] 1.3 Corregir casts bajo `cfg(test)` y ejecutar `cargo test -p me60os --lib`.

## 2. Eliminar floats de las APIs del core

- [ ] 2.1 Sustituir el importador decimal `f64` por una entrada entera escalada y retirar aliases PyO3 flotantes; verificar conversión exacta y búsqueda sin referencias Rust activas a esa API.
- [x] 2.2 Migrar el scheduler SOMA a tiempo/duración enteros y eficiencia de razón entera; verificar escenarios de ventana, tiempo monotónico y eficiencia 0/100 %.
- [x] 2.3 Migrar el detector SOMA a métricas enteras con escalas declaradas, estadística y umbrales sin float; verificar límites y detección contra casos de referencia.
- [x] 2.4 Actualizar los callers Python afectados y añadir pruebas de integración de unidad/escala en las fronteras; verificar los tests Python pertinentes y carga del módulo PyO3.

## 3. Verificación integrada y registro

- [x] 3.1 Ejecutar `cargo clippy -p me60os --all-targets --all-features -- -D warnings`, `cargo test -p me60os --all-targets --all-features` y `git diff --check`; registrar y resolver cada fallo sin relajar lints.
- [ ] 3.2 Ejecutar la validación OpenSpec y documentar el cambio y la evidencia observada en Sentinel y `personalvault`, distinguiendo validación local de cualquier despliegue.

## Evidencia de ejecución — 2026-11-03

- Estado: cambios locales en el árbol de trabajo; sin commit, push ni despliegue.
- `cargo fmt -p me60os -- --check`, `cargo clippy -p me60os --all-targets --all-features -- -D warnings` y `cargo test -p me60os --all-targets --all-features`: pasaron; 109 pruebas de biblioteca y las pruebas disponibles de los binarios.
- La extensión PyO3 se compiló con `backend/.venv/bin/python`; `backend/tests/test_soma_migration.py` pasó (1 prueba), y se verificaron desde Python las llamadas a `phi`, `phi_now`, `is_portal_open`, tamaño adaptativo y espera al portal.
- `openspec validate remediacion-alertas-clippy --strict` y `git diff --check`: pasaron. La inspección de `me-60os-core/src/soma` no encontró firmas ni operaciones float.
- Pendiente: cerrar tareas 1.1–1.3 y 2.1 contra sus pruebas de límites, completar el registro externo de vault en 3.2 y revalidar las alertas remotas/de correo; no se han silenciado ni resuelto alertas en GitHub.

## Workflow follow-up

- Archivar el cambio OpenSpec cuando la implementación y sus verificaciones estén completas.
