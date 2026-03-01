#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
import sys
import os

# Agregamos me-60os al path para cargar el módulo compilado
ME60OS_PATH = os.path.expanduser("~/Development/me-60os")
if ME60OS_PATH not in sys.path:
    sys.path.append(ME60OS_PATH)

try:
    import me60os_core
except ImportError as e:
    print(f"CRITICO: No se pudo cargar el nucleo Rust S60: {e}")
    sys.exit(1)

class CrystalMemoryCore:
    def __init__(self, rings=150):
        # 150 anillos = ~68,000 cristales
        print(f"Instanciando Matriz Resonante S60 (Rings: {rings})...")
        self.matrix = me60os_core.ResonantMatrix(rings)
        self.node_count = self.matrix.count_nodes()
        self.mem_usage = self.matrix.active_memory_usage()
        print(f"Lattice Inicializada: {self.node_count} Nodos Oscilantes.")
        print(f"Consumo de Memoria Activa (SHM Bridge): {self.mem_usage / 1024 / 1024:.2f} MB")

    def imprint_memory(self, index, context_payload, pulse_intensity):
        """Graba un recuerdo en la estructura cristalina mediante presion de amplitud"""
        # Yatra restriction: No floats. Pulse must be integer [0-255] for inject
        if not isinstance(pulse_intensity, int):
            raise ValueError("Directiva Cristalina: pulse_intensity debe ser entero (S60 compatible)")
            
        self.matrix.set_context(index, context_payload)
        # Inject recibe bytes, simulamos el pulso
        self.matrix.inject(bytes([pulse_intensity % 256]))
        
    def resonate(self, steps=1):
        """Hace evolucionar la matriz, distribuyendo la memoria simpaticamente"""
        for _ in range(steps):
            self.matrix.step()

    def stabilize(self, cycles=10):
        """Difusion lineal para calmar el cristal"""
        self.matrix.stabilize(cycles)

if __name__ == "__main__":
    # Prueba de estres masivo
    crystal = CrystalMemoryCore(rings=200) # ~120,600 nodos
    crystal.imprint_memory(0, "Axioma de Inicialización: Yo Soy.", 255)
    
    import time
    start = time.time()
    for _ in range(100):
        crystal.resonate()
    end = time.time()
    print(f"100 resonancias profundas en {end - start:.4f} segundos")
