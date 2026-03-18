# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

import time
import sys
import os

# Ensure clean imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from yatra_core import S60
except ImportError:
    try:
        from yatra_core import S60
    except ImportError:
        # Fallback de emergencia
        print("CRITICAL: Yatra Core missing. Clock running in degraded mode.")
        S60 = None

try:
    from me60os_core import IsochronousClock
    RUST_AVAILABLE = True
except ImportError:
    print("⚠️ IsochronousClock no encontrado en me-60os_core. Usando versión Python nativa.")
    RUST_AVAILABLE = False

class TimeCrystalClock:
    """
    💎 CRISTAL DE TIEMPO YATRA (NANO-SYNC)
    ======================================
    Motor de Sincronización Temporal de Alta Precisión (Base-60).
    
    A diferencia de los relojes de sistema operativo (sujetos a interrupciones y floats),
    este reloj cuenta 'Momentos' (Nanosegundos Enteros) alineados con la Frecuencia Maestra.
    
    Principio:
    - El tiempo no fluye, se cuantiza.
    - Intervalo Sagrado = 23,939,835 ns (Derivado de Plimpton / 17).
    """
    
    def __init__(self):
        self.TICK_INTERVAL_NS = 23_939_835
        self.TARGET_FREQ = 1_000_000_000 // self.TICK_INTERVAL_NS  # ~41 Hz
        
        if RUST_AVAILABLE:
            self._core_clock = IsochronousClock()
            print(f"💎 YATRA CLOCK INIT (RUST NATIVE): Intervalo {self.TICK_INTERVAL_NS} ns, Freq {self.TARGET_FREQ} Hz")
        else:
            self.start_time_ns = time.perf_counter_ns()
            self._core_clock = None
            print(f"💎 YATRA CLOCK INIT (PYTHON FALLBACK): Intervalo {self.TICK_INTERVAL_NS} ns, Freq {self.TARGET_FREQ} Hz")
            
        self.ticks = 0
        self.drift_history = []
        
    def tick(self):
        """
        Espera el siguiente pulso sagrado delegando al SO/Rust.
        """
        self.ticks += 1
        
        if self._core_clock:
            # Delegado al thread::sleep y perf counter de Rust
            current_before = time.perf_counter_ns()
            self._core_clock.tick()
            current_after = time.perf_counter_ns()
            
            # Aproximamos el drift midiendo diferencia del sleep OS
            expected = current_before + self.TICK_INTERVAL_NS
            drift = abs(current_after - expected)
        else:
            target_ns = self.start_time_ns + (self.ticks * self.TICK_INTERVAL_NS)
            current_ns = time.perf_counter_ns()
            error_ns = target_ns - current_ns
            
            if error_ns > 0:
                sleep_sec = error_ns / 1_000_000_000
                time.sleep(sleep_sec)
                drift = 0
            else:
                drift = abs(error_ns)
                
        if drift > 0:
            self.drift_history.append(drift)
            if len(self.drift_history) > 60:
                self.drift_history.pop(0)

    def get_nanos(self):
        if self._core_clock:
            return self._core_clock.get_nanos()
        return time.perf_counter_ns()

    def get_coherence(self):
        """
        Calcula la Coherencia Temporal (0-60) basada en la estabilidad del reloj.
        """
        if not self.drift_history:
            if S60: return S60(1, 0, 0)
            return 100 # Fallback
            
        avg_drift = sum(self.drift_history) // len(self.drift_history)
        tolerance = self.TICK_INTERVAL_NS // 100
        
        if avg_drift <= tolerance:
             if S60: return S60(1, 0, 0) # Coherencia Perfecta
             return 100
             
        penalty_units = (avg_drift - tolerance) // tolerance
        
        if S60:
            remaining_minutes = max(0, 60 - penalty_units)
            return S60(0, remaining_minutes, 0)
        else:
            return max(0, 100 - penalty_units)

# Prueba de Integridad (Solo si se ejecuta directamente)
if __name__ == "__main__":
    clock = TimeCrystalClock()
    print("Iniciando Sincronización (60 ticks)...")
    
    t0 = time.perf_counter_ns()
    for i in range(60):
        clock.tick()
    t1 = time.perf_counter_ns()
    
    total_ns = t1 - t0
    ideal_ns = 60 * clock.TICK_INTERVAL_NS
    diff = total_ns - ideal_ns
    
    print(f"Total Real: {total_ns} ns")
    print(f"Total Ideal: {ideal_ns} ns")
    print(f"Desviación: {diff} ns")
    
    if abs(diff) < 1_000_000: # Menos de 1ms de error en 60 ticks
        print("✅ RELOJ YATRA ESTABLE.")
    else:
        print("⚠️ ALTA DISONANCIA DETECTADA.")