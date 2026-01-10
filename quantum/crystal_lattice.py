#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# RED DE RESONANCIA (CRYSTAL LATTICE)
# -------------------------------------------------------------------------------------

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal
from quantum.yatra_math import S60Math

class CrystalLattice:
    """
    Retículo de cristales acoplados. 
    Permite la transferencia de energía (datos) por simpatía vibratoria.
    """
    def __init__(self, size=2):
        self.size = size
        self.crystals = [SovereignCrystal(name=f"Node-{i}") for i in range(size)]
        # Factor de Acoplamiento: 10/60 (Fuerza de la conexión entre nodos)
        self.coupling_factor = S60(0, 10) 
        self.dt = S60(0, 1)

    def step(self):
        """
        Ejecuta un paso de tiempo en toda la red.
        Calcula la transferencia de energía entre nodos adyacentes.
        """
        # 1. Calcular transferencias (sin aplicar aún para mantener simetría)
        transfers = [S60(0)] * self.size
        
        for i in range(self.size - 1):
            c1 = self.crystals[i]
            c2 = self.crystals[i+1]
            
            # Diferencial de Amplitud (Presión)
            diff = c1.get_amplitude() - c2.get_amplitude()
            
            # Flujo = Diferencial * Factor de Acoplamiento
            flow = diff * self.coupling_factor
            
            # El nodo i pierde, el nodo i+1 gana
            transfers[i] = transfers[i] - flow
            transfers[i+1] = transfers[i+1] + flow
            
        # 2. Aplicar transferencias y oscilar
        for i in range(self.size):
            self.crystals[i].amplitude = self.crystals[i].amplitude + transfers[i]
            self.crystals[i].oscillate(self.dt)

    def inject(self, index, pressure):
        self.crystals[index].transduce_pulse(pressure)

    def get_amplitudes(self):
        return [c.get_amplitude() for c in self.crystals]

if __name__ == "__main__":
    print("🕸️  INICIANDO RED DE RESONANCIA LATTICE")
    net = CrystalLattice(size=3)
    
    # Inyectamos en el extremo izquierdo (Node-0)
    print("\n--- INYECCIÓN EN NODE-0 (Presión: 60) ---")
    net.inject(0, 60)
    
    print("\n--- EVOLUCIÓN DE LA RED ---")
    print("Node-0 \t\t| Node-1 \t\t| Node-2")
    print("-" * 60)
    
    for t in range(1, 13): # 12 ticks
        net.step()
        amps = net.get_amplitudes()
        print(f"T{t:02}: {amps[0]} \t| {amps[1]} \t| {amps[2]}")
    
    final_amps = net.get_amplitudes()
    if final_amps[2] > S60(0):
        print("\n✅ ÉXITO: La energía resonó hasta el Node-2.")
    else:
        print("\n❌ FALLO: No hubo transferencia.")
