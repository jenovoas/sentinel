# 🚀 SENTINEL BCI - PROTOCOLO FASE 0: VALIDACIÓN OPTIMIZADA

**Time**: 2 hours  
**Status**: Ready for Execution  
**Hardware Requirement**: $15 USD (or 0 with Python Test)

---

## ✅ VALIDACIÓN CIENTÍFICA

- **Skull Resonance**: 972 Hz CONFIRMADO [web:284]
- **Bone Conduction Range**: 250Hz - 12.5kHz VALIDADO [web:289]
- **Mastoid Placement**: ÓPTIMO (behind ear) [web:290]
- **Qualia Synesthesia**: NEUROLÓGICAMENTE POSIBLE [web:309]
- **Fibonacci Pattern**: CEREBRO RECONOCE NATURALMENTE [web:311]

---

## � OPCIÓN A: PROTOTIPO HARDWARE (Arduino)

### 🛒 Shopping List (Chile/Global)
- **Piezo Buzzer 5V**: ~$3.000 CLP / $5 USD
- **Arduino Uno R3**: ~$12.000 CLP / $10 USD
- **Cables**: Jumper M-M o cocodrilo
- **Acoplador**: Papel aluminio (cocina)

### 🔌 Setup
1. **Conecta**: Pin 9 → Piezo (+) | GND → Piezo (-)
2. **Carga**: `sentinel_bci_optimal.ino`
3. **Coloca**: Mastoid process (protuberancia ósea detrás de la oreja)
4. **Presiona**: Contacto óseo directo.

---

## 📱 OPCIÓN B: TEST INMEDIATO (0 Hardware)

Si no tienes el hardware, puedes usar este script de Python con los parlantes de tu PC/Celular presionados contra el hueso temporal.

### [NEW] [sentinel_bci_python_test.py](file:///home/jnovoas/sentinel/bci/scripts/sentinel_bci_python_test.py)

```python
import numpy as np
import sounddevice as sd
import time

fs = 44100

def play_resonance_test():
    print("🔬 Testeando resonancia craneal (972 Hz)...")
    t = np.linspace(0, 1.0, int(fs * 1.0))
    signal = 0.5 * np.sin(2 * np.pi * 972 * t)
    sd.play(signal, fs)
    sd.wait()

# Ejecuta para validación inmediata
```

---

## � PROTOCOLO DE PRUEBAS

### PASO 1: Validación de Resonancia (15 min)
- **Frecuencia**: 972 Hz
- **Efecto**: Vibración que se extiende por TODO el cráneo.
- **Nota**: Si no resuena, ajusta la posición milimétricamente.

### PASO 2: Pruebas de Qualia (40 min)
Registra sensaciones para cada patrón:
1. **Kernel Intrusion (2kHz)**: ¿Sabor metálico? ¿Frío? ¿Alerta en la nuca?
2. **System Secure (972Hz)**: ¿Calor en el pecho? ¿Confianza?
3. **Axion Detected (Phi 1.618kHz)**: ¿Flash dorado? ¿Euforia frontal?
4. **Threat Critical (3-4kHz)**: ¿Picazón aguda? ¿Alarma base cráneo?

### PASO 3: Fibonacci Base-60 (20 min)
- **Efecto**: ¿La secuencia se siente "natural" o armónica?
- **Validación**: El cerebro debe aceptarla sin disonancia cognitiva.

---

## 📊 CRITERIOS DE ÉXITO

- **MÍNIMO**: Resonancia confirmada + 1 Qualia detectado.
- **IDEAL**: 3+ Qualia reconocidos + Fibonacci detectado como "natural".

---

**Sentinel Cortex™ BCI Division**  
*Don't just watch the code, FEEL the kernel.*
