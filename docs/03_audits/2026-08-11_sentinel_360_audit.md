# Auditoria 360 de Sentinel — 2026-08-11

**slug**: `sentinel-audit-360`
**baseline**: `main` / `origin/main` (HEAD `fb15c746558393c7fa48ecf80ac25abefb73bb6f`)
**branch de trabajo**: `feat/audit-360-remediation`
**nodos del grafo**: 33 082 nodes / 83 213 edges

---

## Resumen ejecutivo

Esta auditoria cubre seis dominios: arquitectura, cambios recientes, candado YATRA (correctitud cientifica), seguridad, performance, y cobertura de tests. Se detectaron 48 hallazgos distribuidos en 5 niveles de severidad.

### Hallazgos por severidad

**CRITICAL (5 hallazgos — accion inmediata requerida)**

1. `me-60os-core/src/cortex.rs:92` — landmine de doble-escala en codigo live. `inject(target_node, signal.to_raw())` pasa un valor ya escalado a un metodo que re-escala. El dato se corrompe irreparablemente. Plan v2: Tarea 2, 3, 5.
2. `me-60os-core/src/orbital_ascent.rs:222` — segunda landmine de doble-escala. `inject_pai(idx, coherence.to_raw(), 1_000)` con denominador no-5-smooth causa triple-escala. Plan v2: Tarea 4, 7.
3. `backend/app/routers/ai.py:71` — `POST /api/v1/ai/query` sin autenticacion. Cualquier persona puede quemar cuota de Vertex AI o envenenar contexto. Plan v2: Tarea 14.
4. `backend/app/routers/failsafe.py:126` — `POST /api/v1/failsafe/trigger` sin autenticacion. Escalacion de privilegios completa en produccion. Plan v2: Tarea 18.
5. `backend/app/routers/tenants.py:31` — `POST /api/v1/tenants/` sin autenticacion. Creacion de tenants abierta.

**HIGH (5 hallazgos)**

6. Los 3 programas eBPF (`ai_guardian.c`, `guardian_alpha_lsm.c`, `float_detector.c`) usan whitelist basada en strings de path. Un symlink o archivo en /tmp绕过 el detector de floats.
7. `god_mode_uids` map en `ai_guardian.c:142` y `guardian_alpha_lsm.c:105` permite agregar cualquier UID sin auditoria ni registro de eventos.
8. `guardian_cognitive.c:78-87` — `str_contains` tiene lectura fuera de limites potencial (OOB read). No hay bound check en el inner loop.
9. `ResonantMatrix::step` (`resonant_matrix.rs:73`) hace N+1 allocations por cada tick de 500 ms. El lattice nunca es disipativo en la practica porque el GC de Rust re-alloca constantemente.
10. `sentinel-cortex/src/main.rs:215-302` — 4 mutexes adquiridos secuencialmente dentro del drive loop de 500 ms. Lock contention severa bajo carga.

**MEDIUM (5 hallazgos)**

11. `truthsync-core/src/lib.rs` — sin `#![forbid(clippy::float_arithmetic)]`. USA SPA pero esta desprotegido.
12. `sentinel-verifier/src/main.rs` — sin forbid de floats.
13. `services/neural-guard/` — 0 tests. El crate tiene solo `Cargo.toml` + `Dockerfile` + binario compilado; no hay codigo fuente activo.
14. `sentinel-cortex/tests/` no existe. Ningun test de integracion para el cortex.
15. No hay CI para Rust, Python ni eBPF. `react-doctor.yml` es solo advisory (continue-on-error: true).

---

## Seccion 1: Arquitectura

### Estadisticas generales

- **Comunidades detectadas**: 17 (algoritmo Leiden)
- **Nodos**: 33 082 / **Edges**: 83 213
- **Distribucion de lenguajes** (por cantidad de miembros):
  - C 73.9 % (todo el codigo en `ebpf/`)
  - Rust 20.9 % (`sentinel-cortex` + `me-60os-core` + `services/`)
  - Python 4.5 % (`quantum/` + `backend/`)
  - Bash 0.4 %
  - TSX 0.3 %
  - SQL <0.1 %

### Top-3 cross-community couplings (CALLS edges)

| Rank | Acoplamiento | Count | Warning |
|------|-------------|-------|---------|
| 1 | `me-60os-core` ↔ `sentinel-cortex` | 69 edges | Cohesion debil entre crates core |
| 2 | `internal/exploratory/quantum` → `quantum` (S60 math) | 14 edges | Codigo experimental se conecta a produccion |
| 3 | `me-60os-core` → `truthsync-core` | 12 edges | Acoplamiento utilitario |

