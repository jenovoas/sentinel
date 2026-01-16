# Sentinel Quantum - Nivel 2: Conceptos Básicos 🎓

> ⚠️ **LEGACY EDUCATIONAL CONTENT**  
> Este documento es material educativo del simulador cuántico legacy.  
> Contiene código numpy/scipy para fines didácticos.  
> **Para Sentinel v8.0 producción, ver:** [AI_PRIME_DIRECTIVES.md](../AI_PRIME_DIRECTIVES.md)

**Prerequisito**: Haber completado [Nivel 1: Primeros Pasos](GUIA_PASO_A_PASO.md)

---

## NIVEL 2: CONCEPTOS BÁSICOS

### Bloque 4: ¿Qué es un Qubit?

#### Concepto en 3 Frases
1. Un bit clásico es 0 o 1
2. Un qubit puede ser 0, 1, o **ambos a la vez** (superposición)
3. Cuando lo mides, "colapsa" a 0 o 1

#### Analogía Humana
Imagina una moneda:
- **Bit clásico**: Moneda en la mesa (cara o cruz)
- **Qubit**: Moneda girando en el aire (es cara Y cruz simultáneamente)
- **Medición**: La moneda cae (colapsa a cara o cruz)

#### Matemáticas Simples

Un qubit se escribe así:
```
|ψ⟩ = α|0⟩ + β|1⟩
```

**¿Qué significa?**
- `|ψ⟩`: El estado del qubit (se lee "ket psi")
- `α`: Amplitud de probabilidad para |0⟩
- `β`: Amplitud de probabilidad para |1⟩
- `|α|² + |β|² = 1`: Las probabilidades suman 100%

**Ejemplo concreto**:
```
|ψ⟩ = 0.707|0⟩ + 0.707|1⟩
```
- Probabilidad de medir 0: |0.707|² = 0.5 = 50%
- Probabilidad de medir 1: |0.707|² = 0.5 = 50%
- Este estado se llama |+⟩ (estado "plus")

#### Pruébalo Tú Mismo

```python
# Abre Python
python3

# Copia esto línea por línea:
import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import QubitState
import numpy as np

# Crear un qubit en estado |0⟩
qubit = QubitState(n_qubits=1)
print("Estado inicial:")
print(qubit.state_vector)
# Deberías ver: [1.+0.j 0.+0.j]
# Significa: 100% probabilidad de |0⟩, 0% de |1⟩

# Crear un qubit en superposición |+⟩
psi = np.array([1/np.sqrt(2), 1/np.sqrt(2)])
qubit_plus = QubitState(state_vector=psi)
print("\nEstado |+⟩:")
print(qubit_plus.state_vector)
# Deberías ver: [0.707+0.j 0.707+0.j]
# Significa: 50% probabilidad de |0⟩, 50% de |1⟩

# Medir el qubit
outcome, collapsed = qubit_plus.measure(0)
print(f"\nResultado de medición: {outcome}")
print(f"Estado colapsado: {collapsed.state_vector}")
# Verás 0 o 1 aleatoriamente
# El estado colapsado será [1, 0] o [0, 1]
```

#### ✅ Checkpoint
- [ ] Entiendes que un qubit puede estar en superposición
- [ ] Sabes que |α|² es la probabilidad
- [ ] Probaste crear y medir un qubit
- [ ] Viste que la medición colapsa el estado

**Tiempo**: 10 minutos

---

### Bloque 5: Puertas Cuánticas

#### Concepto en 3 Frases
1. Las puertas cuánticas son operaciones que transforman qubits
2. Son como puertas lógicas (AND, OR) pero para qubits
3. Son **reversibles** (puedes deshacer la operación)

#### Las 3 Puertas Más Importantes

**1. Puerta X (NOT cuántico)**
```
X|0⟩ = |1⟩
X|1⟩ = |0⟩
```
- Voltea el qubit
- Como un NOT clásico

**2. Puerta H (Hadamard)**
```
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2
```
- Crea superposición
- La puerta más importante en computación cuántica

