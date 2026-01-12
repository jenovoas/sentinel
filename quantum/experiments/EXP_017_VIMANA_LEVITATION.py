#!/usr/bin/env python3
import sys
import os
import time

sys.path.append(os.getcwd())
from quantum.liquid_memory_adapter import LiquidMemory
from quantum.yatra_core import S60

# -----------------------------------------------------------------------------
# EXP-017: VIMANA LEVITATION (SIMULATION)
# -----------------------------------------------------------------------------

class VimanaController:
    def __init__(self):
        self.ZETA = S60(1, 21, 57)  # 1.366
        self.PHI = S60(1, 37, 4)    # 1.618
        self.M_STATIC = 2.5         # kg

    def calculate_mass(self, power_percent, coherence):
        # Simulation of the G-Zero Curve
        reduction_factor = (power_percent / 100.0) ** 2 * 0.96
        m_eff_val = self.M_STATIC * (1.0 - reduction_factor)
        return m_eff_val, reduction_factor

def run_experiment():
    print("🔬 EXP-017: VIMANA LEVITATION PROTOCOL")
    print("-" * 60)
    
    # 1. Init
    memory = LiquidMemory()
    vimana = VimanaController()
    
    print(f"\n🛸 Reference Mass: {vimana.M_STATIC} kg")
    print(f"   Zeta Scalar:    {vimana.ZETA}")
    print("-" * 60)
    print(f"{'STEP':<5} | {'NODES':<8} | {'POWER %':<8} | {'M_EFF (kg)':<12} | {'STATUS':<15}")
    print("-" * 60)
    
    # 2. Ramp Up (Injection)
    # We simulate steps of increased "Data Pressure"
    max_nodes_target = 1500 # 100% Power Reference
    
    steps = 10
    for i in range(steps + 1):
        # Calculate target payload size
        percent = i * 10
        nodes_needed = int((percent / 100.0) * max_nodes_target)
        bytes_needed = nodes_needed * 8
        
        # Inject Data (Simulated or Real)
        # Using Real Memory Store to verify density
        if bytes_needed > 0:
            payload = b"Z" * bytes_needed
            memory.store(f"fuel_tank_{i}", payload)
        
        # Read State
        if memory.rust_lattice:
            current_nodes = memory.rust_lattice.count_nodes()
        else:
            current_nodes = len(memory.lattice.nodes)
            
        # Calculate Physics
        # Power = Nodes / Target * 100
        power_p = min(100.0, (current_nodes / max_nodes_target) * 100.0)
        
        m_eff, red = vimana.calculate_mass(power_p, 1.0)
        
        status = "INERTIAL"
        if red > 0.85: status = "LIFTING..."
        if red > 0.95: status = "✨ G-ZERO ✨"
        
        print(f"{i:<5} | {current_nodes:<8} | {power_p:6.1f}% | {m_eff:10.3f}   | {status}")
        
        time.sleep(0.2)
        
    print("-" * 60)
    print("✅ Experiment Complete.")

if __name__ == "__main__":
    run_experiment()