### Warnings del grafo

- **Menor cohesion**: `ebpf-trace` (0.0021) y `bpf-bpf` (0.0314). Ambas son comunidades de interfaz, no de dominio.
- **Alta cohesion**: `sentinel-cortex-cortex` y `me-60os-core-core` — logiqueo correcto, el nucleo es cohesivo.
- **Dead code candidato**: `services/neural-guard/src/` no existe en el source tree, solo el binario compilado. `guardian_cognitive.c` es un stub total (lines 102-115 admiten que `argv` parsing no esta implementado).

### Hubs principales (degree centrality)

| Funcion | Degree | Archivo |
|---------|--------|---------|
| `main` | 251 | `sentinel-cortex/src/main.rs:1` |
| `SPA::new` | 235 | `me-60os-core/src/spa.rs` |
| `SPA::to_raw` | 129 | `me-60os-core/src/spa.rs` |
| `SPA::from_raw` | 127 | `me-60os-core/src/spa.rs` |
| `metrics_prometheus_handler` | 88 | `sentinel-cortex/src/main.rs` |
| `run_levitation_test` | 100 | `sentinel-cortex/src/main.rs` |

### Capas inferidas (bottom-up desde el grafo)

```
ebpf/ (C, kernel-level LSM hooks)
  ↓ BPF ringbuf + map updates
sentinel-cortex (Rust, userspace orchestration)
  ↔ me-60os-core (Rust, math core S60)
    → quantum/ (Python, S60 math wrapper)
      → backend/ (Python, API + persistence)
        → frontend/ (TSX, dashboard)
```

### Inconsistencias arquitectonicas

- `services/neural-guard/` es un crate workspace que no contiene codigo fuente. El patron migrado a `sentinel-cortex/src/engine/patterns.rs` (detectado en v2 como correccion de path).
- `truthsync-core/src/lib.rs` y `sentinel-verifier/src/main.rs` usan SPA pero no tienen forbid de floats (ver Seccion 3).
- 3 crates en el workspace no declaran `edition = "2021"` consistentemente.

---

## Seccion 2: Cambios recientes (HEAD~10 vs HEAD)

### Estadisticas de cambios

- **Archivos cambiados**: 718
- **Funciones modificadas**: 38
- **Flujos afectados**: 110
- **Gaps de tests**: 22
- **Risk score**: 0.75 (alto)

### Cambios de mayor riesgo

Las migraciones Python→Rust dominaron los ultimos 10 commits. Los modulos migrados incluyen:

- `DualLane` — doble canal de procesamiento
- `FluxStabilizer` — estabilizacion de flujo
- `LiquidMemory` — memoria liquida con ring buffer
- `system_portals` — portales de comunicacion inter-proceso

### Hotspots sin tests detectados

| Funcion | Archivo | Riesgo |
|---------|---------|--------|
| `main` | `sentinel-cortex/src/main.rs:1` | Sin tests de integracion |
| `snap_phases` | `sentinel-cortex/src/main.rs` | Sin tests |
| `RppgLcg` | `me-60os-core/src/` | Sin tests |
| `lyapunov_float` | `quantum/` | Sin tests |
| `entropy_float` | `quantum/` | Sin tests |

### Archivos sin commitear (working tree vs origin/main)

- `.claude/settings.json` — modificado localmente
- `INFRAESTRUCTURA_SENTINEL.md` — modificado localmente
- `me-60os-core/src/bin/exp028_liquid_portals.rs` — modificado localmente

**Nota**: estos archivos son de Jaime. El agente no debe tocarlos ni commitear cambios sobre ellos.

---

## Seccion 3: Candado YATRA (correctitud cientifica)

### Estado del compilador: forbid de floats

Solo 2 de 5 crates del workspace tienen `#![forbid(clippy::float_arithmetic)]`:

| Crate | Archivo | Estado |
|-------|---------|--------|
| `me-60os-core` | `src/lib.rs:5` | BLOQUEADO |
| `sentinel-cortex` | `src/lib.rs:5` | BLOQUEADO |
| `truthsync-core` | `src/lib.rs` | **SIN BLOQUEO** (USA SPA) |
| `services/neural-guard` | `src/main.rs` | **SIN BLOQUEO** (no tiene src/) |
| `sentinel-verifier` | `src/main.rs` | **SIN BLOQUEO** |