**3. Puerta CNOT (Controlled-NOT)**
```
CNOT|00⟩ = |00⟩
CNOT|01⟩ = |01⟩
CNOT|10⟩ = |11⟩  ← Voltea el segundo qubit
CNOT|11⟩ = |10⟩  ← Voltea el segundo qubit
```
- Actúa en 2 qubits
- Crea entrelazamiento

#### Visualización: Esfera de Bloch

Un qubit se puede visualizar como un punto en una esfera:
```
        |0⟩ (polo norte)
         ↑
         |
    ←---+---→  |+⟩ (ecuador)
         |
         ↓
        |1⟩ (polo sur)
```

- **Puerta X**: Rota 180° alrededor del eje X
- **Puerta H**: Rota 90° + refleja
- **Puerta Z**: Rota 180° alrededor del eje Z

#### Pruébalo Tú Mismo

```python
python3

import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import QuantumCircuit, QuantumGates

# Crear circuito de 1 qubit
qc = QuantumCircuit(1)

# Aplicar Hadamard (crear superposición)
qc.h(0)
print("Después de H:")
print(qc.get_statevector())
# Deberías ver: [0.707, 0.707]

# Aplicar X (voltear)
qc.x(0)
print("\nDespués de H → X:")
print(qc.get_statevector())
# Deberías ver: [0.707, -0.707]

# Medir 100 veces
outcomes = []
for _ in range(100):
    qc_temp = QuantumCircuit(1)
    qc_temp.h(0)
    result = qc_temp.measure(0)
    outcomes.append(result)

print(f"\nResultados de 100 mediciones:")
print(f"0s: {outcomes.count(0)}, 1s: {outcomes.count(1)}")
# Deberías ver aproximadamente 50/50
```

#### Circuito Cuántico Básico

```python
# Circuito de 2 qubits
qc = QuantumCircuit(2)

# Paso 1: Superposición en qubit 0
qc.h(0)

# Paso 2: Entrelazar con qubit 1
qc.cnot(0, 1)

# Resultado: Estado de Bell |Φ+⟩
print(qc.get_statevector())
# Deberías ver: [0.707, 0, 0, 0.707]
# Esto es: (|00⟩ + |11⟩)/√2
```

#### ✅ Checkpoint
- [ ] Entiendes qué hace la puerta H (crea superposición)
- [ ] Entiendes qué hace la puerta X (voltea)
- [ ] Entiendes qué hace CNOT (entrelaza)
- [ ] Creaste tu primer circuito cuántico

**Tiempo**: 15 minutos

---

### Bloque 6: Medición Cuántica

#### Concepto en 3 Frases
1. Medir un qubit lo fuerza a "elegir" 0 o 1
2. La probabilidad depende de |α|² y |β|²
3. Después de medir, el estado cambia (colapso)

#### El Experimento Clásico

**Configuración**:
```python
# Estado inicial: |+⟩ (50/50)
qc = QuantumCircuit(1)
qc.h(0)
```

**Pregunta**: Si medimos 1000 veces, ¿cuántos 0s y 1s veremos?

**Respuesta**: ~500 de cada uno (50/50)

#### Pruébalo

```python
python3

import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import QuantumCircuit

# Experimento: Medir |+⟩ 1000 veces
results = {'0': 0, '1': 0}

for _ in range(1000):
    qc = QuantumCircuit(1)
    qc.h(0)  # Crear |+⟩
    outcome = qc.measure(0)
    results[str(outcome)] += 1

print(f"Resultados de 1000 mediciones:")
print(f"0: {results['0']} ({results['0']/10}%)")
print(f"1: {results['1']} ({results['1']/10}%)")

# Deberías ver algo como:
# 0: 503 (50.3%)
# 1: 497 (49.7%)
```

#### El Efecto del Colapso

