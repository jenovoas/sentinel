# Plan de Remediación GH Dependabot — 117 Vulnerabilidades (2026-08-16)

> **Status:** Plan documentado. Ejecución diferida — sesión actual cerrada
> porque Jaime reinicia omniroute y los agentes caerán. Retomar en la
> próxima sesión.
>
> **Branch sobre la que se trabaja:** `feat/audit-360-remediation`
> (HEAD: `dd2d0f2e`, 1 commit ahead of origin, pyo3 0.29 ya pusheado)
>
> **Baseline de alertas:** `docs/03_audits/phase10-results/gh_dependabot_baseline_2026-08-16.json`
> (snapshot JSONL de los 117 alerts abiertos vía `gh api dependabot/alerts`)

---

## 1. Observación

`cargo audit` local + GitHub Dependabot en `main` reportan **117 alerts
abiertos** sobre la rama default:

| Severidad | Count |
|---|---|
| critical | 1 |
| high     | 46 |
| medium   | 43 |
| low      | 27 |
| **total** | **117** |

**Por paquete (deduped):**

```
openssl (rust-openssl)  32
next (Next.js)          21
rand (rust)              8
pyo3 (rust)              7   ← 2 cerrados en dd2d0f2e (RUSTSEC-2026-0177 & 0176)
bytes (rust)             6
fast-uri (npm)           5
python-multipart         5
postcss (npm)            4
pyjwt (python)           4
lru (rust)               4
tar                      3
ws (npm)                 2
python-dotenv            2
time (rust)              2
keccak (rust)            2
rsa (rust)               2   ← RUSTSEC-2023-0071, sin parche upstream
one-offs (1 c/u): extract-zip, nanoid, PyJWT, serde_with,
                  pydantic-settings, wee_alloc (CRITICAL), sqlx, glib
```

**Por manifest/lockfile:**

```
frontend/package.json:               21
sentinel-cortex/Cargo.lock:          16
src/sentinel-cortex/Cargo.lock:      14  (duplicado del workspace?)
pnpm-lock.yaml:                      13
me-60os-core/Cargo.lock:             13
backend/requirements.txt:            12
src/core/sentinel_core/forensics:    10
gui/src-tauri/Cargo.lock:             8
Cargo.lock:                           3
tools/sip-rs/Cargo.lock:              2
src/core/sentinel_core/init:          2
truthsync-core/Cargo.toml:            1
requirements.cortex.txt:              1
src/sentinel-wasm/Cargo.lock:         1
```

## 2. Hipótesis

De los 117 alerts, **~95-105 son cerrables con bumps de versión
estándar** y los **restantes requieren acción estructural**
(sin parche upstream, deprecación de paquete, etc.).

Estimación de cierre por fase:

| Fase | Vector | Alerts cerrables | Esfuerzo | Riesgo |
|---|---|---|---|---|
| A | Rust deps (cargo update) | ~53 | Bajo | Bajo |
| B | Python deps (pip-compile) | ~16 | Bajo | Bajo |
| C | Frontend npm (pnpm update) | ~38 | Medio | Medio (Next.js mayor) |
| D | Special cases (sin parche) | ~3-5 | Medio | Variable |
| E | Verificar + commit | — | Bajo | — |

**Cierre esperado al final:** 5-15 alerts residuales (rsa sin parche,
wee_alloc si no se puede desactivar, dependencias de Next.js que
requieran mig mayor).

## 3. Plan de ejecución

### Fase A — Rust deps (prioridad alta)
**Objetivo:** cerrar los 53 alerts en los 7 lockfiles Rust.

**Acciones:**
1. `cargo update --aggressive` en root workspace.
2. Bumps específicos en root `Cargo.toml` o workspace `[workspace.dependencies]`:
   - `openssl` → última 0.10.x
   - `lru` → 0.16.x (IterMut fix disponible en 0.16+)
   - `rand` → 0.9.x (la 0.9+ apaga el unsound con custom logger)
   - `bytes` → 1.10.x (fix integer overflow)
3. Re-correr `cargo update -p pyo3` si corre por separado — ya hecho en dd2d0f2e.
4. Validar: `cargo build --workspace --all-features` (no debe romper).
5. Verificar: `cargo audit --json | jq '.vulnerabilities.count'`.
6. Si algún crate del workspace no compila con el bump, hacer
   `cargo update -p <crate>@<version>` con pin conservador.