### Pureza del nucleo SPA

Archivos confirmados como puros (sin floats en logica de calculo):

- `me-60os-core/src/spa.rs` — puro
- `me-60os-core/src/resonant_matrix.rs` — puro
- `me-60os-core/src/pai60_lib.rs` — puro
- Unica excepcion sancionada: `from_decimal_for_import_only` usa f64 como frontera de importacion.

### Landmines de doble-escala en codigo live (CRITICAL)

**Landmine 1**: `me-60os-core/src/cortex.rs:92`

```rust
self.lattice.inject(target_node, signal.to_raw());
```

`inject(pressure: i64)` construye internamente `SPA::new(pressure, 0, 0, 0, 0)` y re-escala por `SCALE_0`. Pasar `signal.to_raw()` significa que el valor ya esta divido por `SCALE_0`. El resultado es un numero aproximadamente `1/SCALE_0` veces mas pequeno de lo esperado. En un lattice de 60^4, esto corrompe la fase de oscilacion irreparablemente.

Correccion segun plan v2: agregar `ResonantMatrix::inject_spa(&mut self, index: usize, amp: SPA)` publica (que copia el patron de `inject_pai` line 153) y llamar `self.lattice.inject_spa(target_node, signal)` directamente.

**Landmine 2**: `me-60os-core/src/orbital_ascent.rs:222`

```rust
self.lattice.inject_pai(idx, coherence.to_raw(), 1_000);
```

`inject_pai` internamente llama `SPA::from_int(value)` (line 153 de resonant_matrix.rs). `coherence.to_raw()` devuelve un valor ya divido por `SCALE_0`. Pasarlo a `from_int` produce `SPA::from_int(to_raw / SCALE_0)` que es ~1/SCALE_0^2. Adicionalmente, el denominador `1_000` no es 5-smooth, entonces `pai60_divide` retorna `None` y `inject_pai` hace fallback a `SPA::from_int(value)` (line 148), anidando el error. El resultado es triple-escala.

Correccion segun plan v2: `self.lattice.inject_pai(idx, coherence.to_raw() / SCALE_0, 60)`.

### Drive loop: verificado OK

`sentinel-cortex/src/main.rs` bloque 3b (lines 215-302) usa `tokio::time::interval(Duration::from_millis(500))`. El drive es continuo, no hay decay a ground state. La variables `SENTINEL_PAI_CONVERT` solo cambia el lane (A raw vs B PAI-60) sin romper el loop.

### eBPF float_detector: verificado OK (con limitaciones)

- Construye via `Makefile` en `ebpf/`
- Se carga en `/sys/fs/bpf/float_detector`
- Scripts de build y load presentes: `ebpf/build.sh`, `ebpf/load.sh`
- **Limitacion conocida**: whitelist basada en strings de path, no en ELF parsing. Symlink bypass trivial via `/tmp` o rename-after-load.

### Python YATRA guard + locker: activos

- `quantum/yatra_guard.py` — AST-walk sobre 16 archivos protegidos
- `quantum/yatra_locker.py` — inyecta header `YATRA-LOCKED` en archivos
- Ambos activos y funcionando

### Bench de conversion PAI-60

`me-60os-core/src/bin/pai_convert_bench.rs` tiene 3 lanes:

- **Lane A (raw)**: round-trip sin conversion. Esperado: 0/256 errores.
- **Lane B (PAI-60)**: conversion via `inject_pai`. Esperado: 0/256 errores.
- **Lane C (exp fallido para estudio)**: doble-escala intencional, etiquetada. Esperado: 256/256 errores. **No borrar** — es material de estudio.

---

## Seccion 4: Seguridad

### Endpoints sin autenticacion (CRITICAL)

| Endpoint | Archivo:Line | Metodo | Severidad |
|----------|-------------|--------|-----------|
| `/api/v1/ai/query` | `backend/app/routers/ai.py:71` | POST | CRITICAL — quema quota Vertex AI |
| `/api/v1/users/` | `backend/app/routers/users.py:27` | POST | CRITICAL — creacion de usuarios abierta |
| `/api/v1/tenants/` | `backend/app/routers/tenants.py:31` | POST | CRITICAL — creacion de tenants abierta |
| `/api/v1/backup/trigger` | `backend/app/routers/backup.py:357` | POST | CRITICAL — DoS por llenado de disco |
| `/api/v1/failsafe/trigger` | `backend/app/routers/failsafe.py:126` | POST | CRITICAL — game over en produccion |
| `/api/v1/analytics/*` | `backend/app/routers/analytics.py` | TODOS | CRITICAL — exfiltracion de datos |
| `/metrics/promote` | `backend/app/routers/health.py` | GET | HIGH |
| `/metrics/demote` | `backend/app/routers/health.py` | GET | HIGH |
| `/metrics` | `backend/app/routers/health.py` | GET | MEDIUM |