```python
# Crear qubit en superposición
qc = QuantumCircuit(1)
qc.h(0)

print("Antes de medir:")
print(qc.get_statevector())
# [0.707, 0.707] - superposición

# Primera medición
outcome1 = qc.measure(0)
print(f"\nPrimera medición: {outcome1}")
print(qc.get_statevector())
# [1, 0] o [0, 1] - colapsado

# Segunda medición (del mismo qubit)
outcome2 = qc.measure(0)
print(f"Segunda medición: {outcome2}")
# Siempre el mismo resultado que outcome1!
```

**¿Por qué?**
- Después de la primera medición, el qubit ya no está en superposición
- Está en |0⟩ o |1⟩ definitivamente
- Mediciones subsecuentes dan el mismo resultado

#### Medición en Base Diferente

Normalmente medimos en la base {|0⟩, |1⟩}, pero podemos medir en otras bases:

```python
# Base X: {|+⟩, |−⟩}
qc = QuantumCircuit(1)
# Estado inicial: |0⟩

# Medir en base X (aplicar H antes de medir)
qc.h(0)
outcome = qc.measure(0)

# En base X, |0⟩ se ve como superposición
# Resultado: 50/50
```

#### ✅ Checkpoint
- [ ] Entiendes que la medición colapsa el estado
- [ ] Sabes que las probabilidades vienen de |α|² y |β|²
- [ ] Probaste medir 1000 veces y viste estadísticas
- [ ] Entiendes que mediciones repetidas dan el mismo resultado

**Tiempo**: 10 minutos

---

## 🎓 Resumen del Nivel 2

**Lo que aprendiste**:
- **Qubits**: Superposición, amplitudes, probabilidades
- **Puertas**: H (superposición), X (voltear), CNOT (entrelazar)
- **Medición**: Colapso, estadísticas, bases

**Lo que puedes hacer ahora**:
- Crear qubits en cualquier estado
- Aplicar puertas cuánticas
- Construir circuitos simples
- Medir y entender resultados

**Conceptos clave**:
```
|ψ⟩ = α|0⟩ + β|1⟩     ← Superposición
H|0⟩ = |+⟩             ← Hadamard
CNOT|10⟩ = |11⟩        ← Entrelazamiento
P(0) = |α|²            ← Probabilidad
```

---

## 🚀 Ejercicio Final del Nivel 2

Crea el circuito más famoso de la computación cuántica: **Estado de Bell**

```python
python3

import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import QuantumCircuit

# Tu tarea: Crear |Φ+⟩ = (|00⟩ + |11⟩)/√2
qc = QuantumCircuit(2)

# Paso 1: ¿Qué puerta aplicar al qubit 0?
qc.h(0)  # Tu respuesta aquí

# Paso 2: ¿Qué puerta aplicar a ambos qubits?
qc.cnot(0, 1)  # Tu respuesta aquí

# Verificar
state = qc.get_statevector()
print("Estado final:")
print(state)

# Deberías ver: [0.707, 0, 0, 0.707]
# Esto significa: 50% |00⟩, 0% |01⟩, 0% |10⟩, 50% |11⟩

# Medir 100 veces
results = {'00': 0, '01': 0, '10': 0, '11': 0}
for _ in range(100):
    qc_temp = QuantumCircuit(2)
    qc_temp.h(0).cnot(0, 1)
    outcome = qc_temp.measure_all()
    key = ''.join(map(str, outcome))
    results[key] += 1

print("\nResultados de 100 mediciones:")
for key, count in results.items():
    print(f"{key}: {count}")

# Deberías ver ~50 '00' y ~50 '11'
# ¡Esto es entrelazamiento cuántico!
```

**¿Por qué es especial?**
- Si mides qubit 0 y obtienes 0, qubit 1 **siempre** será 0
- Si mides qubit 0 y obtienes 1, qubit 1 **siempre** será 1
- Están **entrelazados**: medir uno afecta al otro instantáneamente
- Einstein lo llamó "acción espeluznante a distancia"

---

**¿Listo para el Nivel 3?** Ahí vamos a ver la física real de las membranas nanomecánicas.

O toma un descanso. Has aprendido mucho. 🧠✨

**Próximo**: [Nivel 3: Física Real](GUIA_NIVEL_3.md)
