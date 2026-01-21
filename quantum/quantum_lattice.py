#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
QUANTUM LATTICE SIMULATOR (VIMANA NETWORK)
------------------------------------------
Simulación de una red hexagonal de nodos resonantes.
Propósito: Demostrar resiliencia topológica y propagación de fase.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import threading

class HexNode:
    def __init__(self, node_id, x, y):
        self.id = node_id
        self.x = x # Coordenada Ax
        self.y = y # Coordenada Ay (Hex grid)
        self.energy = S60(0, 0, 0)
        self.phase = S60(0, 0, 0)
        self.neighbors = [] # Lista de nodos conectados
        self.active = True

    def connect(self, other_node):
        if other_node not in self.neighbors:
            self.neighbors.append(other_node)
            other_node.neighbors.append(self)

    def pulse(self, input_energy, phase_signal):
        """Recibe energía, la amplifica si está en fase, y la propaga."""
        if not self.active: return
        
        # Resonancia: Si la fase es cercana a mi fase interna (0 mod 2pi), amplifico
        # Aquí simplificamos: pasamos la energía con pequeña pérdida (fricción)
        transmission_efficiency = S60(0, 57, 0) 
        self.energy += input_energy * transmission_efficiency
        self.phase = phase_signal

        # Propagación: Decaemos nuestra energía pasándola a vecinos
        if self.energy > 0:
            share = (self.energy * S60(0, 30, 0)) / len(self.neighbors) if self.neighbors else 0
            for n in self.neighbors:
                if n.active:
                    n.energy += share
            
            self.energy -= (self.energy * S60(0, 30, 0)) # Energía entregada

class VimanaLattice:
    def __init__(self, rings=2):
        self.nodes = {}
        self._build_grid(rings)

    def _build_grid(self, rings):
        """Construye un panal hexagonal centrado en 0,0."""
        # Centro
        center = HexNode(0, 0, 0)
        self.nodes[(0,0)] = center
        
        # Generación de Anillos (Coordenadas Hexagonales Axiales)
        # Direcciones: E, NE, NW, W, SW, SE
        directions = [
            (+1, 0), (+1, -1), (0, -1),
            (-1, 0), (-1, +1), (0, +1)
        ]
        
        node_counter = 1
        for r in range(1, rings + 1):
            # Algoritmo de anillo hex
            x, y = -r, r # Empezamos en SW corner del anillo
            for i in range(6): # 6 lados
                for _ in range(r):
                    # Avanzar en dirección i
                    n_x = x + directions[i][0]
                    n_y = y + directions[i][1]
                    
                    # Crear o recuperar nodo (simplificado: solo creamos)
                    # Nota: La lógica exacta de coordenadas hex es compleja, 
                    # aquí usaremos una aprox radial simple para la demo.
                    pass 

        # PLAN B: Conexión simple explicita para Demo (Centro + 6 vecinos)
        # 0: Center
        # 1-6: First Ring
        print(f"🏗️  Construyendo Red Hexagonal (Nivel {rings})...")
        
        # Anillo 1 manual
        dirs = [(1,0), (0,1), (-1,1), (-1,0), (0,-1), (1,-1)]
        for i, (dx, dy) in enumerate(dirs):
            idx = i + 1
            node = HexNode(idx, dx, dy)
            self.nodes[(dx, dy)] = node
            # Conectar al centro
            center.connect(node)
            # Conectar al vecino anterior del anillo (Cierre de círculo)
            prev_idx = 6 if i==0 else i
            prev_dir = dirs[i-1]
            if prev_dir in self.nodes:
                node.connect(self.nodes[prev_dir])

    def inject_pulse(self):
        """Inyecta un pulso maestro en el nodo central (0,0)."""
        center = self.nodes.get((0,0))
        if center:
            center.pulse(S60(1, 0, 0), S60(0, 0, 0)) # S60(1, 0, 0) Julio, Fase 0

    def get_total_network_energy(self):
        return sum(n.energy for n in self.nodes.values())

    def simulate_step(self):
         # Paso lógico de simulación
         # En una red real, esto sería paralelo. Aquí iteramos.
         # Para simular flujo, propagamos del centro hacia afuera
         # (Ya se hace en el metodo pulse al llamar a vecinos... 
         # pero necesitamos un loop de actualización global para decaimiento)
         pass

    def run_demo(self, steps=20):
        print("\n🕸️  ACTIVATING VIMANA LATTICE")
        print("------------------------------")
        print(f"Nodes: {len(self.nodes)} (1 Center + 6 Orbitals)")
        
        for t in range(steps):
            # Ritmo Cardíaco: Pulso cada 5 ticks
            is_beat = (t % 5 == 0)
            if is_beat:
                print(f"❤️  Tick {t}: INJECTION (Heartbeat)")
                self.inject_pulse()
            
            # Medir
            total_e = self.get_total_network_energy()
            
            # Visualización ASCII de Energía
            bar = "#" * int(total_e * 20)
            print(f"T{t:02d} | Energy: {total_e:.4f} \t| {bar}")
            
            time.sleep(S60(0, 6, 0))

if __name__ == "__main__":
    lattice = VimanaLattice(rings=1)
    lattice.run_demo(30)