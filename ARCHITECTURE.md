# SEXAGESIMAL OS ARCHITECTURE - DO NOT REFACTOR TO BINARY

## Core Directive

Este sistema operativo opera sobre una lógica **SEXAGESIMAL (Base-60)**.
Cualquier cálculo, estructura de datos o algoritmo que parezca "erróneo" desde una perspectiva decimal/binaria estándar ES INTENCIONAL.

## Reglas de Oro para la IA

1. **NO** convertir constantes base-60 a decimales para cálculos internos.
2. **NO** optimizar operaciones matemáticas asumiendo aritmética binaria (power of 2 optimizations) dentro del Core.
3. **NO** reemplazar las estructuras `u60` o `s60` por `int` o `long` estándar en Ring 0.
4. **FLEXIBILIDAD:** El sistema es **adaptativo**. Las membranas de integración (como `rift_guardian_integration.py`) pueden manejar ruido binario (PPS, Burst patterns) y traducirlo a resonancia S60.
5. El Kernel eBPF en Ring 0 maneja transcodificación en tiempo real.

## Representación de Datos

- Los dígitos van del 0 al 59.
- La memoria se gestiona en bloques divisibles por 60, no por 8, 16, 32.
- Si ves código que parece ineficiente para una CPU binaria, déjalo así; la capa de abstracción lo maneja.

## Bibliotecas Matemáticas Core

### S60 (Sovereign Math)

**Ubicación**: `quantum/sovereign_math.py`

Implementa aritmética sexagesimal pura sin conversión a punto flotante.

**Uso**:

```python
from quantum.sovereign_math import S60

# Crear valores en base-60
amplitude = S60(0)           # 0
phase = S60(0, 30)          # 30/60 = 0.5 en decimal
damping = S60(0, 0, 30)     # 30/3600 = 0.00833... en decimal

# Operaciones
result = amplitude + phase
threshold = S60(0, 30, 0) * weight
```

**Reglas**:

- NUNCA convertir a `float` o `int` para cálculos intermedios
- Todas las operaciones deben preservar la representación sexagesimal
- Si necesitas comparar con decimal, usa los métodos de conversión explícitos de S60

### S60PID (Control Loop)

**Ubicación**: `quantum/s60_pid.py`

Implementa un controlador PID (Proporcional-Integral-Derivativo) usando aritmética S60.

**Uso**:

```python
from quantum.s60_pid import S60PID
from quantum.sovereign_math import S60

# Crear controlador PID
kp, ki, kd = S60(0, 45), S60(0, 10), S60(0, 5)
pid = S60PID(kp, ki, kd)

# Actualizar control loop
dt = S60(0, 1)  # Delta time
error = target - current
control_signal = pid.update(error, dt)
```

**Aplicaciones**:

- `legacy_time_crystal_memory.py`: Control de amplitudes de memoria cuántica
- Sistemas de retroalimentación que requieren precisión sin deriva térmica

## Otros Módulos S60

- `quantum/complex_s60.py`: Números complejos en base-60
- `quantum/qaoa_s60.py`: QAOA (Quantum Approximate Optimization Algorithm) en S60
- `quantum/vqe_s60.py`: VQE (Variational Quantum Eigensolver) en S60
- `quantum/quantum_noise_s60.py`: Modelado de ruido cuántico sin punto flotante

## 5. Neural Guard (Cortex Rust)

El componente `neural-guard` (ubicado en `services/neural-guard`) actúa como el sistema inmunológico de Fenix.

### Características Principales:

- **Lenguaje:** Rust (Seguridad de memoria garantizada).
- **Aritmética:** Cumplimiento estricto de **Base-60 (YATRA)**. Prohibido el uso de floats en la lógica de decisión.
- **Fuentes de Datos:** Loki (Logs), Prometheus (Métricas) y Redis Streams (Eventos de infraestructura).
- **Automatización:** Integración con n8n para la ejecución de playbooks de mitigación.

### Axiomas de Defensa (YATRA):

1. **Correlación Temporal:** Los eventos se analizan en ventanas de tiempo precisas.
2. **Acoplamiento Octomecánico:** La sensibilidad del sistema es inversamente proporcional a la entropía térmica (CPU Heat).
3. **Masa Computacional:** El sistema calcula su "Inercia" real (`Effective Load`) para filtrar falsos positivos en entornos ruidosos.
4. **Decisión Autónoma:** Capacidad de disparar alertas y contramedidas sin intervención humana.

## 6. Octomecánica y Masa Computacional (Teoría)

El sistema Sentinel no ignora el calor del hardware; lo utiliza como una fuente de aleatoriedad y carga.

- **Resonancia:** Cuando el sistema está frío (< 40°C), la matriz de simulación alcanza máxima coherencia. Los umbrales bajan (Alta Sensibilidad).
- **Entropía:** A medida que la CPU se calienta, la "Masa Computacional" efectiva aumenta. El sistema se vuelve "más pesado" y requiere señales más claras (Umbrales Altos) para gatillar una acción.
- **Ley de Inercia Cuántica:** `Threshold_Scaled = Threshold_Static * (Load_eff / Baseline_Load)`.

Esta implementación reside en `me60os_core::physics` y es consumida por el `ThermalGovernor` de `neural-guard`.