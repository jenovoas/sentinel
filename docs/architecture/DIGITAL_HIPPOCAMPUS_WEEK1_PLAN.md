# Plan de Implementación: Digital Hippocampus - Semana 1 (Fundación)

## Contexto Estratégico

El **Digital Hippocampus** es la pieza clave para la persistencia cognitiva de Sentinel. Esta semana nos enfocamos en establecer la infraestructura de almacenamiento vectorial y la capacidad de generación de escenarios de memoria.

---

## Objetivos

1. **Establecer ChromaDB**: Repositorio de memoria distribuido en 12 zonas Base-60.
2. **Implementar CA3 Generator**: Integración con Gemini 3 Flash para análisis episódico.
3. **Validar Persistencia**: Asegurar que las decisiones técnicas se guarden y recuperen correctamente.

---

## 1. Capa de Almacenamiento (ChromaDB)

### Objetivo

**Crear una memoria de fase persistente organizada por zonas de divisibilidad.**

### Implementación

#### [NEW] [chromadb_storage.py](file:///home/jnovoas/sentinel/src/backend/app/core/chromadb_storage.py)

**Características**:
- **Persistent Client**: Almacenamiento local en `/var/lib/sentinel/memory`.
- **12 Colecciones**: Mapeo directo a los divisores de 60.
- **Embeddings**: Uso de `sentence-transformers/all-MiniLM-L6-v2` (local).

---

## 2. Capa Generativa (CA3 Generator)

### Objetivo

**Transformar detecciones de eBPF en escenarios de memoria enriquecidos.**

### Implementación

#### [NEW] [ca3_generator.py](file:///home/jnovoas/sentinel/src/backend/app/core/ca3_generator.py)

**Características**:
- **Gemini 3 Flash**: Generación de 3-5 escenarios por evento.
- **Enriquecimiento**: Inclusión de threat score, ataque hipotético y confianza.

---

## Verification Plan

### Automated Tests
1. **Storage Test**: Store/Recall en una zona específica (e.g., Zona 1 - Primos).
2. **Generator Test**: Generar escenarios para un payload de ataque simulado.
3. **Integration Test**: Flujo completo de detección -> generación -> almacenamiento.

---

## Timeline

### Día 1 (Hoy - 31 Dic)
- [x] Configurar `/var/lib/sentinel/memory` (ahora `data/memory`) ✅
- [x] Implementar `chromadb_storage.py` ✅
- [x] Inicializar las 12 zonas Base-60 ✅
- [x] Verificar almacenamiento vectorial ✅

### Día 2 (1 Ene 2026)
- [ ] Implementar `ca3_generator.py`.
- [ ] Integrar con API keys de Gemini.
- [ ] Primer test de almacenamiento episódico.

---

**Sentinel Cortex™ Memory Division**  
*Remembering the past to protect the future.*
