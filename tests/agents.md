# 🧪 AGENTE TESTS: ASEGURAMIENTO DE CALIDAD

> **CONTEXTO:** Este directorio (`/tests`) valida que la realidad coincida con la teoría.

## 1. 🛡️ DIRECTIVAS CRÍTICAS

### 🎯 AXIOMA II: HONESTIDAD RADICAL
- **FALLOS:** Un test rojo es un regalo. Es datos. No lo "arregles" cambiando el assert para que pase. Arregla el código.
- **MOCKS:** Minimiza los mocks. Testea contra la lógica real S60 siempre que sea posible.

### 🚫 AXIOMA I: NO FLOATS EN TESTS
- **INPUTS:** No uses `10.5` en tus inputs de prueba. Usa `S60(10, 30)`.
- **ASSERTS:** Valida contra resultados enteros exactos.

## 2. ⚙️ REGLAS OPERATIVAS

1. **Frameworks:** `pytest` (Python), `cargo test` (Rust).
2. **CI:** Los tests deben ser deterministas. Si falla a veces (flaky), está mal.
3. **Cobertura:** Prioriza la lógica S60 y la seguridad del Kernel.
4. **Regresión:** Cada bug encontrado debe convertirse en un test nuevo (`test_bug_XXX.py`).

## 3. 📂 MAPA DE CONOCIMIENTO

- **Unitarios:** `tests/unit/`
- **Integración:** `tests/integration/` (E2E)
- **Benchmarks:** `tests/benchmarks/` (Rendimiento)

---
**OBJETIVO:** Confianza absoluta. "Trust, but verify."
