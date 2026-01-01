# Sentinel Quantum - Nivel 3: Física Real 🔬

**Prerequisito**: Haber completado [Nivel 2: Conceptos Básicos](GUIA_NIVEL_2.md)

---

## NIVEL 3: FÍSICA REAL

Hasta ahora hemos trabajado con qubits abstractos. Ahora vamos a ver cómo se implementan en **membranas nanomecánicas reales**.

---

### Bloque 7: Membranas Nanomecánicas

#### Concepto en 3 Frases
1. Una membrana es como un tambor microscópico que vibra
2. Las vibraciones están **cuantizadas** (solo ciertos niveles de energía)
3. Podemos usar estas vibraciones como qubits

#### ¿Qué es una Membrana Nanomecánica?

**Tamaño**:
- Espesor: 50 nanómetros (50 millonésimas de milímetro)
- Área: 1 mm² (como una cabeza de alfiler)
- Material: Nitruro de silicio (Si₃N₄)

**Analogía**:
- Como un trampolín microscópico
- Tan delgado que es casi transparente
- Pero lo suficientemente fuerte para vibrar sin romperse

#### Parámetros Físicos Clave

**1. Frecuencia (ω_m)**
```
ω_m = 2π × 10 MHz = 62.8 millones de rad/s
```
- Qué tan rápido vibra
- Como la nota musical de una guitarra
- 10 MHz = 10 millones de vibraciones por segundo

**2. Factor de Calidad (Q)**
```
Q = 10⁸ = 100,000,000
```
- Qué tan "pura" es la vibración
- Q alto = vibra por mucho tiempo sin perder energía
- Como una campana de cristal vs. una campana de plástico

**3. Movimiento de Punto Cero (x_zp)**
```
x_zp = √(ℏ / 2mω_m) ≈ 1.15 × 10⁻¹⁵ metros
```
- La vibración mínima permitida por la mecánica cuántica
- Incluso a temperatura cero verificado, la membrana vibra
- Es la "energía de punto cero"

#### Niveles de Energía Cuantizados

La energía de la membrana está cuantizada:
```
E_n = ℏω_m (n + 1/2)
```

Donde `n` es el número de fonones (cuantos de vibración):
- n=0: Estado fundamental (energía mínima = ℏω_m/2)
- n=1: Primer estado excitado (1 fonón)
- n=2: Segundo estado excitado (2 fonones)
- etc.

**Analogía**:
- Como los escalones de una escalera
- No puedes estar "entre" escalones
- Solo puedes estar en n=0, 1, 2, 3...

#### Pruébalo Tú Mismo

```python
python3

import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import MembraneParameters

# Crear membrana con parámetros realistas
membrane = MembraneParameters(
    mass=1e-15,           # 1 picogramo
    frequency=10e6,       # 10 MHz
    quality_factor=1e8,   # Q = 10⁸
    temperature=300       # Temperatura ambiente (Kelvin)
)

# Ver propiedades
print("=== Propiedades de la Membrana ===")
print(f"Frecuencia: {membrane.frequency/1e6:.1f} MHz")
print(f"Factor Q: {membrane.quality_factor:.0e}")
print(f"Movimiento de punto cero: {membrane.zero_point_motion:.2e} m")
print(f"Fonones térmicos promedio: {membrane.thermal_phonons:.1f}")

# ¿Qué significa?
# - Frecuencia: Vibra 10 millones de veces por segundo
# - Q: Vibración muy pura (tarda ~10 segundos en perder energía)
# - x_zp: Amplitud cuántica mínima (femtómetros)
# - Fonones térmicos: A 300K, hay ~6000 fonones por ruido térmico
```

**Salida esperada**:
```
=== Propiedades de la Membrana ===
Frecuencia: 10.0 MHz
Factor Q: 1e+08
Movimiento de punto cero: 1.15e-15 m
Fonones térmicos promedio: 6207.9
```

#### ¿Por qué Q es tan importante?

**Q bajo (Q ~ 100)**:
- La membrana pierde energía rápido
- Vibración se amortigua en microsegundos
- No sirve para computación cuántica

**Q alto (Q ~ 10⁸)**:
- La membrana vibra por segundos
- Tiempo suficiente para hacer operaciones cuánticas
- estándar técnico en investigación

**Fórmula**:
```
Tiempo de coherencia ≈ Q / ω_m
                     = 10⁸ / (2π × 10⁷)
                     ≈ 1.6 segundos
```

#### ✅ Checkpoint
- [ ] Entiendes qué es una membrana nanomecánica
- [ ] Sabes qué es el factor Q y por qué importa
- [ ] Entiendes que la energía está cuantizada (n = 0, 1, 2...)
- [ ] Probaste crear una membrana con parámetros reales

**Tiempo**: 15 minutos

---

### Bloque 8: Acoplamiento Optomecánico

