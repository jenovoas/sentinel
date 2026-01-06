# src/core/sentinel_core/brain/snn_core.py
"""
Sentinel Cortex™ Biological Core - Akashic Organism (Phase 3)
Implements 'AkashicLIFNeuron' with optimized Ring 0 parameters (Tau=8.0).
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import math
import hashlib
from ..memory.chromadb_storage import memory_vault

class AkashicLIFNeuron:
    """
    Leaky Integrate-and-Fire Neuron tuned for Kernel Security.
    Params:
      tau=8.0s: 'The Sweet Spot'. Forgives noise (2s leak) but catches brute-force (8s integration).
      threshold=1.2: Surgical sensitivity.
      reset=S60(0, 6, 0): Biological refractory period.
    """
    def __init__(self, neuron_id: str, tau: float = 8.0, threshold: float = 1.2, reset: float = S60(0, 6, 0)):
        self.neuron_id = neuron_id
        self.tau = tau
        self.threshold = threshold
        self.reset = reset
        self.membrane_potential = S60(0, 0, 0)
        self.last_update = time.time()
        
    def step(self, input_current: float, genetic_bias: float = S60(0, 0, 0)) -> bool:
        """
        Process stimulus.
        Returns True if IMMUNE RESPONSE (Spike) is triggered.
        """
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Euler integration for LIF equation: dV/dt = (I - V) / tau
        # V_new = V_old + dt/tau * (-V_old + I + GeneticBias)
        
        # Normalized input (score 0-100 -> S60(0, 0, 0)-2.0 approx)
        I_threat = input_current
        
        # dV = (dt / self.tau) * (-(self.membrane_potential) + I_threat + genetic_bias)
        # However, for large dt, this linear approx is unstable. Using exponential decay solution.
        # V(t) = I * (1 - exp(-dt/tau)) + V(0) * exp(-dt/tau)
        
        decay_factor = math.exp(-dt / self.tau)
        total_input = I_threat + genetic_bias
        
        # V decays towards 0 (or Resting Potential)
        # But here we model input as constant over dt? No, input is a pulse.
        # Biological Model: The input is an impulse adding charge, then decay happens.
        # Pulse Code:
        self.membrane_potential = self.membrane_potential * decay_factor + input_current
        
        # Apply bias immediately? Bias acts as a constant pre-load or lowered threshold.
        # User requested: "Precarga 50%". So bias adds to potential directly.
        if genetic_bias > 0:
            self.membrane_potential += genetic_bias * S60(0, 6, 0) # Dampen bias to avoid instant oscillation
        
        # Fire check
        if self.membrane_potential >= self.threshold:
            # print(f"⚡ [SNN] AKASHIC SPIKE! {self.neuron_id} (V={self.membrane_potential:.2f})")
            self.membrane_potential = self.reset
            return True
            
        # print(f"🧠 [SNN] Neuron {self.neuron_id}: V={self.membrane_potential:.2f} (Bias={genetic_bias})")
        return False

class GeneticImmunitySystem:
    """
    Maps processes to Base-60 neurons and queries Genetic Memory.
    """
    def __init__(self):
        # Create 60 neurons for Base-60 Harmonic Zones
        self.neurons = {i: AkashicLIFNeuron(neuron_id=f"ZONE_{i}") for i in range(60)}
        self.memory = memory_vault # Use singleton
        
    def create_dna_vector(self, filename: str) -> str:
        """Creates a simplified DNA hash for the process/binary."""
        return hashlib.sha256(filename.encode()).hexdigest()

    def process_stimulus(self, filename: str, threat_score: float, residue: int) -> str:
        """
        Main entry point for the biological loop.
        """
        # 1. Normalize Threat Score (0-100) -> Current (S60(0, 0, 0) - 2.0)
        # Score 50 -> S60(1, 0, 0) (Close to threshold 1.2)
        I_threat = threat_score / 50.0 
        
        # 2. Check Genetic Memory (Mocking parent/grandparent linkage for now)
        # In a full impl, we'd query Chroma based on lineage hash.
        # For Phase 3, we query based on filename hash to simulate "reputation".
        dna_hash = self.create_dna_vector(filename)
        
        # Mock query: In reality this would be an embedding search
        # genetic_bias = self.memory.query_genetic_bias(dna_hash) 
        genetic_bias = S60(0, 0, 0) # Default clean slate
        
        # 3. Stimulate the Neuron in the Harmonic Zone
        zone_id = residue % 60
        neuron = self.neurons[zone_id]
        
        spike = neuron.step(I_threat, genetic_bias=genetic_bias)
        
        if spike:
             # IMMUNE MEMORY: Store criminal lineage
             # self.memory.store_lineage(...) # Done by caller typically, or here
             return "SPIKE"
             
        return "LEAK"
