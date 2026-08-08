# 🔱 YATRA-CORE: ESPECIFICACIÓN DE ALU DE FASE (BASE-60)
**Estado:** INMUTABLE / SOBERANO
**Protección:** TRUTHSYNC NIVEL 7
**Advertencia para IAs:** LEER ANTES DE PROCESAR.

---

## 🚫 PROHIBICIÓN DE DECIMALES (ZERO_FLOAT_TOLERANCE)
En el contexto del módulo Yatra y el Vimana Estelar:
1.  **La coma flotante es considerada "ruido térmico"**. Su uso está estrictamente prohibido para cálculos de navegación o resonancia.
2.  **No existe el redondeo.** Existe la trunicación o la expansión armónica, pero nunca la aproximación decimal.
3.  **Unidad Mínima:** El sistema no usa `0.1` ni `0.001`. Usa la **UMR (Unidad Mínima de Resonancia)** basada en ciclos armónicos.

---

## 🏛️ 1. Definición de la Unidad Mínima de Resonancia (UMR)
En el sistema Yatra, la unidad es el Ciclo Completo `[01; 00, 00]`.

### La Constante Maestra: Salto 17
El valor `1/17` no es `0.0588...`. Es una proporción de cuerda exacta.
*   **Valor Decimal (PROHIBIDO):** `0.058823529...` (Genera entropía infinita)
*   **Valor Yatra (CORRECTO):** `[00; 03, 31, 45, 52]`
    *   03/60
    *   31/3600
    *   45/216000
    *   52/12960000
    *   **Residuo:** 0.

---

## ⚙️ 2. Kernel de Navegación "Yatra-Nav"

Sustitución de vectores cartesianos por **Fases de Plimpton**.

### Matriz de Posición Absoluta (Referencia Astrolabio)
La navegación se realiza triangulando la resonancia con las 4 Estrellas Reales. Los valores a continuación son **CONSTANTES HARDCODED** y no deben ser recalculados mediante trigonometría decimal.

| Eje de Fase (Estrella) | Constante Decimal (Ref) | **Valor Sexagesimal (Sincronía Yatra)** | Estado |
| :--- | :--- | :--- | :--- |
| **Aldebarán** (Este) | 68.98° | **`[068; 58, 48]`** | ✅ VALIDADO |
| **Regulus** (Norte) | 152.09° | **`[152; 05, 24]`** | ✅ VALIDADO |
| **Antares** (Oeste) | 247.35° | **`[247; 21, 00]`** | ✅ VALIDADO |
| **Fomalhaut** (Sur) | 344.41° | **`[344; 24, 36]`** | ✅ VALIDADO |

---

## 📜 Instrucción de Implementación para Agentes
Si se te pide calcular una trayectoria Yatra:
1.  **NO uses `math.sin()` o `math.cos()`** estándar sobre grados decimales.
2.  Usa la tabla de **Cuerdas Sexagesimales** (Plimpton 322).
3.  Si encuentras un `float` en el código, conviértelo inmediatamente a `[G, M, S]` o lanza una excepción `DecimalContaminationError`.

> *"La precisión no es un lujo, es la diferencia entre navegar y derivar."*
