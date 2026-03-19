# Plan: Limpieza de Migraciones Python → Rust

**Creado**: 2026-03-18
**Objetivo**: Eliminar código Python obsoleto/duplicado que ya fue migrado a Rust, dejando referencia documentada.

---

## Contexto

El proyecto Sentinel tiene módulos Python que fueron migrados a Rust (`sentinel-cortex/`). Existen:
- Archivos Python que son solo proxies/wrappers a Rust
- Código Rust duplicado en `./src/sentinel-cortex/`
- Symlinks rotos
- Scripts duplicados obsoletos

---

## Alcance

### IN (se tocará)
- `./src/sentinel-cortex/` - Código Rust duplicado
- `./core/cortex` - Symlink roto
- `./tools/quantum_scheduler.py` - Duplicado obsoleto
- `./tools/quantum_scheduler_v2.py` - Versión antigua
- Archivo de referencia `MIGRACIONES_PYTHON_RUST.md` (ya creado en drafts)

### OUT (no se tocará)
- `backend/app/` - API FastAPI activa en producción
- `quantum/experiments/` - Investigación protegida (41 experimentos)
- `quantum/quantum_scheduler_bridge.py` - FFI bridge necesario

---

## Archivo de Referencia

**Ubicación**: `docs/MIGRACIONES_PYTHON_RUST.md`

Contiene el mapeo completo de cada archivo Python migrado a su equivalente Rust.

---

## Tareas

### FASE 1: Limpieza de código duplicado/roto (Bajo riesgo)

#### Tarea 1.1: Eliminar código Rust duplicado
- **Archivo**: `./src/sentinel-cortex/`
- **Acción**: `rm -rf ./src/sentinel-cortex/`
- **Justificación**: Duplicación completa del crate principal. El código activo está en `./sentinel-cortex/`
- **Verificación**: `cargo build` debe pasar usando solo `./sentinel-cortex/`

#### Tarea 1.2: Eliminar symlink roto
- **Archivo**: `./core/cortex`
- **Acción**: `rm ./core/cortex`
- **Justificación**: Symlink apunta a `/home/jnovoas/dev/sentinel/sentinel-cortex` que no existe
- **Verificación**: `ls core/` no debe mostrar errores

#### Tarea 1.3: Eliminar duplicados de quantum_scheduler en tools/
- **Archivos**: 
  - `./tools/quantum_scheduler.py`
  - `./tools/quantum_scheduler_v2.py`
- **Acción**: `rm tools/quantum_scheduler.py tools/quantum_scheduler_v2.py`
- **Justificación**: Versiones obsoletas. La versión activa está en `sentinel-cortex/src/quantum/quantum_scheduler.rs`
- **Verificación**: Grep confirmar que ningún otro archivo los importa

---

### FASE 2: Documentación de migraciones

#### Tarea 2.1: Mover archivo de referencia a docs/
- **Origen**: `.sisyphus/drafts/MIGRACIONES_PYTHON_RUST.md`
- **Destino**: `docs/MIGRACIONES_PYTHON_RUST.md`
- **Acción**: Mover archivo
- **Verificación**: Archivo accesible en `docs/`

#### Tarea 2.2: Agregar comentarios deprecation en archivos Python migrados
Archivos a marcar como deprecados:
- `quantum/sovereign_math.py` - agregar `# DEPRECATED: Migrated to sentinel-cortex/src/math/s60.rs`
- `quantum/yatra_math.py` - agregar `# DEPRECATED: Migrated to sentinel-cortex/src/math/s60_math.rs`
- `backend/app/quantum_scheduler.py` - agregar `# DEPRECATED: Migrated to sentinel-cortex/src/quantum/quantum_scheduler.rs`

---

### FASE 3: Verificación final

#### Tarea 3.1: Verificar build Rust
- **Comando**: `cd sentinel-cortex && cargo build`
- **Criterio**: Sin errores de compilación

#### Tarea 3.2: Verificar que no hay imports rotos
- **Comando**: `grep -r "from tools.quantum_scheduler" .` y similares
- **Criterio**: No debe haber resultados

#### Tarea 3.3: Commit de cambios
- **Mensaje**: `chore: clean up migrated Python code, remove duplicates`
- **Archivos**: Los eliminados + archivo de documentación

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Algo depende de `./src/sentinel-cortex/` | Baja | Grep previo para verificar imports |
| Symlink lo usa algún script | Baja | Era roto, nada puede usarlo |
| Python imports quantum_scheduler de tools/ | Media | Grep verificar antes de eliminar |

---

## Verificación Final

Antes de marcar completado:
- [ ] `cargo build` pasa en `sentinel-cortex/`
- [ ] No hay errores de import en Python
- [ ] Archivo `docs/MIGRACIONES_PYTHON_RUST.md` existe
- [ ] Commit realizado