**Lockfiles a tocar:**
- `Cargo.lock` (raíz)
- `me-60os-core/Cargo.lock`
- `sentinel-cortex/Cargo.lock`
- `src/sentinel-cortex/Cargo.lock` (probable duplicado del workspace,
  investigar si se puede eliminar)
- `src/core/sentinel_core/forensics/Cargo.lock`
- `src/core/sentinel_core/init/Cargo.lock`
- `gui/src-tauri/Cargo.lock`
- `tools/sip-rs/Cargo.lock`
- `src/sentinel-wasm/Cargo.lock`
- `truthsync-core/Cargo.toml` (no lockfile propio, vive dentro del workspace)

**Resultado esperado:** 117 → ~64 alerts.

### Fase B — Python deps
**Objetivo:** cerrar los 16 alerts en los 2 requirements.

**Acciones:**
1. `pip-compile --upgrade backend/requirements.in` (si existe) o
   `pip install --upgrade ...` y re-pinear.
2. Bumps específicos:
   - `pyjwt` → 2.10.x (fix mixed families JWK/HMAC)
   - `python-multipart` → 0.0.20+ (fix DoS cuadrático)
   - `python-dotenv` → 1.1.x
   - `pydantic-settings` → 2.7+ (cubrir CVEs varios)
3. `pip-compile --upgrade requirements.cortex.txt` (mismo criterio).
4. Validar: `pip install -r backend/requirements.txt` en venv limpio
   y `python -c "import <mod>"` para cada uno.

**Resultado esperado:** 64 → ~48 alerts.

### Fase C — Frontend npm
**Objetivo:** cerrar los 38 alerts en `frontend/package.json` + `pnpm-lock.yaml`.

**Acciones:**
1. `cd frontend && pnpm update --latest` (no `--latest` por defecto,
   `--latest` fuerza majors).
2. Si Next.js pide mayor (15.x → 16.x), evaluar módulo por módulo:
   - Revisar `app/` para uso de Server Actions custom server (si lo hay)
   - Server-side rewrites (afecta a SSR)
   - DoS en App Router
3. Bumps específicos que pueden quedar:
   - `fast-uri` → 3.x
   - `postcss` → 8.5.x
   - `ws` → 8.18.x
   - `nanoid` → 5.x
   - `extract-zip` → 2.0.2
4. Validar: `pnpm build` y `pnpm test` (si existen).

**Resultado esperado:** 48 → ~10 alerts.

### Fase D — Special cases (sin parche)
**Objetivo:** reducir los residuales sin forzar upstream.

**Acciones:**
1. **rsa (RUSTSEC-2023-0071):** investigar qué crate del workspace
   jala `rsa` (candidatos: `reqwest`, `redis`, `sqlx`). Si el caller
   ya tiene un bump que no usa rsa, hacer cargo update de ese caller.
   Si no hay opción, documentar aceptado en `.cargo/audit.toml` con
   `ignore = ["RUSTSEC-2023-0071"]`.
2. **wee_alloc (CRITICAL, unmaintained):** buscar en lockfiles; si
   es solo transitivo de `wasm-bindgen`, evaluar flag
   `--default-features=false` o reemplazo con `dlmalloc`.
3. **pyo3 restantes (6 alerts):** verificar que ninguno de los 6
   sea RUSTSEC-2026-0176 (ya cerrado) — los otros 6 son probablemente
   versiones previas a 0.29 que requieren nuestro bump. Cuando
   feat/audit-360-remediation se mergee a main, deben cerrarse solos.
4. **glib (1 alert):** revisar Cargo.toml con `glib` directo, pinear
   versión fixeada.

**Resultado esperado:** 10 → ~3-5 alerts.

### Fase E — Verificar y commit
**Objetivo:** documentar el delta y commitear.

**Acciones:**
1. Re-correr `cargo audit --json` y comparar `.vulnerabilities.count`
   con baseline.
2. `gh api 'repos/jenovoas/sentinel/dependabot/alerts?state=open&per_page=100' --paginate -q '.[] | .number'` y comparar con baseline.
3. Si delta > 50 actuals: commitear `fix(deps): massive bump to clear
   N alerts` con tabla de delta incluidos.
