#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# ------------------------------------------------------------
# Quantum Lattice Engine
# ------------------------------------------------------------
# Simulador de red cuántica discreta sin floats.
# Integra reloj de cristal de tiempo y acoplamiento de fase XY.
# ------------------------------------------------------------

from quantum.time_crystal_clock import TimeCrystalClock
from quantum.yatra_core import S60
from quantum.yatra_math import S60Math

import time
import os


class QuantumNode:
    def __init__(self, node_id, phase=None, energy=None):
        self.id = node_id
        self.phase = phase if phase else S60(0, 0, 0)
        self.energy = energy if energy else S60(0, 0, 0)
        self.neighbors = []
        self.active = True

    def connect(self, other):
        if other not in self.neighbors:
            self.neighbors.append(other)
            other.neighbors.append(self)

    def interact(self, coupling, dt=1):
        """
        Interacción XY con dinámica hamiltoniana.
        
        Ecuación de movimiento:
        dφᵢ/dt = -J Σⱼ sin(φᵢ - φⱼ)
        
        Args:
            coupling: S60 coupling strength
            dt: int time step
        """
        if not self.active or not self.neighbors:
            return
        
        # 1. Auto-evolución (Fase proporcional a la Energía)
        # dφ/dt = ω = E (en unidades de resonancia)
        self.phase += self.energy * dt
        
        # 2. Interacción con vecinos (Hamiltoniano XY)
        phase_force = S60(0, 0, 0)
        
        for n in self.neighbors:
            if not n.active:
                continue
            
            # Diferencia de fase discreta
            dphi = self.phase - n.phase
            
            # Dinámica Hamiltoniana S60 pura (sin aproximaciones lineales sucias)
            sin_dphi = S60Math.sin(dphi)
            
            # Fuerza hamiltoniana: F = -J sin(Δφ)
            phase_force -= coupling * sin_dphi
            
            # Transferencia de energía (conservativa)
            # ΔE = J * sin(Δφ) -> Intercambio de flujo
            delta_e = coupling * abs(sin_dphi)
            
            self.energy += delta_e
            n.energy -= delta_e
        
        # 3. Aplicar fuerzas de red
        self.phase += phase_force * dt

class QuantumLatticeEngine:
    def __init__(self, rings=1, use_zpe=False):
        self.clock = TimeCrystalClock()
        self.nodes = []
        self.coupling = S60(0, 1, 0)  # Coupling strength J
        self.dt = 1  # Time step (integer, will multiply S60)
        self._build_hex_lattice(rings)
        self.use_zpe = use_zpe
        self.zpe_strength = S60(0, 0, 0)
        print(f"💎 Quantum Lattice Engine Initialized ({len(self.nodes)} nodes)")

    def _build_hex_lattice(self, rings):
        """Construye red hexagonal con múltiples anillos."""
        # Centro
        center = QuantumNode(0)
        self.nodes.append(center)
        
        if rings == 0:
            return
        
        # Direcciones hexagonales (E, NE, NW, W, SW, SE)
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)]
        
        # Anillo 1
        ring_nodes = []
        for i, (dx, dy) in enumerate(directions):
            node = QuantumNode(i+1)
            self.nodes.append(node)
            center.connect(node)
            ring_nodes.append(node)
        
        # Conectar vecinos del anillo
        for i in range(len(ring_nodes)):
            ring_nodes[i].connect(ring_nodes[(i+1) % len(ring_nodes)])
        
        # Anillos adicionales (si rings > 1)
        for r in range(2, rings + 1):
            prev_ring = ring_nodes
            ring_nodes = []
            
            # Cada anillo tiene 6*r nodos
            node_id = len(self.nodes)
            for i in range(6 * r):
                node = QuantumNode(node_id)
                self.nodes.append(node)
                ring_nodes.append(node)
                node_id += 1
                
                # Conectar al anillo anterior (simplificado)
                if i < len(prev_ring):
                    prev_ring[i].connect(node)
            
            # Conectar vecinos del anillo
            for i in range(len(ring_nodes)):
                ring_nodes[i].connect(ring_nodes[(i+1) % len(ring_nodes)])

    def inject_pulse(self, energy=S60(1,0,0)):
        """Inyecta pulso de energía en el nodo central."""
        center = self.nodes[0]
        center.energy += energy
        print(f"⚡ Pulse injected at Node 0 | +{energy}")

    def step(self):
        """Paso de simulación con integración temporal."""
        self.clock.tick()
        drift = self.clock.get_coherence()
        
        for n in self.nodes:
            n.interact(self.coupling, self.dt)
            
            if self.use_zpe:
                # Perturbación ZPE usando entropía real del sistema
                sys_load = int(os.getloadavg()[0] * 100)  # Convertir a entero (carga * 100)
                zpe_fluctuation = S60(0, 0, sys_load)  # En segundos Base-60
                n.phase += zpe_fluctuation / S60(0, 10, 0)
        
        return drift

    def measure_coherence(self):
        """Mide coherencia de fase de la red."""
        if not self.nodes or len(self.nodes) == 0:
            return S60(1, 0, 0)
        
        # Promedio aritmético (usando división por entero)
        n_nodes = len(self.nodes)
        if n_nodes == 0:
            return S60(1, 0, 0)
            
        total_phase_val = sum(n.phase._value for n in self.nodes)
        mean_phase_val = total_phase_val // n_nodes
        
        # Desviación absoluta media
        total_dev_val = sum(abs(n.phase._value - mean_phase_val) for n in self.nodes)
        mean_dev_val = total_dev_val // n_nodes
        
        # Coherencia = 1 - (desviación / escala_maxima)
        # Una desviación de 180 grados (6480000 unidades) es el máximo desorden
        max_dev = 180 * S60.SCALE_0
        
        if mean_dev_val > max_dev:
            mean_dev_val = max_dev
            
        # Ratio de coherencia: (max_dev - mean_dev) / max_dev
        coh_val = ((max_dev - mean_dev_val) * S60.SCALE_0) // max_dev
        
        return S60._from_raw(coh_val)


    def total_energy(self):
        """Energía total del sistema (debe conservarse)."""
        total = S60(0,0,0)
        for n in self.nodes:
            total += n.energy
        return total

    def verify_conservation(self):
        """Verifica conservación de energía."""
        E = self.total_energy()
        return E

    def run_demo(self, steps=60):
        """Ejecuta demostración del motor."""
        print("\n🕸️  Running Quantum Lattice Demo (Base-60 Mode)")
        print("----------------------------------------------")
        
        # Energía inicial
        E0 = self.total_energy()
        
        for t in range(steps):
            if t % 10 == 0:
                self.inject_pulse(S60(1,0,0))
            
            drift = self.step()
            coh = self.measure_coherence()
            energy = self.total_energy()
            
            # Verificar conservación
            delta_E = abs(energy - E0)
            conservation_ok = "✅" if delta_E < S60(0, 0, 1) else "❌"
            
            print(f"Tick {t:02d} | Coherence: {coh} | Energy: {energy} | "
                  f"ΔE: {delta_E} {conservation_ok} | Drift: {drift}")
            
            time.sleep(0.1)

if __name__ == "__main__":
    engine = QuantumLatticeEngine(rings=1, use_zpe=True)
    engine.run_demo(60)