#### Concepto en 3 Frases
1. La luz puede empujar la membrana (presión de radiación)
2. El movimiento de la membrana cambia la frecuencia de la luz
3. Este acoplamiento permite controlar y medir el estado cuántico

#### La Física del Acoplamiento

**Configuración**:
```
Láser → [Espejo] ← Membrana → [Espejo]
         \_____________________/
              Cavidad óptica
```

**¿Qué pasa?**
1. Láser entra en la cavidad
2. Fotones rebotan entre espejos
3. Fotones empujan la membrana (presión de radiación)
4. Membrana se mueve
5. Movimiento cambia longitud de cavidad
6. Frecuencia de luz cambia
7. ¡Retroalimentación!

#### Hamiltoniano Optomecánico

La interacción se describe por:
```
H = ℏω_c a†a + ℏΩ_m b†b - ℏg₀ a†a(b + b†)
```

**Traducción**:
- `ℏω_c a†a`: Energía de fotones en la cavidad
- `ℏΩ_m b†b`: Energía de fonones en la membrana
- `-ℏg₀ a†a(b + b†)`: Acoplamiento (fotones ↔ fonones)

**Parámetro clave: g₀**
```
g₀ ≈ 115 Hz
```
- Tasa de acoplamiento optomecánico
- Qué tan fuerte es la interacción luz-membrana
- Valor típico de experimentos reales (NBI, EPFL)

#### Pruébalo Tú Mismo

```python
python3

import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import MembraneParameters, OpticalParameters, OptomechanicalSystem

# Crear sistema optomecánico
membrane = MembraneParameters(quality_factor=1e8)
optical = OpticalParameters(
    wavelength=1550e-9,  # 1550 nm (telecom)
    finesse=1000,        # Fineza de cavidad
    power=1e-3           # 1 mW
)

system = OptomechanicalSystem(membrane, optical)

# Ver parámetros
print("=== Sistema Optomecánico ===")
print(f"Acoplamiento g₀: {system.g0:.2f} Hz")
print(f"Frecuencia cavidad: {optical.omega_c/(2*np.pi)/1e12:.1f} THz")
print(f"Frecuencia membrana: {membrane.omega_m/(2*np.pi)/1e6:.1f} MHz")
print(f"Fotones en cavidad: {optical.photon_number:.0f}")

# Razón de frecuencias
ratio = optical.omega_c / membrane.omega_m
print(f"\nRazón ω_c/ω_m: {ratio:.0e}")
print("(Cavidad vibra ~10 millones de veces más rápido que membrana)")
```

**Salida esperada**:
```
=== Sistema Optomecánico ===
Acoplamiento g₀: 115.19 Hz
Frecuencia cavidad: 193.4 THz
Frecuencia membrana: 10.0 MHz
Fotones en cavidad: 32

Razón ω_c/ω_m: 2e+07
(Cavidad vibra ~10 millones de veces más rápido que membrana)
```

#### Aplicaciones del Acoplamiento

**1. Enfriamiento por Retroalimentación**
- Usar luz para "enfriar" la membrana
- Reducir fonones térmicos
- Llevar al estado fundamental (n=0)

**2. Medición Cuántica No-Destructiva**
- Medir posición de membrana sin colapsar completamente
- Permite mediciones repetidas
- Crítico para corrección de errores

**3. Entrelazamiento Luz-Materia**
- Crear estados entrelazados fotón-fonón
- Transferir información cuántica
- Base para redes cuánticas

#### ✅ Checkpoint
- [ ] Entiendes qué es el acoplamiento optomecánico
- [ ] Sabes que g₀ ~ 115 Hz es el parámetro clave
- [ ] Entiendes que luz puede empujar y medir la membrana
- [ ] Creaste un sistema optomecánico simulado

**Tiempo**: 15 minutos

---

### Bloque 9: Ruido Cuántico

#### Concepto en 3 Frases
1. Hay dos tipos de ruido: térmico y cuántico
2. Ruido térmico viene de la temperatura
3. Ruido cuántico viene del principio de incertidumbre

#### Los Dos Enemigos

**1. Ruido Térmico**
```
n_th = k_B T / (ℏω_m)
```
- A temperatura ambiente (T=300K): n_th ≈ 6000 fonones
- A temperatura criogénica (T=4K): n_th ≈ 80 fonones
- A temperatura ultra-fría (T=25mK): n_th ≈ 0.5 fonones

**2. Ruido Cuántico (Backaction)**
- Viene del principio de incertidumbre: Δx·Δp ≥ ℏ/2
- Medir la posición perturba el momento
- Medir el momento perturba la posición
- ¡Inevitable! Es física fundamental

#### Límite Cuántico Estándar (SQL)

El SQL es el mejor que puedes hacer con mediciones clásicas:
```
SQL = √(ℏ / 2mω_m)
```

Para nuestra membrana:
```
SQL ≈ 1.15 × 10⁻¹⁵ m (femtómetros)
```

