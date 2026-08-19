# Migraciones Python → Rust - Sentinel

**Fecha de análisis**: 2026-03-18
**Propósito**: Documentar qué módulos Python han sido migrados a Rust para facilitar la limpieza del codebase.

---

## 📋 Resumen Ejecutivo

| Categoría | Archivos Python | Estado |
|-----------|-----------------|--------|
| **Migrados a Rust** | 8 | ✅ Listos para marcar deprecados |
| **Proxies/ Wrappers** | 3 | ⚠️ Mantener como puente FFI |
| **Backend API** | ~25 | 🔴 No migrar - API activa |
| **Tooling/scripts** | ~15 | 🟡 Evaluar caso por caso |
| **Quantum experiments** | ~100+ | 🟡 Mantener - investigación activa |

---

## ✅ MIGRADOS A RUST (Python deprecado)

### 1. Matemática S60 (Base-60)

| Python (Deprecado) | Rust (Activo) | Notas |
|--------------------|---------------|-------|
| `quantum/sovereign_math.py` | `sentinel-cortex/src/math/s60.rs` | Proxy a Rust, dice: "Redirigido exitosamente a YatraCore/Rust S60Math" |
| `quantum/yatra_math.py` | `sentinel-cortex/src/math/s60_math.rs` | Wrapper para Rust S60Math |
| `quantum/yatra_core.py` | `me60os_core` (crate externo) | Usa `me60os_core.so` via ctypes |

**Acción recomendada**: Marcar archivos Python como `# DEPRECATED - Use sentinel_cortex.math.s60` y eventualmente eliminar.

---

### 2. Quantum Scheduler

| Python (Deprecado) | Rust (Activo) | Notas |
|--------------------|---------------|-------|
| `backend/app/quantum_scheduler.py` | `sentinel-cortex/src/quantum/quantum_scheduler.rs` | Scheduler con resonancia armónica |
| `tools/quantum_scheduler.py` | Mismo | **ELIMINADO** - Duplicado obsoleto |
| `tools/quantum_scheduler_v2.py` | Mismo | **ELIMINADO** - Versión antigua |
| `quantum/quantum_scheduler_bridge.py` | FFI en `sentinel-cortex/src/lib.rs` | Bridge FFI para Python |

---

### 3. BioResonator

| Python (Deprecado) | Rust (Activo) | Notas |
|--------------------|---------------|-------|
| Lógica bio-coherence en Python | `sentinel-cortex/src/quantum/bio_resonator.rs` | Motor de coherencia bio-cuántica |
| - | `sentinel-cortex/src/security/bio_resonance.rs` | Versión para seguridad |

---

### 4. Pattern Detection (Motor de Decisiones)

| Python (Deprecado) | Rust (Activo) | Notas |
|--------------------|---------------|-------|
| Detección de patrones en Python | `sentinel-cortex/src/engine/patterns.rs` | Credential Stuffing, Resource Exhaustion |
| Modelos de eventos | `sentinel-cortex/src/models/event.rs` | Data models para detección |

---

### 5. Memory Bridge

| Python (Deprecado) | Rust (Activo) | Notas |
|--------------------|---------------|-------|
| Bridge Python a memoria compartida | `sentinel-cortex/src/memory/resonant_lattice_bridge.rs` | Comentario: "Direct Rust integration... avoiding Python-level bridging" |

---

### 6. Semantic Shell / Router

| Python (Deprecado) | Rust (Activo) | Notas |
|--------------------|---------------|-------|
| CLI interactivo Python | `sentinel-cortex/src/quantum/semantic_shell.rs` | REPL interactivo en Rust |
| Router de intents Python | `sentinel-cortex/src/quantum/semantic_router.rs` | Clasificación via Vertex AI/Gemini |

---

### 7. Soul Verifier S60

| Python (Deprecado) | Rust (Activo) | Notas |
|--------------------|---------------|-------|
| Verificación S60 en Python | `sentinel-cortex/src/security/soul_verifier_s60.rs` | Validación de integridad S60 |
| - | `sentinel-cortex/src/security/soul_verifier_s60_production.rs` | Versión producción |

---

## 🔴 NO MIGRAR - Código Python Activo

### Backend FastAPI (`backend/app/`)
- `main.py` - Entry point de la API
- `config.py` - Configuración
- `database.py` - Conexión SQLAlchemy
- `routers/` - Todos los endpoints HTTP
- `models/` - Modelos ORM
- `services/` - Lógica de negocio
- `security/` - Autenticación JWT

