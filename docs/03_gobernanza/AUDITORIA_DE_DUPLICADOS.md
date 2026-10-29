# Auditoría Científica de Duplicados - Sentinel

Este documento identifica los archivos duplicados generados durante la restauración masiva para que el usuario pueda tomar una decisión informada sobre su eliminación manual, respetando la prohibición de uso de `rm/mv` por parte de la IA.

## 1. Módulos Core S60 (Ciencia Real)

A continuación se listan los archivos resucitados del pasado que contienen la matemática sexagesimal verdadera. **ESTOS SON LOS QUE DEBEN PREVALECER.**

| Archivo | Ruta | Hash MD5 | Estado |
| :--- | :--- | :--- | :--- |
| **Math Engine** | `sentinel-cortex/src/math/s60.rs` | `75e2afd7e774601d86e6a998d823804f` | **VERDAD** |
| **Math Logic** | `sentinel-cortex/src/math/s60_math.rs` | `e2a213aa64e2791f1292716288617517` | **VERDAD** |
| **Soul Verifier** | `sentinel-cortex/src/security/soul_verifier_s60.rs` | `f30224a466cb96052a56de7f8c71385c` | **VERDAD** |

---

## 2. Archivos de Arquitectura (La Mentira SOLID)

Existen múltiples versiones de la arquitectura. El archivo en la raíz es una simplificación generada por la IA.

- **VERDAD**: `docs/00_vision_y_arquitectura_global/ARCHITECTURE.md` (Hash `8d24...`)
- **MENTIRA**: `docs/ARCHITECTURE.md` (Hash `ef29...` - Contiene aviso de desinformación).
- **OBSOLETO**: `docs/archive/ARCHITECTURE.md` (Hash `4645...`).

---

## 3. Carpetas de Residuos Identificadas

Se recomienda la eliminación manual de los siguientes directorios que contienen copias redundantes:

1. `docs/archive/` (Contenido ya movido a `docs/`).
2. `quantum/.yatra_backup/` (Respaldo de sesiones fallidas).
3. `services/me-60os_dependency/` (Si está vacío o roto).

---

## 4. Archivos de Respaldo (.bak)

Detectados 12 archivos `.bak` que son restos de operaciones de edición de la IA. Se recomienda su borrado total.