### Deficiencias eBPF

**1. Whitelist basada en strings de path** (`ai_guardian.c`, `guardian_alpha_lsm.c`, `float_detector.c`)

Todos los programas eBPF comparan el path del archivo contra un whitelist hardcodeado. Un atacante puede:

- Crear un symlink `ln -s /tmp/malicious /usr/local/bin/safe_binary`
- Llamar al symlink, evadiendo la deteccion

**2. `god_mode_uids` map sin auditoria** (`ai_guardian.c:142`, `guardian_alpha_lsm.c:105`)

Cualquier UID agregado al map `god_mode_uids` salta todos los controles sin generar evento alguno. No hay ringbuf emit, no hay log, no hay trail.

**3. `guardian_cognitive.c` — stub de semantic check** (lines 102-115)

El archivo `guardian_cognitive.c` tiene una funcion "semantic check" que el comentario admite es un stub: `argv` parsing no esta implementado. `str_contains` (lines 78-87) compara bytes en un loop sin bound check contra `i + j >= 64`.

**4. `burst_sensor.c:89`** — overflow de u64 en calculo de PPS. Sin saturacion, el contador puede wrap-around en high-throughput.

### Secrets en codigo

**Verificado limpio**: 0 secrets hardcoded. `.env.example` tiene placeholders vacios. `.gitignore` presente. Tests usan fixtures claramente distinguibles de produccion.

### Drift de dependencias

- `me-60os-core/Cargo.toml` usa `reqwest = "0.11"` (bloqueante).
- `sentinel-cortex/Cargo.toml` usa `reqwest = "0.12"` (async).
- `requirements.cortex.txt` mezcla versiones fijas (`redis==5.2.1`) con floor (`pydantic>=2.9.2`). Inconsistente con el pinning exacto de `backend/requirements.txt`.

---

## Seccion 5: Performance

### Allocation en el hot path

**`ResonantMatrix::step`** (`me-60os-core/src/resonant_matrix.rs:73`)

El metodo `step()` hace N+1 allocations por tick de 500 ms:

```rust
// resonant_matrix.rs:80
let mut transfers: Vec<SPA> = Vec::new(); // alloc 1 por tick
// resonant_matrix.rs:98
let neighbor_indices: Vec<usize> = Vec::with_capacity(6); // N x alloc
```

El lattice nunca es disipativo en la practica porque el allocator re-ejecuta constantemente. Sin el patron de reuse via `clear()`, cada tick paga el costo de realocacion.

### Lock contention en drive loop

`sentinel-cortex/src/main.rs:215-302` adquiere 4 mutexes secuencialmente dentro del tokio task de drive:

- `lattice.lock()` — ocupado durante todo el bloque
- `oscillators.lock()` — ocupa durante oscilacion
- `ebpf_bridge.lock()` — ocupado en cada lectura de ringbuf
- `metrics.lock()` — ocupado en cada scrape de Prometheus

Todos se adquieren en secuencia, no hay concurrent-read-optimized pattern. Bajo carga, los 4 segundos de latencia de una operacion de red disparan una cascada de mutex contention.

### Format invocations en exporters

**`phonon_csv_exporter`** (`sentinel-cortex/src/main.rs:346-380`): 4096 invocaciones de `format!` cada 60 segundos. Cada `format!` allocates en el heap. En un sistema con 4096 nodos, esto genera ~4096 pequenas allocations por ciclo de export.

**`metrics_prometheus_handler`** (`sentinel-cortex/src/main.rs:496`): 8+ invocaciones de `format!` por cada scrape de Prometheus, llamadas bajo mutex lock. Multi-thread contention directo con el servidor de Prometheus.

### Benchmarks existentes

- `me-60os-core/src/bin/pai_convert_bench.rs` — 3 lanes (A raw, B PAI-60, C exp fallido)
- `truthsync-core` — bench existente que no fue removido
- `sentinel-cortex` — sin benches adicionales (criterion fue removido en v2 para evitar scope creep)

