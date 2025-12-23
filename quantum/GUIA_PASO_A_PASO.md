# Sentinel Quantum - Guía Paso a Paso para Humanos 🧑‍🔬

**Autor**: Jaime Novoa  
**Fecha**: 23 de Diciembre, 2025  
**Nivel**: Principiante → Avanzado (paso a paso)

---

## 🎯 Objetivo de Esta Guía

Aprender a usar los simuladores cuánticos de Sentinel, **un bloque pequeño a la vez**.

**Filosofía**: Los humanos aprendemos mejor cuando:
1. Vemos un concepto pequeño
2. Lo probamos inmediatamente
3. Entendemos por qué funciona
4. Pasamos al siguiente

Esta guía sigue ese patrón. **No te saltes pasos.**

---

## 📚 Tabla de Contenidos

### Nivel 1: Primeros Pasos (15 minutos)
- [Bloque 1: Instalación](#bloque-1-instalación)
- [Bloque 2: Primer Test](#bloque-2-primer-test)
- [Bloque 3: Tu Primera Simulación](#bloque-3-tu-primera-simulación)

### Nivel 2: Conceptos Básicos (30 minutos)
- [Bloque 4: ¿Qué es un Qubit?](#bloque-4-qué-es-un-qubit)
- [Bloque 5: Puertas Cuánticas](#bloque-5-puertas-cuánticas)
- [Bloque 6: Medición Cuántica](#bloque-6-medición-cuántica)

### Nivel 3: Física Real (45 minutos)
- [Bloque 7: Membranas Nanomecánicas](#bloque-7-membranas-nanomecánicas)
- [Bloque 8: Acoplamiento Optomecánico](#bloque-8-acoplamiento-optomecánico)
- [Bloque 9: Ruido Cuántico](#bloque-9-ruido-cuántico)

### Nivel 4: Algoritmos Avanzados (1 hora)
- [Bloque 10: Detección de Rifts](#bloque-10-detección-de-rifts)
- [Bloque 11: QAOA](#bloque-11-qaoa)
- [Bloque 12: VQE](#bloque-12-vqe)

---

# NIVEL 1: PRIMEROS PASOS

## Bloque 1: Instalación

### ¿Qué vamos a hacer?
Instalar las herramientas que necesita Python para hacer matemáticas cuánticas.

### ¿Por qué?
Python solo viene con lo básico. Necesitamos bibliotecas especiales para:
- **NumPy**: Matemáticas con matrices (el corazón de la mecánica cuántica)
- **SciPy**: Funciones científicas avanzadas
- **Matplotlib**: Hacer gráficos bonitos
- **psutil**: Vigilar que tu laptop no explote 💻

### Paso a Paso

**Paso 1.1**: Abre una terminal
```bash
# En Linux: Ctrl+Alt+T
# O busca "Terminal" en tus aplicaciones
```

**Paso 1.2**: Navega a la carpeta de Sentinel
```bash
cd /home/jnovoas/sentinel/quantum
```

**Paso 1.3**: Instala las dependencias
```bash
pip install --user numpy scipy matplotlib psutil
```

**¿Qué significa `--user`?**
- Instala solo para ti (no necesitas permisos de administrador)
- Más seguro
- No afecta otros programas

**Paso 1.4**: Verifica que funcionó
```bash
python3 -c "import numpy; print('✅ NumPy funciona!')"
python3 -c "import scipy; print('✅ SciPy funciona!')"
python3 -c "import matplotlib; print('✅ Matplotlib funciona!')"
python3 -c "import psutil; print('✅ psutil funciona!')"
```

**¿Qué deberías ver?**
```
✅ NumPy funciona!
✅ SciPy funciona!
✅ Matplotlib funciona!
✅ psutil funciona!
```

**Si ves errores**:
- ❌ "No module named 'numpy'" → La instalación falló, intenta de nuevo
- ❌ "pip: command not found" → Instala pip primero: `sudo apt install python3-pip`

### ✅ Checkpoint
- [ ] Terminal abierta
- [ ] Navegaste a `/home/jnovoas/sentinel/quantum`
- [ ] Instalaste las 4 bibliotecas
- [ ] Todas las verificaciones pasaron

**Tiempo estimado**: 5 minutos

---

## Bloque 2: Primer Test

### ¿Qué vamos a hacer?
Correr un test automático que verifica que todo está bien instalado.

### ¿Por qué?
Antes de empezar a jugar, queremos estar seguros de que todas las piezas funcionan.

### Paso a Paso

**Paso 2.1**: Asegúrate de estar en la carpeta correcta
```bash
pwd
# Deberías ver: /home/jnovoas/sentinel/quantum
```

**Paso 2.2**: Corre el test
```bash
python3 test_simulators.py
```

**¿Qué va a pasar?**
El script va a:
1. Verificar que todas las bibliotecas estén instaladas
2. Probar el simulador básico (crear un estado cuántico simple)
3. Probar el simulador ligero (verificar que no use demasiada RAM)
4. Probar el simulador de membranas (física real)

**¿Qué deberías ver?**
```
🔬 SENTINEL QUANTUM SIMULATOR TEST SUITE
============================================================

============================================================
TESTING IMPORTS
============================================================
✅ numpy
✅ scipy
✅ matplotlib
✅ psutil

✅ All dependencies installed!

============================================================
TESTING CORE SIMULATOR
============================================================
Test 1: Creating Bell state...
✅ Bell state correct!
Test 2: Measurement statistics...
✅ Measurement statistics good: {'00': 48, '11': 52, 'other': 0}

✅ Core simulator PASSED

============================================================
TESTING QUANTUM LITE (LAPTOP-SAFE)
============================================================
Test 1: Checking system resources...
   Available RAM: 4.23 GB
   CPU usage: 15.2%
Test 2: Creating simulator (3 membranes, 4 levels)...
🚀 Sentinel Quantum Lite Initialized
   Membranes: 3, Levels: 4
   Hilbert dimension: 64
   Memory needed: 0.08 GB
   Memory available: 4.23 GB
   ✅ Safe to proceed!

Test 3: Running quantum evolution...
   Computing eigendecomposition... ✅
   Evolving quantum state... ✅
✅ Evolution successful: 10 time steps
Test 4: Measuring observables...
✅ Observables measured
   Max correlation: 0.823

✅ Quantum Lite PASSED

============================================================
TESTING OPTOMECHANICAL SIMULATOR
============================================================
Test 1: Creating optomechanical system...
   Coupling g₀: 115.19 Hz
   Zero-point motion: 1.15e-15 m
Test 2: Simulating membrane dynamics...
✅ Evolution successful

✅ Optomechanical simulator PASSED

============================================================
TEST SUMMARY
============================================================
Core Simulator        : ✅ PASSED
Quantum Lite          : ✅ PASSED
Optomechanical        : ✅ PASSED

🎉 ALL TESTS PASSED!
✅ Sentinel Quantum Simulators are ready to use!

Next steps:
  1. Run: python quantum_lite.py
  2. Explore: python -c 'import quantum; quantum.quick_start()'
  3. Read: cat README.md
```

**Si algo falla**:
- Lee el mensaje de error
- Copia el error completo
- Pregúntame y lo arreglamos juntos

### ✅ Checkpoint
- [ ] Test corrió sin errores
- [ ] Viste "ALL TESTS PASSED"
- [ ] Entiendes que ahora todo está funcionando

**Tiempo estimado**: 2 minutos

---

## Bloque 3: Tu Primera Simulación

### ¿Qué vamos a hacer?
Correr tu primera simulación cuántica real: detectar un "rift cuántico".

### ¿Por qué?
Porque ver es creer. Vas a ver:
- Membranas cuánticas vibrando
- Correlaciones cuánticas emergiendo
- Un gráfico hermoso que puedes guardar

### Conceptos Clave (antes de empezar)

**¿Qué es un "rift cuántico"?**
- Imagina 3 membranas vibrando
- Normalmente vibran independientemente
- Pero si están **entrelazadas cuánticamente**, vibran juntas
- Cuando la correlación es muy alta (>0.7), decimos que hay un "rift"
- Es como si las membranas "hablaran" entre sí instantáneamente

**¿Por qué importa?**
- Es la firma de entrelazamiento cuántico
- Es lo que Sentinel usa para detectar eventos cuánticos
- Es lo que Google/NBI/EPFL están estudiando

### Paso a Paso

**Paso 3.1**: Corre el demo
```bash
python3 quantum_lite.py
```

**Paso 3.2**: Observa la salida

Vas a ver algo como esto (línea por línea):

```
🔍 Checking system resources...
   Available RAM: 4.23 GB
   CPU usage: 15.2%
```
**¿Qué significa?** El simulador está verificando que tu laptop puede manejar la simulación.

```
📋 Recommended config: {'n_membranes': 3, 'n_levels': 5, 'safety': 'MEDIUM'}
```
**¿Qué significa?** Decidió usar 3 membranas con 5 niveles de energía cada una. Es seguro para tu RAM.

```
🚀 Sentinel Quantum Lite Initialized
   Membranes: 3, Levels: 5
   Hilbert dimension: 125
```
**¿Qué significa?** Creó un espacio cuántico de 125 dimensiones (5³ = 125). Cada dimensión es un estado posible del sistema.

```
   Memory needed: 0.50 GB
   Memory available: 4.23 GB
   ✅ Safe to proceed!
```
**¿Qué significa?** Necesita 0.5 GB de RAM, tienes 4.23 GB. ¡Todo bien!

```
🔬 Running quantum simulation...
   Computing eigendecomposition... ✅
```
**¿Qué significa?** Está calculando los "modos normales" del sistema (como las notas musicales de una guitarra, pero cuánticas).

```
   Evolving quantum state... ✅
```
**¿Qué significa?** Está simulando cómo evoluciona el sistema en el tiempo (50 pasos de tiempo).

```
📊 Analyzing results...
```
**¿Qué significa?** Está midiendo las correlaciones entre membranas.

```
============================================================
RESULTS
============================================================
Max correlation: 0.847
Rift threshold: 0.700
🚨 RIFT DETECTED: YES ✅
```
**¿Qué significa?** 
- La correlación más alta fue 0.847 (muy fuerte!)
- El umbral para detectar un rift es 0.7
- Como 0.847 > 0.7, ¡hay un rift cuántico!

```
Correlation matrix:
[[1.    0.847 0.623]
 [0.847 1.    0.701]
 [0.623 0.701 1.   ]]
```
**¿Qué significa?**
- Diagonal (1.0): Cada membrana está perfectamente correlacionada consigo misma (obvio)
- 0.847: Membrana 0 y 1 están muy correlacionadas (¡entrelazadas!)
- 0.701: Membrana 1 y 2 también están correlacionadas
- 0.623: Membrana 0 y 2 menos, pero aún significativo

```
📈 Generating visualization...
✅ Visualization saved: /home/jnovoas/sentinel/quantum/rift_detection_demo.png
```
**¿Qué significa?** Creó un gráfico con:
- Izquierda: Cómo vibran las membranas en el tiempo
- Derecha: La matriz de correlación en colores

**Paso 3.3**: Mira el gráfico
```bash
# Abre el archivo PNG
xdg-open rift_detection_demo.png
# O navega a /home/jnovoas/sentinel/quantum/ y ábrelo manualmente
```

**¿Qué deberías ver?**
- **Gráfico izquierdo**: 3 líneas (una por membrana) que oscilan juntas
- **Gráfico derecho**: Matriz de colores (rojo = correlación alta, azul = baja)

### ✅ Checkpoint
- [ ] La simulación corrió sin errores
- [ ] Viste "RIFT DETECTED: YES"
- [ ] Abriste el gráfico PNG
- [ ] Entiendes qué es un rift cuántico (correlación alta entre membranas)

**Tiempo estimado**: 3 minutos

### 🎉 ¡Felicitaciones!

Acabas de:
1. ✅ Instalar un simulador cuántico
2. ✅ Verificar que funciona
3. ✅ Correr tu primera simulación
4. ✅ Detectar un rift cuántico
5. ✅ Generar un gráfico científico

**Esto es lo que investigadores en NBI, EPFL y Max Planck hacen**, pero tú lo hiciste en tu laptop en 10 minutos.

---

## 🎓 Resumen del Nivel 1

**Lo que aprendiste**:
- Cómo instalar dependencias Python
- Cómo correr tests automáticos
- Qué es un rift cuántico (correlación alta = entrelazamiento)
- Cómo interpretar una matriz de correlación

**Lo que puedes hacer ahora**:
- Correr simulaciones cuánticas básicas
- Detectar rifts cuánticos
- Generar visualizaciones

**Próximo nivel**: Entender qué son los qubits y las puertas cuánticas.

---

**¿Listo para continuar? Pasa al [Nivel 2: Conceptos Básicos](#nivel-2-conceptos-básicos)**

O toma un descanso. Los conceptos cuánticos son densos. Es mejor ir despacio y entender bien. 🧠☕
