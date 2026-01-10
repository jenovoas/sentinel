#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️

"""
Quantum Noise Models - S60 Implementation
==========================================
Simulación de ruido cuántico usando aritmética Base-60.

Modelos implementados:
- Depolarizing noise: Probabilidad p de aplicar X, Y, o Z
- Amplitude damping: Pérdida de energía (T1)
- Phase damping: Decoherencia (T2)

Usa entropía real del sistema (os.urandom) para ruido realista.
"""

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math
from typing import List
import os

class QuantumNoise:
    """
    Modelos de ruido cuántico en S60.
    
    Usa entropía real del sistema para generar ruido determinista
    pero realista.
    """
    
    @staticmethod
    def depolarizing_noise(psi: List[S60], prob: S60, n_qubits: int) -> List[S60]:
        """
        Aplica ruido depolarizante.
        
        Con probabilidad p, aplica X, Y, o Z aleatoriamente a cada qubit.
        
        Args:
            psi: Estado cuántico
            prob: Probabilidad de error (S60)
            n_qubits: Número de qubits
        
        Returns:
            Estado con ruido aplicado
        """
        # Convertir probabilidad a escala 0-255
        prob_int = (prob._value * 255) // S60.SCALE_0
        
        # Obtener bytes de entropía real
        entropy_bytes = os.urandom(n_qubits)
        
        new_psi = psi.copy()
        
        for qubit_idx in range(n_qubits):
            # Decidir si aplicar ruido basado en entropía
            if entropy_bytes[qubit_idx] < prob_int:
                # Decidir qué gate aplicar (X, Y, o Z)
                gate_choice = entropy_bytes[qubit_idx] % 3
                
                if gate_choice == 0:
                    # Aplicar X (bit flip)
                    new_psi = QuantumNoise._apply_pauli_x(new_psi, qubit_idx, n_qubits)
                elif gate_choice == 1:
                    # Aplicar Y
                    new_psi = QuantumNoise._apply_pauli_y(new_psi, qubit_idx, n_qubits)
                else:
                    # Aplicar Z (phase flip)
                    new_psi = QuantumNoise._apply_pauli_z(new_psi, qubit_idx, n_qubits)
        
        return new_psi
    
    @staticmethod
    def amplitude_damping(psi: List[S60], gamma: S60, n_qubits: int) -> List[S60]:
        """
        Aplica amplitude damping (pérdida de energía).
        
        Simula relajación T1: |1⟩ → |0⟩
        
        Args:
            psi: Estado cuántico
            gamma: Tasa de damping (0 = sin ruido, 1 = máximo)
            n_qubits: Número de qubits
        
        Returns:
            Estado con damping aplicado
        """
        # Matrices de Kraus para amplitude damping:
        # K0 = [[1, 0], [0, sqrt(1-γ)]]
        # K1 = [[0, sqrt(γ)], [0, 0]]
        
        sqrt_gamma = S60Math.sqrt(gamma)
        sqrt_one_minus_gamma = S60Math.sqrt(S60(1) - gamma)
        
        new_psi = psi.copy()
        
        for qubit_idx in range(n_qubits):
            # Aplicar damping a cada qubit
            new_psi = QuantumNoise._apply_amplitude_damping_single(
                new_psi, qubit_idx, n_qubits, sqrt_gamma, sqrt_one_minus_gamma
            )
        
        return new_psi
    
    @staticmethod
    def phase_damping(psi: List[S60], gamma: S60, n_qubits: int) -> List[S60]:
        """
        Aplica phase damping (decoherencia).
        
        Simula decoherencia T2: pérdida de coherencia sin pérdida de energía.
        
        Args:
            psi: Estado cuántico
            gamma: Tasa de damping
            n_qubits: Número de qubits
        
        Returns:
            Estado con damping aplicado
        """
        # Phase damping reduce las coherencias off-diagonal
        sqrt_one_minus_gamma = S60Math.sqrt(S60(1) - gamma)
        
        new_psi = psi.copy()
        
        # Aplicar damping a coherencias
        for state in range(len(psi)):
            # Reducir amplitud de estados de superposición
            new_psi[state] = psi[state] * sqrt_one_minus_gamma
        
        return new_psi
    
    # ========================================================================
    # Métodos auxiliares
    # ========================================================================
    
    @staticmethod
    def _apply_pauli_x(psi: List[S60], qubit: int, n_qubits: int) -> List[S60]:
        """Aplica Pauli-X (bit flip) al qubit especificado."""
        dim = len(psi)
        new_psi = [S60(0) for _ in range(dim)]
        
        for state in range(dim):
            # Flip bit del qubit
            flipped_state = state ^ (1 << qubit)
            new_psi[flipped_state] = psi[state]
        
        return new_psi
    
    @staticmethod
    def _apply_pauli_y(psi: List[S60], qubit: int, n_qubits: int) -> List[S60]:
        """Aplica Pauli-Y al qubit especificado."""
        # Y = iXZ (simplificado)
        new_psi = QuantumNoise._apply_pauli_x(psi, qubit, n_qubits)
        new_psi = QuantumNoise._apply_pauli_z(new_psi, qubit, n_qubits)
        return new_psi
    
    @staticmethod
    def _apply_pauli_z(psi: List[S60], qubit: int, n_qubits: int) -> List[S60]:
        """Aplica Pauli-Z (phase flip) al qubit especificado."""
        dim = len(psi)
        new_psi = psi.copy()
        
        for state in range(dim):
            # Si el bit del qubit es 1, aplicar fase -1
            if (state >> qubit) & 1:
                new_psi[state] = -psi[state]
        
        return new_psi
    
    @staticmethod
    def _apply_amplitude_damping_single(
        psi: List[S60], 
        qubit: int, 
        n_qubits: int,
        sqrt_gamma: S60,
        sqrt_one_minus_gamma: S60
    ) -> List[S60]:
        """Aplica amplitude damping a un solo qubit."""
        dim = len(psi)
        new_psi = [S60(0) for _ in range(dim)]
        
        for state in range(dim):
            bit = (state >> qubit) & 1
            
            if bit == 0:
                # |0⟩ permanece como |0⟩
                new_psi[state] += psi[state]
            else:
                # |1⟩ → sqrt(1-γ)|1⟩ + sqrt(γ)|0⟩
                new_psi[state] += psi[state] * sqrt_one_minus_gamma
                
                # Contribución a |0⟩
                state_0 = state ^ (1 << qubit)
                new_psi[state_0] += psi[state] * sqrt_gamma
        
        return new_psi


