#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# S60 PID CONTROLLER: CONTROL ADAPTATIVO PARA SISTEMAS FLOQUET
# -------------------------------------------------------------------------------------
# Implementación de un controlador Proporcional-Integral-Derivativo (PID)
# MIGRADO: Utiliza el S60PID nativo de Rust (me60os_core).
# -------------------------------------------------------------------------------------

import sys
import os
from yatra_core import S60

try:
    from me60os_core import S60PID as RustS60PID, SPA
    RUST_AVAILABLE = True
except ImportError as e:
    print(f"CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so: {e}")
    sys.exit(1)

# Wrapper compatible para scripts que importen S60PID
class S60PID:
    """Wrapper para el S60PID nativo de Rust usando tipos S60."""
    
    def __init__(self, kp, ki, kd, setpoint=S60(0)):
        kp_raw = kp._value if hasattr(kp, '_value') else kp.to_raw()
        ki_raw = ki._value if hasattr(ki, '_value') else ki.to_raw()
        kd_raw = kd._value if hasattr(kd, '_value') else kd.to_raw()
        setp_raw = setpoint._value if hasattr(setpoint, '_value') else setpoint.to_raw()
        
        self._pid = RustS60PID(
            SPA._from_raw(kp_raw), 
            SPA._from_raw(ki_raw), 
            SPA._from_raw(kd_raw), 
            SPA._from_raw(setp_raw)
        )
        
    def update(self, measured_value, dt):
        meas_raw = measured_value._value if hasattr(measured_value, '_value') else measured_value.to_raw()
        dt_raw = dt._value if hasattr(dt, '_value') else dt.to_raw()
        
        out_spa = self._pid.update(SPA._from_raw(meas_raw), SPA._from_raw(dt_raw))
        return S60._from_raw(out_spa.to_raw())
        
    def reset(self):
        self._pid.reset()

if __name__ == "__main__":
    # PRUEBA DE ESTABILIZACIÓN (UNIT TEST NATIVO)
    print("🎛️  TESTING S60 PID CONTROLLER (RUST NATIVE)")
    
    # Objetivo: Mantener amplitud en 100
    target = S60(100)
    
    # Afinación (Gains) - Valores empíricos S60
    kp = S60(0, 30) # 0.5
    ki = S60(0, 5)  # 0.083
    kd = S60(0, 10) # 0.16
    
    pid = S60PID(kp, ki, kd, setpoint=target)
    
    current_val = S60(90) # Empezamos por debajo
    dt = S60(0, 1)        # 1 tick
    
    print(f"Target: {target} | Start: {current_val}")
    
    for i in range(5):
        output = pid.update(current_val, dt)
        print(f"Tick {i+1}: Input={current_val} -> PID Output (Fuerza)={output}")
        # Simulamos que el sistema responde subiendo
        current_val = current_val + (output * S60(0, 30)) # Aplica parte de la fuerza
        
    print(f"Final Value: {current_val}")