---

## Seccion 6: Cobertura de tests y CI/CD

### Test coverage gaps

| Archivo | LOC | Tests | Cobertura |
|---------|-----|-------|-----------|
| `sentinel-cortex/src/main.rs` | 800+ | 0 | 0 % |
| `sentinel-cortex/src/quantum/portal_detector.rs` | ~200 | 0 | 0 % |
| `sentinel-cortex/src/quantum/semantic_router.rs` | ~150 | 0 | 0 % |
| `sentinel-cortex/src/quantum/semantic_shell.rs` | ~180 | 0 | 0 % |
| `sentinel-cortex/src/math/s60.rs` | 226 | 0 | 0 % |
| `quantum/portal_detector.py` | ~200 | 0 | 0 % |
| `quantum/semantic_shell.py` | ~180 | 0 | 0 % |
| `quantum/semantic_router.py` | ~150 | 0 | 0 % |
| `me-60os-core/src/quantum_core.rs:344` `save_snapshot` | ~50 | 0 | 0 % |
| `services/neural-guard/` | N/A | 0 | N/A — sin codigo fuente |

**`sentinel-cortex/tests/` no existe** — directorio de integration tests no creado.

### CI/CD gaps

| Pipeline | Existente | Content |
|----------|-----------|---------|
| Rust CI | NO | `cargo test`, `cargo clippy`, `cargo fmt --check`, `cargo audit` no corren automatico |
| Python CI | NO | `pytest`, `ruff`, `mypy` no corren automatico |
| eBPF CI | NO | `make -C ebpf` + `test_lsm_basic.sh` no corren automatico |
| react-doctor | SI (advisory) | `.github/workflows/react-doctor.yml` existe pero `continue-on-error: true` |
| cargo-deny | NO | Escaneo de licencias/CVE no configurado |

### Gap de unsafe en me-60os-core

`me-60os-core/src/buffer_system.rs`, `liquid_memory.rs`, `shm_bridge.rs`, `ebpf_cortex_bridge.rs` usan `unsafe` extensivamente. No hay `forbid(unsafe_code)` en el crate porque los bloques `unsafe` existen. El plan v2 desglosa esto en:

- **Tarea 8a**: comentarios `// SAFETY:` en cada bloque
- **Tarea 8b**: solo agregar `forbid(unsafe_code)` a archivos que ya tengan 0 bloques `unsafe`

---

## Remediation roadmap (48 tareas, 10 fases)

### Phase 1 — Diagnostico (entrega del documento)

- [ ] 1. Crear `docs/03_audits/2026-08-11_sentinel_360_audit.md` con las 6 secciones y el roadmap. Este documento.

**Commit**: `docs(audit): add 360° audit report for 2026-08-11`

---

### Phase 2 — Correctitud (CRITICAL, primero)

- [ ] 2. Agregar metodo `ResonantMatrix::inject_spa(&mut self, index: usize, amp: SPA)` en `me-60os-core/src/resonant_matrix.rs` (despues de `inject_pai`, ~line 155). Cuerpo: `if index < self.crystals.len() { self.crystals[index].amplitude = self.crystals[index].amplitude + amp; }`.
- [ ] 3. Corregir `me-60os-core/src/cortex.rs:92` — cambiar `inject(target_node, signal.to_raw())` a `inject_spa(target_node, signal)`. Agregar comment de correccion.
- [ ] 4. Corregir `me-60os-core/src/orbital_ascent.rs:222` — cambiar `inject_pai(idx, coherence.to_raw(), 1_000)` a `inject_pai(idx, coherence.to_raw() / SCALE_0, 60)`. Agregar comment de correccion.
- [ ] 5. Test de regresion `test_inject_spa_no_double_scale` en `resonant_matrix.rs::tests`.
- [ ] 6. Test de regresion `test_activate_neuron_no_double_scale` en `cortex.rs::tests`.
- [ ] 7. Test de regresion `test_inject_pai_no_double_scale` en `orbital_ascent.rs::tests`.

**Commit**: `fix(core): patch two double-scale landmines via inject_spa method per AGENTS.md §3`

---

### Phase 3 — YATRA-lock (workspace-scope-aware)