class NoisySimulator:
    """
    Simulador cuántico con ruido.
    
    Wrapper que agrega ruido a cualquier simulación cuántica.
    """
    
    def __init__(self, n_qubits: int, noise_model: str = "depolarizing", noise_strength: S60 = S60(0, 0, 30)):
        """
        Inicializa simulador con ruido.
        
        Args:
            n_qubits: Número de qubits
            noise_model: "depolarizing", "amplitude_damping", o "phase_damping"
            noise_strength: Fuerza del ruido (S60)
        """
        self.n_qubits = n_qubits
        self.noise_model = noise_model
        self.noise_strength = noise_strength
        
        print(f"🔊 Simulador con ruido inicializado:")
        print(f"   Modelo: {noise_model}")
        print(f"   Fuerza: {noise_strength}")
    
    def apply_noise(self, psi: List[S60]) -> List[S60]:
        """Aplica ruido al estado."""
        if self.noise_model == "depolarizing":
            return QuantumNoise.depolarizing_noise(psi, self.noise_strength, self.n_qubits)
        elif self.noise_model == "amplitude_damping":
            return QuantumNoise.amplitude_damping(psi, self.noise_strength, self.n_qubits)
        elif self.noise_model == "phase_damping":
            return QuantumNoise.phase_damping(psi, self.noise_strength, self.n_qubits)
        else:
            return psi