**Razón**: Esta es la API HTTP principal. Mantener hasta que se decida migrar todo el backend a Rust.

---

### Quantum Experiments (`quantum/experiments/`)
- 41+ archivos de experimentos activos
- Investigación en curso sobre Base-60 y Bekenstein-Hawking

**Razón**: Documentado en CLAUDE.md como "NO MODIFICAR sin consultar".

---

## 🟡 EVALUAR CASO POR CASO

### Tools (`tools/`)
- `watchdog_loader_ai.py` - Podría migrarse
- `scan_code_patterns.py` - Utilidad de análisis
- Duplicados de `quantum_scheduler.py` - **ELIMINADOS**

### Host Metrics (`host-metrics/`)
- `audit_watchdog_quantum.py` - Watchdog
- `scripts/analyze.py`, `scripts/report.py` - Scripts de análisis

---

## 🗑️ CÓDIGO DUPLICADO/RUPTURA (Eliminado)

| Archivo/Path | Problema | Acción | Estado |
|--------------|----------|--------|--------|
| `./src/sentinel-cortex/` | Duplicación completa del crate | **ELIMINADO** | ✅ |
| `core/cortex` | Symlink roto a `/home/jnovoas/dev/sentinel/sentinel-cortex` | **ELIMINADO** | ✅ |
| `tools/quantum_scheduler.py` | Duplicado de backend | **ELIMINADO** | ✅ |
| `tools/quantum_scheduler_v2.py` | Versión antigua | **ELIMINADO** | ✅ |

---

## 📊 Mapa de Dependencias

```
sentinel-cortex/ (Rust - SOURCE OF TRUTH)
├── src/math/s60.rs          ← sovereign_math.py, yatra_math.py (DEPRECATED)
├── src/quantum/
│   ├── quantum_scheduler.rs ← quantum_scheduler*.py (DEPRECATED except bridge)
│   ├── bio_resonator.rs     ← Python bio logic (DEPRECATED)
│   ├── semantic_shell.rs    ← Python CLI (DEPRECATED)
│   └── semantic_router.rs   ← Python router (DEPRECATED)
├── src/memory/resonant_lattice_bridge.rs ← Python bridge (DEPRECATED)
├── src/security/
│   ├── soul_verifier_s60.rs ← Python verifier (DEPRECATED)
│   └── bio_resonance.rs
└── src/engine/patterns.rs   ← Python detection (DEPRECATED)

backend/app/ (Python - ACTIVE API)
├── main.py                  ← FastAPI entry point
├── quantum_scheduler.py     ← MIGRADO pero mantener hasta transición
└── ...

quantum/ (Python - MIXED)
├── sovereign_math.py        ← PROXY a Rust (mantener como wrapper)
├── yatra_core.py            ← PROXY a Rust (mantener como wrapper)
├── quantum_scheduler_bridge.py ← FFI bridge (mantener)
└── experiments/             ← ACTIVE RESEARCH (no tocar)
```

---

## 🚀 Próximos Pasos Recomendados

1. **Inmediato**: ✅ COMPLETADO - Eliminar código duplicado confirmado
   - `./src/sentinel-cortex/` (duplicación) ✅
   - `core/cortex` (symlink roto) ✅
   - `tools/quantum_scheduler*.py` (duplicados obsoletos) ✅

2. **Corto plazo**: Marcar archivos deprecados
   - Agregar comentario `# DEPRECATED - Migrated to sentinel-cortex/src/...`
   - Documentar en cada archivo el path de Rust equivalente

3. **Mediano plazo**: Crear tests de regresión
   - Verificar que Rust produce mismos resultados que Python
   - Eliminar Python gradualmente tras validación

4. **Largo plazo**: Migrar backend FastAPI
   - Evaluar migrar a Axum (Rust) o mantener Python

---

## 📝 Notas

- Los archivos en `quantum/experiments/` están protegidos por el protocolo de investigación
- Los wrappers como `sovereign_math.py` sirven como interfaz FFI - mantener hasta que todo el código Python consuma Rust directamente
- El backend FastAPI es producción - cualquier migración requiere plan separado

---

## Historial de Cambios

- **2026-03-18**: Limpieza inicial - eliminados duplicados Rust y scripts obsoletos