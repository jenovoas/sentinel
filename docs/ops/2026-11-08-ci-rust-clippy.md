# 2026-11-08 — Corrección del fallo de Rust CI (clippy / candado YATRA)

## Estado

- **Preparación local completada. NO desplegado, NO subido a GitHub.** El CI de GitHub
  seguirá en rojo hasta que estos cambios se confirmen (commit) y se publiquen (push).
- Verificación en GitHub pendiente: confirmar que `Rust CI` pasa en `main` tras el push.

## Síntoma

`Rust CI` fallaba en cada push a `main` (runs 42415559798, 42416420164, 42417173214,
42436748841). Paso que fallaba: `cargo clippy --all -- -D warnings`.

## Causa raíz

- `sentinel-cortex/src/lib.rs` hacía `#![allow(clippy::cast_possible_truncation,
  cast_precision_loss, float_arithmetic)]`, pero `sentinel-cortex/Cargo.toml`
  (`[lints.clippy]`) los declara `forbid` → error `E0453` (allow incompatible con forbid).
- Al corregirlo, afloraron 26 errores reales de casts con truncamiento y aritmética `f64`
  que el `allow` ocultaba, más avisos (`dead_code`, `Default`, `is_multiple_of`, etc.).

## Cambios (sin relajar el `forbid` de Cargo.toml)

- Eliminado el `allow` de `lib.rs`; casts reemplazados por `try_from` con saturación
  (nuevo helper `math::s60::saturating_i64`) o enmascarado explícito donde el wrapping
  es intencional (`token_id` de semilla fractal).
- `/metrics`: temperatura y `retention_score` ahora en entero escalado
  (`retention_score_x10k`, `fmt_fixed`), mismo formato de salida (`{:.2}` / `{:.4}`).
  Redondeo al más cercano; sin `f64`.
- `bin/certify_s60.rs`: retirada la mitad `f64` de la comparación (prohibida por YATRA).
  Las comparaciones de drift IEEE-754 siguen en los prototipos Python (`quantum/experiments`).
- Constantes `DTC_CLOCK_*` conservadas con `#[allow(dead_code)]` (contrato SHM reservado,
  ver `docs/AUDITORIA_DESPLIEGUE_MULTINODO_2026-10-30.md`).
- `truthsync-core/Cargo.toml`: eliminado el `[[bench]]` duplicado que apuntaba al mismo
  archivo que el `[[bin]]` (aviso de manifiesto).

## Evidencia (ejecutada en local, 2026-11-08)

| Comprobación | Resultado |
|---|---|
| `cargo clippy --all -- -D warnings` | sin errores ni avisos |
| `cargo fmt --all -- --check` | OK |
| `CARGO_PROFILE_RELEASE_PANIC=unwind cargo test --all --release` | todo en verde (129 + 64 + resto, 0 fallos) |
| `cargo deny check` | advisories/bans/licenses/sources ok |
| `cargo audit --deny warnings` | **no ejecutado**: `cargo-audit` no instalado en local (el CI lo instala) |

## Pendiente / riesgos

- Ejecutar `cargo audit` (solo lo corre el CI).
- Cambio de comportamiento menor: conversiones que antes truncaban en silencio ahora
  saturan; el redondeo de las métricas es al más cercano y puede diferir del `f64` en el
  último decimal en casos límite.
- Alertas de seguridad en GitHub: code scanning y Dependabot sin alertas abiertas al
  momento de la revisión.