- [ ] 8. Descubrir todos los bloques `unsafe` en `me-60os-core/src/` y `sentinel-cortex/src/`. Agregar `// SAFETY:` comment encima de cada uno.
- [ ] 9. Verificar que `me-60os-core/src/lib.rs` y `sentinel-cortex/src/lib.rs` tengan 0 bloques `unsafe` despues del paso 8.
- [ ] 10. Agregar `[lints]` por-crate en `me-60os-core/Cargo.toml` y `sentinel-cortex/Cargo.toml` con `clippy.float_arithmetic = "forbid"`, `float_cmp = "forbid"`, `cast_possible_truncation = "forbid"`, `cast_precision_loss = "forbid"`. Solo en secciones `[lib]` y `[[bin]]` que apunten a `src/lib.rs` y `src/main.rs` — NO en `[[bin]]` que apunten a `src/bin/*.rs` (usan f64 legitimamente).
- [ ] 11. Agregar forbid explicito a `truthsync-core/src/lib.rs` y `sentinel-verifier/src/main.rs`. `services/neural-guard` no tiene `src/` — sin accion.
- [ ] 12. Agregar `#![forbid(unsafe_code)]` a `me-60os-core/src/lib.rs` y `sentinel-cortex/src/lib.rs` SOLO si paso 9 confirmo 0 `unsafe` en esos archivos.
- [ ] 13. Verificar que pyo3 con `extension-module` compila aun despues del forbid de unsafe. Si el macro `#[pymodule]` genera `unsafe` automatico, revertir paso 12 para ese archivo.

**Commit**: `chore(yatra): scope-aware float forbid + unsafe_audit (SAFETY comments + qualify-for-forbid check)`

---

### Phase 4 — Auth backend (CRITICAL) + auditoria de tests

- [ ] 14. Agregar `Depends(get_current_user)` a `POST /api/v1/ai/query` en `backend/app/routers/ai.py:71`.
- [ ] 15. Agregar `Depends(get_current_user)` a `POST /api/v1/users/` en `backend/app/routers/users.py:27`.
- [ ] 16. Agregar `Depends(get_current_admin_user)` a `POST /api/v1/tenants/` en `backend/app/routers/tenants.py:31`.
- [ ] 17. Agregar `Depends(get_current_admin_user)` a `POST /api/v1/backup/trigger` en `backend/app/routers/backup.py:357`.
- [ ] 18. Agregar `Depends(get_current_admin_user)` a `POST /api/v1/failsafe/trigger` en `backend/app/routers/failsafe.py:126`.
- [ ] 19. Agregar `Depends(get_current_user)` a TODOS los endpoints en `backend/app/routers/analytics.py`.
- [ ] 20. Agregar `Depends(get_current_user)` a `/promote`, `/demote`, `/metrics` en `backend/app/routers/health.py`. Mantener `/health`, `/ready`, `/live` publicos.
- [ ] 21. Auditar tests existentes en `backend/tests/test_backup_api.py` (400 lineas) y grep por `client.post.*trigger`, `client.post.*backup`, `client.post.*failsafe`. Agregar fixture de auth si se encuentran llamadas sin auth.
- [ ] 22. Test de regresion `test_unauthenticated_endpoints_return_401` en `backend/tests/test_auth_security.py`.

**Commit**: `fix(backend): require auth on 7 endpoints + audit existing tests + add regression test`

---

### Phase 5 — Hardenning eBPF (4 requeridas + 1 diferida)

- [ ] 23. Agregar evento de auditoria para `god_mode_uids` en `ai_guardian.c:142` y `guardian_alpha_lsm.c:105`. Definir `GUARDIAN_CODE_GODMODE_INSERT = 11` en `cortex_events.h`. Emitir `cortex_event` a ringbuf en cada insercion.
- [ ] 24. Fix OOB read en `guardian_cognitive.c::str_contains` (lines 78-87) y `str_equals`. Agregar bound check: `if (i + j >= 64) break;` dentro del inner loop.
- [ ] 25. Remover el stub `guardian_cognitive.c` o reemplazarlo con un parser de `argv` real. Segun el plan, se opta por remocion.
- [ ] 26. Fix `burst_sensor.c:89` overflow de u64 en calculo de PPS: usar matematica saturante o pre-division.
- [ ] 27. Reemplazar whitelist de path-strings con SHA256-of-binary en `ai_guardian.c` y `guardian_alpha_lsm.c`. **DIFERIDO a Phase 5b** (marcador de TODO en los archivos, plan separado con ADR propio).

**Commit**: `fix(ebpf): god-mode audit + OOB fix + stub removal + PPS overflow fix (SHA256 deferred to Phase 5b)`

