# Investigación Pendiente: Patrones de Flujo

**Fecha**: 2025-12-21  
**Estado**: Por investigar

---

## Patrón Algorítmico de Flujo

### Observación Inicial:

Del benchmark observamos un patrón de flujo que puede ser calculado matemáticamente:

```
Baseline:     f(t) = 1.2 Mbps (constante)
Precursor:    f(t) = 1.2 + (85-1.2) * (t/10)  (rampa lineal ~10s)
Burst:        f(t) = 85 Mbps (pico ~2s)
Decay:        f(t) = 85 * e^(-t/τ) (decaimiento exponencial)
```

### Hipótesis:

El flujo de datos sigue un patrón predecible que puede ser:
1. **Modelado matemáticamente** (ecuaciones diferenciales)
2. **Predicho con precisión** (conociendo parámetros)
3. **Optimizado** (minimizando drops)

### Investigaciones Propuestas:

#### 1. Análisis de Fourier del Flujo
**Objetivo**: Identificar frecuencias dominantes en el patrón de tráfico

**Método**:
```python
import numpy as np
from scipy.fft import fft, fftfreq

# Transformada de Fourier del throughput
frequencies = fftfreq(len(throughput_samples), sample_interval)
fft_values = fft(throughput_samples)

# Identificar frecuencias dominantes
dominant_freq = frequencies[np.argmax(np.abs(fft_values))]
```

**Resultado esperado**: Frecuencia de bursts (1/15s = 0.067 Hz)

---

#### 2. Modelado con Ecuaciones Diferenciales
**Objetivo**: Expresar el flujo como sistema dinámico

**Modelo**:
```
dF/dt = α(F_target - F_current) + β*noise

Donde:
- F = flujo actual
- F_target = flujo objetivo (baseline o burst)
- α = tasa de cambio
- β = factor de ruido
```

**Aplicación**: Predecir evolución del flujo sin necesidad de LSTM

---

#### 3. Cálculo de Volumen Total
**Objetivo**: Cuantificar datos totales transmitidos

**Fórmula**:
```
V_total = ∫[0,T] f(t) dt

Para nuestro patrón:
V_baseline = 1.2 * t_baseline
V_precursor = ∫ (1.2 + 83.8*t/10) dt
V_burst = 85 * t_burst
V_total = V_baseline + V_precursor + V_burst
```

**Utilidad**: Dimensionar buffers basado en volumen esperado

---

#### 4. Optimización del Buffer
**Objetivo**: Calcular tamaño óptimo de buffer para zero drops

**Enfoque**:
```
Buffer_size(t) = ∫[t, t+Δt] (f(τ) - capacity) dτ

Donde:
- f(τ) = flujo predicho
- capacity = capacidad del sistema
- Δt = ventana de predicción
```

**Resultado**: Función que da tamaño óptimo en cada momento

---

#### 5. Análisis de Estabilidad
**Objetivo**: Determinar condiciones para flujo estable

**Criterio de Lyapunov**:
```
V(F) = (F - F_equilibrium)²

dV/dt < 0  →  Sistema estable
dV/dt > 0  →  Sistema inestable
```

**Aplicación**: Detectar cuándo el sistema está por volverse inestable

---

#### 6. Teoría de Colas
**Objetivo**: Modelar buffer como sistema de colas M/M/1

**Parámetros**:
```
λ = tasa de llegada (pps)
μ = tasa de servicio (pps)
ρ = λ/μ (utilización)

Drops cuando ρ > 1
```

**Insight**: Relacionar con teoría matemática establecida

---

#### 7. Entropía del Flujo
**Objetivo**: Medir "desorden" o impredecibilidad

**Fórmula de Shannon**:
```
H(F) = -Σ p(f_i) * log₂(p(f_i))

Donde p(f_i) = probabilidad de flujo f_i
```

**Aplicación**: Cuantificar qué tan predecible es el tráfico

---

#### 8. Correlación Temporal
**Objetivo**: Medir dependencia entre muestras

**Autocorrelación**:
```
R(τ) = E[F(t) * F(t+τ)]

τ = lag temporal
```

**Resultado**: Identificar memoria del sistema (¿el flujo actual depende del pasado?)

---

## Conexión con Física:

Este patrón de flujo es análogo a:
- **Flujo de fluidos** (ecuaciones de Navier-Stokes)
- **Circuitos eléctricos** (corriente variable)
- **Ondas** (propagación de señal)

**Hipótesis**: Las mismas matemáticas que describen flujo físico pueden describir flujo de datos.

---

## Referencias a Investigar:

1. **Network Calculus** - Teoría matemática de redes
2. **Queueing Theory** - Teoría de colas
3. **Control Theory** - Teoría de control (PID, MPC)
4. **Chaos Theory** - ¿Es el tráfico caótico o predecible?

---

**Autor**: Sentinel Cortex™ Team  
**Fecha**: 2025-12-21  
**Status**: 📋 **PENDIENTE DE INVESTIGACIÓN**