4. Si quedan residuales: cerrar con `gh api repos/.../dependabot/alerts/<n>/dismiss`
   con razón `tolerable_risk` o `no_bandwagon`, documentado en el
   `docs/03_audits/2026-08-16_*` doc.

## 4. Verificación al final

| Antes | Después |
|---|---|
| 117 alerts | ≤ 15 alerts esperados |
| 1 critical | 0 critical |
| 46 high | ≤ 10 high |
| 43 medium | ≤ 5 medium |
| 27 low | ≤ 0 low (los rand/lru low son bumps) |

**Criterio de éxito:** `cargo audit` + `gh api dependabot/alerts`
reportan ≤ 15 alerts, ninguno critical, y los residuales están
documentados con `ignore` justificado en `.cargo/audit.toml`.

## 5. Riesgos identificados

1. **Next.js major bumps** — pueden romper Server Actions custom
   server y rewrites. Mitigación: bump conservador (minor → minor),
   PR por archivo Next.js modificado.
2. **`src/sentinel-cortex/Cargo.lock` duplicado** — hay un Cargo.lock
   dentro de `src/sentinel-cortex/` que parece un duplicado del
   workspace root. Investigar si es código histórico o si realmente
   se compila standalone. Si es histórico, archivar.
3. **rsa (RUSTSEC-2023-0071)** — sin parche upstream. No se puede
   cerrar; documentar aceptado.
4. **pyo3 0.29 pendientes** — los 6 alerts restantes de pyo3 deben
   cerrarse automáticamente cuando feat/audit-360-remediation se
   mergee a main. Confirmar en Fase E.

## 6. Estado guardado — restaurar al retomar

```
Branch:           feat/audit-360-remediation
HEAD:             dd2d0f2e (fix pyo3 0.25→0.29)
Working tree:     tracked clean; 2 untracked (este plan + JSON baseline)
Origin:           synced (0 commits ahead of origin/feat/audit-360-remediation)
Baseline alerts:  docs/03_audits/phase10-results/gh_dependabot_baseline_2026-08-16.json
```

> **Nota:** el plan mismo y el JSON baseline aparecen como `untracked`
> en `git status` hasta que se commiteen. La línea "Working tree: clean"
> de una versión anterior era engañosa porque los untracked SON estos
> 2 archivos.

## 7. Orden de commits sugerido

```
1. fix(deps): bump rust workspace deps (openssl, rand, lru, bytes)
2. fix(deps): bulk cargo update — reduce N alerts
3. fix(deps): bump frontend packages (next, postcss, fast-uri, ws)
4. fix(deps): bump python deps (pyjwt, python-multipart, dotenv)
5. chore(audit): document tolerable residuals + close gh dependabot
```

O bien un solo commit `fix(deps): clear 100+ gh alerts (Phase A-D)`
si el diff es mecanico y Jaime prefiere un solo bundle.

---

**Próxima sesión:** empezar por Fase A, fase por fase, con commits
individuales por familia de crates para mantener el diff scannable.

---

## 8. Addendum post-Phase 10 (2026-08-16) — hallazgos que afectan este plan

La onda de verificación F1–F11 (commit `2c072752 docs(audit): record
final verification results for 360° audit`) ya se ejecutó en dev box
(Fedora 44). Tres hallazgos de Phase 10 **modifican la confianza** con
la que se puede ejecutar este plan tal como está escrito.

### 8.1 — F7 `pai_convert_bench` falla la tesis del plan v2

| Lane | Esperado por plan v2 | Obtenido en dev box |
|------|----------------------|---------------------|
| A (RAW — producción actual) | 0/256 errores | **30/256 (~12%)** |
| B (PAI-60 exacto, `inject_pai/60`) | 0/256 errores | **30/256 (~12%)** |
| C (PY PROTO doble-escala, exp-fallido) | 256/256 errores | 256/256 ✓ |

Output: `docs/03_audits/phase10-results/F7.txt`.

**Impacto:** los bumps de Fase A (openssl/lru/rand/bytes) **van a mover**
los Lane A y Lane B. Riesgo: terminemos Fase A con Lane A=0/256 (mejor)
o Lane A=60/256 (peor). El bench mide fidelidad de reconstrucción por
nodo, no se preserva bajo bumps arbitrarios.

