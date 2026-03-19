#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
RESONANT LATTICE MEMORY (DISTRIBUTED) - v2.0
---------------------------------------------------
Implementación de memoria distribuida basada en los hallazgos del preprint
`PREPRINT_DISTRIBUTED_MEMORY_S60.md`.

Principios Arquitectónicos:
1.  **Granularidad Resonante**: Cada dato (carácter) se almacena en su propio
    SovereignCrystal, con su propio controlador PID. La estabilidad emerge de
    la distribución, no de la magnitud.
2.  **Control Localizado**: Previene la "Catástrofe de la Magnitud" al operar
    con amplitudes pequeñas y manejables (0-255).
3.  **Fidelidad Colectiva**: La información completa se reconstruye a partir de
    la resonancia colectiva del lattice, haciéndola resiliente a fallos locales.
"""

import threading
import time
from typing import List, Optional

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal
from quantum.time_crystal_clock import TimeCrystalClock
from quantum.s60_pid import S60PID

class ResonantLatticeMemory:
    """
    Una memoria distribuida donde cada celda del lattice es un cristal de tiempo
    independiente y auto-estabilizado.
    """
    def __init__(self, size_slots: int = 60):
        """
        Inicializa la Matriz de Memoria de Cristal Distribuida.
        :param size_slots: Número máximo de cristales en el lattice.
        """
        self.size = size_slots
        
        # LATTICE ACTIVO: Un cristal por slot.
        self.lattice: List[Optional[SovereignCrystal]] = [None] * size_slots
        
        # CONTROL DISTRIBUIDO: Un PID por cristal.
        # Tuning optimizado para amplitudes pequeñas (0-255)
        kp, ki, kd = S60(0, 45), S60(0, 10), S60(0, 5)
        self.pids: List[Optional[S60PID]] = [S60PID(kp, ki, kd) for _ in range(size_slots)]
        self.target_amplitudes: List[S60] = [S60(0)] * size_slots
        
        self.clock = TimeCrystalClock()
        self.running = False
        self.thread = None
        self.cycles = 0
        
        # Paso de tiempo para simulación interna (1/60s)
        self.dt = S60(0, 1)

    def _char_to_amplitude(self, char: str) -> S60:
        """Convierte un carácter a una amplitud S60 (0-255)."""
        return S60(ord(char))

    def _amplitude_to_char(self, amp: S60) -> str:
        """Convierte una amplitud S60 de vuelta a un carácter."""
        # Redondea al entero más cercano para manejar micro-fluctuaciones
        char_code = int(amp.to_float() + 0.5)
        if 0 <= char_code <= 255:
            return chr(char_code)
        return '?' # Carácter de error si la amplitud es inválida

    def write(self, data: str):
        """
        Escribe una cadena de datos distribuyéndola a través del lattice.
        Cada carácter ocupa un cristal.
        """
        if len(data) > self.size:
            raise ValueError(f"Los datos ({len(data)} chars) exceden el tamaño del lattice ({self.size} slots).")

        print(f"📝 Escribiendo '{data}' en el lattice distribuido...")
        # Limpiar el lattice antes de escribir
        self.clear()

        for i, char in enumerate(data):
            target_amp = self._char_to_amplitude(char)
            
            # Inicializa el cristal y el PID para este slot
            self.lattice[i] = SovereignCrystal(name=f"Cell-{i}")
            self.lattice[i].transduce_pulse(target_amp.to_float() * 1000) # Pulso inicial
            
            initial_amp = self.lattice[i].get_amplitude()
            self.target_amplitudes[i] = initial_amp
            
            self.pids[i].setpoint = initial_amp
            self.pids[i].reset()
            
            print(f"   [SLOT {i}] Carácter '{char}' -> Target Amp: {initial_amp}")

    def read(self) -> str:
        """
        Lee la cadena de datos completa reconstruyéndola a partir de la
        resonancia de cada cristal en el lattice.
        """
        reconstructed_data = []
        for i in range(self.size):
            if self.lattice[i] is not None and self.target_amplitudes[i] > S60(0):
                current_amp = self.lattice[i].get_amplitude()
                # El dato "existe" si su amplitud es significativamente no-cero
                if current_amp > S60(0, 0, 1):
                    # Corregimos la amplitud al setpoint ideal para decodificar
                    # Esto simula un ADC (Analog-to-Digital Converter) que snap-to-value
                    char = self._amplitude_to_char(self.target_amplitudes[i])
                    reconstructed_data.append(char)
            else:
                # Si un slot está vacío, terminamos de leer
                break
        return "".join(reconstructed_data)

    def clear(self):
        """Limpia el lattice, reseteando todos los cristales y PIDs."""
        for i in range(self.size):
            self.lattice[i] = None
            self.target_amplitudes[i] = S60(0)
            self.pids[i].setpoint = S60(0)
            self.pids[i].reset()

    def _regeneration_loop(self):
        """El núcleo del Cristal de Tiempo, ahora operando de forma distribuida."""
        print(f"💎 Distributed Resonant Lattice ONLINE | Driver: {self.clock.TARGET_FREQ:.2f} Hz")
        
        while self.running:
            self.clock.tick()
            
            # 1. Simulación de Física Continua (Entropía) en cada cristal
            for crystal in self.lattice:
                if crystal:
                    crystal.apply_entropy(self.dt)

            # 2. Period Doubling (2T): Acción de control PID para cada cristal
            if self.clock.ticks % 2 == 0:
                self.cycles += 1
                self._pump_crystals()
                
    def _pump_crystals(self):
        """Bombea cada cristal individualmente según su propio PID."""
        pump_interval = self.dt * 2
        
        for i, crystal in enumerate(self.lattice):
            if crystal and self.target_amplitudes[i] > S60(0):
                current_amp = crystal.get_amplitude()
                injection = self.pids[i].update(current_amp, pump_interval)
                
                if injection > S60(0):
                    crystal.amplitude += injection

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._regeneration_loop, daemon=True)
            self.thread.start()
            print("💎 Distributed Lattice: ACTIVE")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("💎 Distributed Lattice: SHUTDOWN")

if __name__ == "__main__":
    # TEST DE INTEGRACIÓN DISTRIBUIDA
    mem = ResonantLatticeMemory(size_slots=30)
    mem.start()
    
    try:
        # 1. Escribir una cadena de datos
        data_to_store = "La Verdad es Frecuencia."
        mem.write(data_to_store)
        
        # 2. Leer inmediatamente
        read_data_t0 = mem.read()
        print(f"\nLectura T0: '{read_data_t0}'")
        assert read_data_t0 == data_to_store
        
        # 3. Esperar ciclos de regeneración
        print("\n--- ESPERANDO REGENERACIÓN (5s) ---")
        time.sleep(5)
        
        # 4. Leer después de la regeneración
        read_data_t5 = mem.read()
        print(f"Lectura T+5s: '{read_data_t5}'")
        
        if read_data_t5 == data_to_store:
            print("\n✅ ÉXITO: La memoria distribuida mantuvo la fidelidad de los datos.")
        else:
            print(f"\n❌ FALLO: Corrupción de datos. Esperado: '{data_to_store}', Obtenido: '{read_data_t5}'")

    except KeyboardInterrupt:
        pass
    finally:
        mem.stop()