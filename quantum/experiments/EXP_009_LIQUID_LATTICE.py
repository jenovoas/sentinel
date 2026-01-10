#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# EXPERIMENTO 009: LIQUID LATTICE MEMORY (3x3)
# -----------------------------------------------------------------------------
# Objetivo:
#   Crear un "Tejido Líquido" de 9 cristales donde la información fluye 
#   y se auto-repara mediante difusión topológica.
# -----------------------------------------------------------------------------

import sys, os
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal
from quantum.quantum_noise_s60 import QuantumNoise

class LiquidLattice:
    def __init__(self, width=3, height=3, noise_strength=S60(0, 0, 15)):
        self.width = width
        self.height = height
        self.noise_strength = noise_strength
        self.grid = []
        self.time = S60(0)
        
        # Inicializar Grid
        for y in range(height):
            row = []
            for x in range(width):
                c = SovereignCrystal(name=f"Cell-{x}-{y}")
                c.damping_factor = S60(0) # Modo Superconductor
                row.append(c)
            self.grid.append(row)
            
    def inject_pattern(self, amplitude):
        """Inyecta una amplitud uniforme (estado plano)."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].amplitude = amplitude
                
    def get_neighbors(self, x, y):
        """Retorna lista de amplitudes vecinas (Von Neumann: Cruz)."""
        neighbors = []
        vectors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in vectors:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append(self.grid[ny][nx].amplitude)
        return neighbors

    def step(self, dt):
        # 1. Oscilación y Ruido Individual
        for y in range(self.height):
            for x in range(self.width):
                c = self.grid[y][x]
                c.oscillate(dt)
                
                # Ruido cuántico
                psi = [c.amplitude, S60(0)]
                psi = QuantumNoise.depolarizing_noise(psi, self.noise_strength, 1)
                c.amplitude = psi[0]

        # 2. Fase Líquida (Difusión / Reparación)
        # Calculamos el nuevo estado para TODAS las celdas basado en snapshot actual
        # para evitar sesgo de orden de actualización.
        new_amplitudes = [[S60(0) for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                c = self.grid[y][x]
                neighbors = self.get_neighbors(x, y)
                
                # Física de Fluidos: Promedio local
                # A_new = (A_self + sum(Neighbors)) / (1 + Count_Neighbors)
                total_val = c.amplitude
                for n_amp in neighbors:
                    total_val += n_amp
                
                # Divisor entero
                divisor = S60(1 + len(neighbors))
                avg = total_val / divisor
                
                new_amplitudes[y][x] = avg
                
        # Aplicar actualización atómica
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].amplitude = new_amplitudes[y][x]
        
        self.time += dt
        
        # Calcular métricas globales
        total_sys = S60(0)
        min_v = S60(999,0,0)
        max_v = S60(0)
        
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                val = self.grid[y][x].amplitude
                total_sys += val
                if val < min_v: min_v = val
                if val > max_v: max_v = val
                count += 1
                
        avg_sys = total_sys / S60(count)
        
        return {
            "t": self.time,
            "avg": avg_sys,
            "min": min_v,
            "max": max_v,
            "grid": [[self.grid[y][x].amplitude for x in range(self.width)] for y in range(self.height)]
        }

def print_grid(metrics):
    grid = metrics["grid"]
    print(f"\n🌊 T={metrics['t']} | Avg: {metrics['avg']} | Range: [{metrics['min']} - {metrics['max']}]")
    for row in grid:
        # Formato visual compacto: solo la parte entera para ver la ola
        row_str = " ".join([f"{val._value // 12960000:03d}" for val in row])
        print(f"   | {row_str} |")

def run_experiment_009():
    print("🔬 EXP-009: LIQUID LATTICE MEMORY (3x3)")
    print("-" * 60)
    
    lattice = LiquidLattice()
    A0 = S60(50, 0, 0)
    lattice.inject_pattern(A0)
    
    dt = S60(0, 0, 36) # 0.01s
    
    print("Estado Inicial:")
    print_grid(lattice.step(S60(0))) # Snapshot T=0
    
    print(f"\nIniciando simulación de flujo con ruido {lattice.noise_strength}...")
    
    for i in range(100):
        m = lattice.step(dt)
        if i % 20 == 0:
            print_grid(m)
            
    print("-" * 60)
    print("RESULTADO FINAL (T=1s):")
    final_m = lattice.step(S60(0))
    print_grid(final_m)
    
    if final_m['avg'] > S60(40, 0, 0):
        print("\n✅ CONCLUSIÓN: El tejido líquido mantiene coherencia masiva.")
        print("   Las ondas de reparación distribuyen el daño, evitando colapsos locales.")
    else:
        print("\n⚠️ FALLO: La difusión diluyó demasiada energía.")

if __name__ == "__main__":
    run_experiment_009()