**Acción obligatoria antes de Fase A:**
1. Re-correr `cargo run --release -p me60os --bin pai_convert_bench`
   en el HEAD limpio y guardarlo como
   `docs/03_audits/phase10-results/pai_convert_bench_baseline_pre-fase-a.txt`.
2. Después de cada bump en Fase A, re-correr el bench y comparar:
   - Si Lane A sube >40/256: abortar el bump, reportar a Jaime.
   - Si Lane A baja a 0/256: documentar como mejora.
3. Lane B también requiere tracking — un bump que mejora A pero rompe
   B es peor que el estado actual.

### 8.2 — F11b `cargo audit` local ≠ GitHub Dependabot

| Fuente | Vulns abiertos |
|--------|---------------|
| GitHub Dependabot (alcance de este plan) | 117 |
| `cargo audit` local (Phase 10 F11b) | 3 (pyo3×2 OOB+Sync, rsa Marvin Attack) + 3 warnings (paste unmaintained, lru×2 unsound) |

**Impacto:** la métrica de "X alertas cerradas" en Fase E step 1
(`cargo audit --json`) **no es comparable** con la baseline de 117
GitHub alerts. El audit local es señal rezagada: los advisories de
GitHub pueden no estar en la DB de `rustsec/advisory-db` aún, y
viceversa.

**Acción obligatoria en Fase E:**
- Métrica primaria de cierre: `gh api 'repos/.../dependabot/alerts?state=open&per_page=100' --paginate | jq -s 'length'`.
- Métrica secundaria: `cargo audit --json | jq '.vulnerabilities.list | length'`.
- Si la primaria no baja ~50%: el plan está subestimando el problema,
  re-evaluar.

### 8.3 — F5 pyo3 binding stale vs `quantum/` tests

17 tests de `quantum/` asumen un método
`me60os_core.SPA.from_decimal_degrees_FOR_IMPORT_ONLY` que el binding
pyo3 **ya no expone**. El bump pyo3 0.25→0.29 (commit `dd2d0f2e`)
**rompió la API Python** sin recompilar el binding.

**Impacto en Fase A:** cualquier otro bump de crate Rust que tenga
binding Python (pyo3, numpy, etc.) **va a requerir**
`maturin develop` o equivalente antes de correr pytest.

**Acción obligatoria en Fase A:**
- Si el bump toca pyo3/numpy: re-compilar el binding
  (`maturin develop --release` o `cargo build --release -p me60os-py`
  según el binding usado por Sentinel) antes de pytest.
- Si pytest no se puede correr en dev box (F4 BLOQUEADO), al menos
  validar con `python -c "import me60os_core; print(dir(me60os_core.SPA))"`
  que los atributos críticos siguen existiendo.

### 8.4 — Tesis "Lane A=0" del plan v2 — re-evaluar

El plan v2 asume Lane A=0/256 como baseline sano. Phase 10 encontró
Lane A=30/256 **antes** de tocar dependencias. Esto significa que la
tesis "el bench valida la fidelidad del lattice" no es tan limpia como
el plan предполагает. La pregunta a responder antes de cerrar Fase A
**no es** "¿podemos cerrar las 117 alerts?" sino:

> ¿Podemos cerrar las 117 alerts **sin empeorar** la fidelidad del
> lattice (Lane A y Lane B) ni los 4 FAIL corregibles de Phase 10
> (F2 clippy, F3 fmt, F7 bench, F11b audit)?

Si la respuesta al final de Fase A es "sí cerramos 50 alerts pero Lane A
subió a 60/256 y F11b sigue con 3 vulns", el delta neto es **negativo**
y hay que reconsiderar el orden de las fases.

**Acción:**
- Antes de mergear Fase A, regenerar `docs/03_audits/phase10-results/F*.txt`
  con los nuevos números (especialmente F7, F11b).
- Si F7 Lane A > 60/256 al final de Fase A: NO mergear, abrir task
  aparte para entender por qué `inject_spa` (Phase 2, commit 3117557f)
  no es suficiente.

---

**Estado del addendum:** los 4 sub-puntos (8.1–8.4) son **bloqueantes**
para empezar Fase A. Se recomienda ejecutar las 4 acciones obligatorias
de 8.1 y 8.2 antes de tocar cualquier `Cargo.toml`.