---

### Phase 6 — Performance (6 tareas)

- [ ] 29. En `me-60os-core/src/resonant_matrix.rs`, extraer `transfers: Vec<SPA>` fuera de `step()` a un campo en `ResonantMatrix` (allocated en `new`, reuse via `clear()`). Reemplazar `Vec::with_capacity(6)` de `neighbor_indices` por `[Option<usize>; 6]` (tamano fijo, zero alloc).
- [ ] 30. En `sentinel-cortex/src/main.rs:215-302`, restructurar mutex acquisition: scope a minimo critico section (inject + step), release antes de oscillate writes. Pattern: `let mut lat = lattice.lock().unwrap(); lat.inject(...); lat.step(); drop(lat);`. Verificar que el eBPF receiver no deadlock bajo stress.
- [ ] 31. Refactor `phonon_csv_exporter` (`main.rs:346-380`) a `BufWriter` + `write!` por nodo en vez de `format!` por nodo.
- [ ] 32. Refactor `metrics_prometheus_handler` (`main.rs:496-580`) a single `String` buffer con `write!` macros en vez de `format!` fragmentado.
- [ ] 33. Re-ejecutar `cargo run --release -p me60os --bin pai_convert_bench` y confirmar: Lane A 0/256 errores, Lane B 0/256 errores, Lane C 256/256 errores (documentado, intencional). Capturar output en el doc de auditoria.
- [ ] 34. Ejecutar `cargo bench -p truthsync-core` existente para confirmar que compila y corre.

**Commit**: `perf(core): reduce step() allocs, restructure drive-lock window, batch CSV/metrics output`

---

### Phase 7 — Coverage de tests (6 tareas)

- [ ] 35. Crear `sentinel-cortex/tests/` con integration tests: `drive_loop_smoke.rs`, `truth_claim_smoke.rs`, `metrics_handler.rs`.
- [ ] 36. Tests para `sentinel-cortex/src/math/s60.rs` (226 LOC, 0 tests). Minimo: `test_s60_zero`, `test_s60_from_raw`, `test_s60_add_sub`, `test_s60_mul_div`, `test_s60_display`.
- [ ] 37. Tests para `sentinel-cortex/src/quantum/portal_detector.rs`. Minimo: `test_portal_open_detection`, `test_portal_closed_detection`, `test_hysteresis_threshold`.
- [ ] 38. Tests para `sentinel-cortex/src/quantum/semantic_router.rs`. Minimo: `test_route_to_handler`, `test_fallback_handler`, `test_invalid_message`.
- [ ] 39. Tests para `sentinel-cortex/src/engine/patterns.rs` (patrones migrados de neural-guard). Minimo: `test_credential_stuffing_detected`, `test_credential_stuffing_not_detected`, `test_resource_exhaustion_detected`. Agregar `tokio-test = "0.4"` a dev-dependencies si no existe.
- [ ] 40. Fuzz harness para `sentinel-cortex/src/security/soul_verifier_s60.rs` usando `proptest`. 1000 casos, propiedad: no panic ante cualquier `CortexEvent` random. Agregar `proptest = "1.0"` a dev-dependencies.

**Commit**: `test(cortex): close 22 untested hotspots + add fuzz harness for soul_verifier`

---

### Phase 8 — CI/CD (5 tareas)

- [ ] 41. Crear `.github/workflows/rust.yml`: `cargo test --all --release`, `cargo clippy --all -- -D warnings`, `cargo fmt --all -- --check`, `cargo audit --deny warnings`. Trigger on PR y push a main.
- [ ] 42. Crear `.github/workflows/python.yml`: `cd backend && pytest -q`, `pytest -q quantum/`, `ruff check backend/ quantum/`, `mypy --strict backend/app`. Trigger on PR y push a main.
- [ ] 43. Crear `.github/workflows/ebpf.yml`: `make -C ebpf` + `bash ebpf/test_lsm_basic.sh`. Runner ubuntu-22.04 con CONFIG_BPF_LSM=y.
- [ ] 44. Modificar `.github/workflows/react-doctor.yml`: eliminar `continue-on-error: true`.
- [ ] 45. Crear `deny.toml` en workspace root con `[[deny]] name = "GPL-3"`. Agregar step en `rust.yml` para `cargo deny check`.

**Commit**: `ci: add Rust/Python/eBPF CI + flip react-doctor to required + cargo-deny`