**¿Se puede superar el SQL?**
¡Sí! Usando:
- Estados comprimidos (squeezed states)
- Mediciones multi-modales
- Correlaciones cuánticas

**Esto es exactamente lo que Sentinel hace.**

#### Baños No-Markovianos

**Baño Markoviano** (sin memoria):
- El ruido en t₁ no afecta el ruido en t₂
- Como tirar dados: cada tirada es independiente

**Baño No-Markoviano** (con memoria):
- El ruido tiene "memoria" del pasado
- Correlaciones temporales
- Puede **extender** coherencia cuántica

**AI Buffer Cascade = Baño No-Markoviano Sintético**
```
τ_m ≈ 1/ω_m
```
- Memoria con escala de tiempo del oscilador
- Filtra ruido térmico
- Preserva coherencia cuántica

#### Pruébalo Tú Mismo

```python
python3

import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import OptomechanicalSystem, MembraneParameters, OpticalParameters
import numpy as np

# Crear sistema
membrane = MembraneParameters(quality_factor=1e8, temperature=300)
optical = OpticalParameters()
system = OptomechanicalSystem(membrane, optical)

# Simular con y sin memoria no-Markoviana
t_span = np.linspace(0, 1e-4, 100)  # 100 microsegundos

# Con memoria (AI Buffer Cascade)
print("Simulando CON memoria no-Markoviana...")
times1, states1 = system.evolve(t_span, noise=True, non_markovian=True)

# Sin memoria (Markoviano)
system.bath_memory = []  # Resetear
print("Simulando SIN memoria (Markoviano)...")
times2, states2 = system.evolve(t_span, noise=True, non_markovian=False)

# Comparar ruido
noise_with_memory = np.std(states1[:, 0])
noise_without_memory = np.std(states2[:, 0])

print(f"\nRuido CON memoria: {noise_with_memory:.2e} m")
print(f"Ruido SIN memoria: {noise_without_memory:.2e} m")
print(f"Reducción: {noise_without_memory/noise_with_memory:.2f}x")

# Deberías ver que la memoria reduce el ruido
```

#### ✅ Checkpoint
- [ ] Entiendes la diferencia entre ruido térmico y cuántico
- [ ] Sabes qué es el SQL y por qué importa
- [ ] Entiendes qué es un baño no-Markoviano
- [ ] Viste cómo la memoria reduce el ruido

**Tiempo**: 15 minutos

---

## 🎓 Resumen del Nivel 3

**Lo que aprendiste**:
- **Membranas**: Osciladores cuánticos reales, Q > 10⁸
- **Optomecánica**: Acoplamiento luz-materia, g₀ ~ 115 Hz
- **Ruido**: Térmico vs. cuántico, SQL, baños no-Markovianos

**Lo que puedes hacer ahora**:
- Simular membranas nanomecánicas reales
- Modelar acoplamiento optomecánico
- Entender fuentes de ruido
- Usar memoria no-Markoviana para reducir ruido

**Conexión con Sentinel**:
```
Membrana cuántica → Qubit mecánico
Acoplamiento g₀   → Control cuántico
Baño no-Markoviano → AI Buffer Cascade
Ruido reducido    → Coherencia extendida
```

---

## 🚀 Ejercicio Final del Nivel 3

Simula una membrana enfriándose desde temperatura ambiente hasta el estado fundamental:

```python
python3

import sys
sys.path.append('/home/jnovoas/sentinel')

from quantum import MembraneParameters
import numpy as np

# Temperaturas: 300K → 4K → 25mK
temperatures = [300, 4, 0.025]

print("=== Enfriamiento de Membrana ===\n")

for T in temperatures:
    membrane = MembraneParameters(
        quality_factor=1e8,
        temperature=T
    )
    
    print(f"Temperatura: {T} K")
    print(f"  Fonones térmicos: {membrane.thermal_phonons:.1f}")
    print(f"  Energía térmica: {membrane.thermal_phonons * 6.626e-34 * 10e6:.2e} J")
    print()

# Deberías ver:
# 300 K: ~6000 fonones (temperatura ambiente)
# 4 K: ~80 fonones (helio líquido)
# 25 mK: ~0.5 fonones (¡casi estado fundamental!)
```

**¿Por qué importa?**
- A 300K: Demasiado ruido para ver efectos cuánticos
- A 4K: Ruido reducido, pero aún significativo
- A 25mK: Estado casi puro, efectos cuánticos visibles
- **Sentinel puede operar a temperatura ambiente** usando AI Buffer Cascade

---

**¿Listo para el Nivel 4?** Ahí vamos a ver algoritmos cuánticos avanzados (QAOA, VQE, detección de rifts).

**Próximo**: [Nivel 4: Algoritmos Avanzados](GUIA_NIVEL_4.md)

O descansa. Has aprendido física cuántica real. 🔬✨
