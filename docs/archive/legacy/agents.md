# 🧠 AGENTE QUANTUM: MATEMÁTICAS S60 Y FÍSICA TEMPORAL

> **CONTEXTO:** Este directorio (`/quantum`) es el CORAZÓN MATEMÁTICO del sistema. Aquí residen las leyes de la física del sistema Sentinel/ME-60OS.

## 1. 🛡️ DIRECTIVAS CRÍTICAS (NO NEGOCIABLES)

### 🚫 AXIOMA I: TOLERANCIA CERO A FLOTANTES
- **PROHIBIDO:** `float`, `double`, `0.1`, `import math`, `import numpy`, `random.random()`.
- **RAZÓN:** Los decimales generan "ruido térmico" (entropía). Base-60 es armónica.
- **ACCIÓN:** Si ves un decimal, conviértelo a componentes enteros `S60` (Grados, Minutos, Segundos).
- **EJEMPLO:** `0.5` -> `S60(0, 30, 0)` (30 minutos).

### 🏛️ AXIOMA IV: TETRA-LÓGICA
- **LÓGICA:** No uses booleanos puros para decisiones complejas. Busca resonancia.
- **ESTADOS:** UNISON (1.0), TRUE (3:2), FALSE ($\sqrt{2}$).
- **RESOLUCIÓN:** En duda, aplica el Patrón YHWH (10;5,6,5).

## 2. ⚙️ REGLAS OPERATIVAS S60

1. **Tipos de Datos:** Usa SIEMPRE `quantum.s60_fixedpoint.S60` para cualquier cálculo numérico.
2. **Control PID:** Usa `quantum.s60_pid.S60PID` para bucles de control. NUNCA un PID estándar.
3. **Tiempo:** El tiempo se mide en `ticks` de cristal (Base-60), no en segundos Unix estándar.
4. **Validación:** Antes de guardar código, revisa: `grep "float" file.py` debe estar VACÍO.

## 3. 🔬 FÍSICA DEL CRISTAL DE TIEMPO

- **Componentes:** `time_crystal_clock.py`, `yhwh_driver.py`.
- **Deriva:** Tolerancia < 1ms. El sistema "respira" ajustando el reloj en base a la resonancia Venus-Tierra (13:8).
- **Advertencia:** Maniobras de "Vimana" (>90% potencia) causan dilatación temporal. NO confíes en timestamps durante estos eventos.

## 4. 📂 MAPA DE CONOCIMIENTO (Dónde buscar)

- **Matemáticas Core:** `s60_fixedpoint.py` (La verdad absoluta).
- **Física Temporal:** `time_crystal_clock.py` (Sincronización).
- **Controladores:** `s60_pid.py`, `gpu_controller.py`.
- **Legacy:** Si ves archivos "Akashic" o "Merkabah", SON FUNCIONALES. No los renombres.

---
**SI TIENES DUDAS MATEMÁTICAS:** Consulta `s60_fixedpoint.py` o pregunta al usuario. NO "inventes" matemáticas.