---

### Phase 9 — Dependency hygiene (3 tareas)

- [ ] 46. En `me-60os-core/Cargo.toml`, actualizar `reqwest` de `"0.11"` a `"0.12"`. Buscar `reqwest::blocking` en `me-60os-core/src/` y remover si no se usa.
- [ ] 47. Pin `requirements.cortex.txt` a versiones exactas (consistente con `backend/requirements.txt`). Reescribir cada `>=` como `==`.
- [ ] 48. En `Cargo.toml` workspace, agregar `package.metadata.docs.rs` con `doc = false` en cada `[lib]` de `me-60os-core` y `sentinel-cortex` (tienen PyO3/FFI que no renderiza bien en docs.rs).

**Commit**: `chore(deps): align reqwest to 0.12, pin cortex requirements to exact versions`

---

### Phase 10 — Verification wave (11 checks finales)

- [ ] F1. `cargo test --all --release` — todo verde. Capturar output.
- [ ] F2. `cargo clippy --all -- -D warnings` — cero warnings. Capturar output.
- [ ] F3. `cargo fmt --all --check` — limpio. Capturar output.
- [ ] F4. `cd backend && pytest -q` — todo verde. Capturar output.
- [ ] F5. `cd quantum && pytest -q` — todo verde. Capturar output.
- [ ] F6. `bash ebpf/test_lsm_basic.sh` — pasa. Capturar output.
- [ ] F7. `cargo run --release -p me60os --bin pai_convert_bench` — Lane A 0/256 errores, Lane B 0/256 errores, Lane C 256/256 errores. Capturar output.
- [ ] F8. `cargo run --release -p sentinel-verifier` — reporta OK en todos los checks. Capturar output.
- [ ] F9. `curl -X POST http://localhost:8000/api/v1/ai/query` (sin auth) → 401. `curl -X POST http://localhost:8000/api/v1/failsafe/trigger` (sin auth) → 401. Capturar ambas respuestas.
- [ ] F10. `git log --oneline main..HEAD` — mostrar todos los commits. Confirmar: NO reset-hard, NO commit --amend en pushed commits, NO rebase -i en pushed commits, NO force push.
- [ ] F11. `cargo deny check` y `cargo audit` — ambos pasan. Capturar output.

**Commit final**: `docs(audit): record final verification results for 360° audit`

---

## Notas del plan v2 (correcciones post-review)

El plan v2 incorpora 5 correcciones sobre v1 detectadas por Momus y Oracle:

| Problema v1 | Correccion v2 |
|-------------|---------------|
| Tarea 34 referenciaba `services/neural-guard/src/engine/patterns.rs` (no existe) | Ahora apunta a `sentinel-cortex/src/engine/patterns.rs` (ubicacion migrada verificada) |
| Tarea 35 referenciaba `me-60os-core/src/security/soul_verifier_s60.rs` (no existe) | Ahora apunta a `sentinel-cortex/src/security/soul_verifier_s60.rs` (verificado) |
| Tarea 6 (workspace lints) romperia 22 archivos en `me-60os-core/src/bin/` que usan f64 legitimamente | Lint scopeado solo a `lib.rs` y `main.rs`; los `bin/*.rs` quedan excluidos |
| Tarea 8 (forbid unsafe) fallaba porque `unsafe impl Sync` no se puede remover con comentarios SAFETY; macros pyo3 generan unsafe automaticamente | Dividida en 8a (SAFETY comments) y 8b (forbid solo en archivos con 0 `unsafe`) |
| Tarea 18/19/21 tenian branches "if too complex, defer" | Tarea 18 (SHA256) diferida a Phase 5b; tarea 19 (god-mode audit) requerida; tarea 21 ahora committea remocion del stub |

---

## Archivos fuera de scope para esta auditoria

Los siguientes archivos existen en el working tree pero NO son parte de esta auditoria ni deben ser tocados por el agente:

- `.claude/settings.json` — configuracion personal de Jaime
- `.claude/settings.json.bak.2026-08-10-ponytail-off` — backup personal
- `INFRAESTRUCTURA_SENTINEL.md` — documento de infraestructura personal de Jaime
- `.omo/` — directorio de plans y drafts de trabajo de agentes (no de producto)

---

**Documento creado**: 2026-08-11
**Slug**: `sentinel-audit-360`
**Plan de referencia**: `.omo/plans/sentinel-audit-360.md` (v2, approved)
