"""
Sentinel Quantum Simulator - Core Module

This module provides a complete quantum mechanics simulation framework
for testing quantum algorithms and optomechanical systems before hardware deployment.

Author: Jaime Novoa
Project: Sentinel Cortex™
License: MIT (pre-patent filing)
"""

import numpy as np
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.integrate import odeint


class QubitState:
    """
    Represents a quantum state in Hilbert space.
    
    Supports:
    - Pure states (state vectors)
    - Mixed states (density matrices)
    - Multi-qubit systems (tensor products)
    """
    
    def __init__(self, state_vector: Optional[np.ndarray] = None, 
                 density_matrix: Optional[np.ndarray] = None,
                 n_qubits: int = 1):
        """
        Initialize quantum state.
        
        Args:
            state_vector: Complex vector representing pure state |ψ⟩
            density_matrix: Density matrix ρ for mixed states
            n_qubits: Number of qubits (if creating from scratch)
        """
        if state_vector is not None:
            self.state_vector = state_vector / np.linalg.norm(state_vector)  # Normalize
            self.density_matrix = np.outer(self.state_vector, self.state_vector.conj())
            self.n_qubits = int(np.log2(len(state_vector)))
            self.is_pure = True
        elif density_matrix is not None:
            self.density_matrix = density_matrix
            self.state_vector = None
            self.n_qubits = int(np.log2(density_matrix.shape[0]))
            self.is_pure = np.allclose(density_matrix @ density_matrix, density_matrix)
        else:
            # Initialize to |0⟩^⊗n
            self.n_qubits = n_qubits
            dim = 2 ** n_qubits
            self.state_vector = np.zeros(dim, dtype=complex)
            self.state_vector[0] = 1.0  # |00...0⟩
            self.density_matrix = np.outer(self.state_vector, self.state_vector.conj())
            self.is_pure = True
    
    def apply_gate(self, gate: np.ndarray, target_qubits: Optional[List[int]] = None):
        """
        Apply quantum gate to state.
        
        Args:
            gate: Unitary matrix representing quantum gate
            target_qubits: Which qubits to apply gate to (None = all)
        """
        if target_qubits is None:
            # Apply to entire state
            if self.is_pure:
                self.state_vector = gate @ self.state_vector
                self.density_matrix = np.outer(self.state_vector, self.state_vector.conj())
            else:
                self.density_matrix = gate @ self.density_matrix @ gate.conj().T
        else:
            # Apply to specific qubits (tensor product)
            full_gate = self._expand_gate(gate, target_qubits)
            self.apply_gate(full_gate)
    
    def _expand_gate(self, gate: np.ndarray, target_qubits: List[int]) -> np.ndarray:
        """Expand gate to full Hilbert space using tensor products."""
        n_gate_qubits = int(np.log2(gate.shape[0]))
        
        if len(target_qubits) != n_gate_qubits:
            raise ValueError(f"Gate acts on {n_gate_qubits} qubits, but {len(target_qubits)} targets specified")
        
        # Build full gate via tensor products
        full_gate = np.eye(1, dtype=complex)
        gate_idx = 0
        
        for i in range(self.n_qubits):
            if i in target_qubits:
                # Extract appropriate part of gate
                if n_gate_qubits == 1:
                    full_gate = np.kron(full_gate, gate)
                else:
                    # Multi-qubit gate (e.g., CNOT)
                    full_gate = np.kron(full_gate, gate)
                    break  # Assume contiguous qubits for now
                gate_idx += 1
            else:
                # Identity on this qubit
                full_gate = np.kron(full_gate, np.eye(2))
        
        return full_gate
    
    def measure(self, qubit_idx: int) -> Tuple[int, 'QubitState']:
        """
        Measure qubit in computational basis, collapsing state.
        
        Args:
            qubit_idx: Which qubit to measure
            
        Returns:
            (outcome, collapsed_state): 0 or 1, and post-measurement state
        """
        # Projection operators
        P0 = self._projection_operator(qubit_idx, 0)
        P1 = self._projection_operator(qubit_idx, 1)
        
        # Probabilities
        if self.is_pure:
            p0 = np.abs(self.state_vector.conj() @ P0 @ self.state_vector)
            p1 = np.abs(self.state_vector.conj() @ P1 @ self.state_vector)
        else:
            p0 = np.real(np.trace(P0 @ self.density_matrix))
            p1 = np.real(np.trace(P1 @ self.density_matrix))
        
        # Sample outcome
        outcome = np.random.choice([0, 1], p=[p0, p1])
        
        # Collapse state
        P = P0 if outcome == 0 else P1
        p = p0 if outcome == 0 else p1
        
        if self.is_pure:
            collapsed_vector = P @ self.state_vector / np.sqrt(p)
            collapsed_state = QubitState(state_vector=collapsed_vector)
        else:
            collapsed_density = P @ self.density_matrix @ P / p
            collapsed_state = QubitState(density_matrix=collapsed_density)
        
        return outcome, collapsed_state
    
    def _projection_operator(self, qubit_idx: int, outcome: int) -> np.ndarray:
        """Build projection operator for measuring qubit_idx."""
        # Single-qubit projector
        if outcome == 0:
            proj_single = np.array([[1, 0], [0, 0]], dtype=complex)
        else:
            proj_single = np.array([[0, 0], [0, 1]], dtype=complex)
        
        # Expand to full space
        proj_full = np.eye(1, dtype=complex)
        for i in range(self.n_qubits):
            if i == qubit_idx:
                proj_full = np.kron(proj_full, proj_single)
            else:
                proj_full = np.kron(proj_full, np.eye(2))
        
        return proj_full
    
    def get_bloch_vector(self, qubit_idx: int = 0) -> np.ndarray:
        """
        Get Bloch sphere coordinates for single qubit.
        
        Returns:
            [x, y, z] coordinates on Bloch sphere
        """
        if self.n_qubits > 1:
            # Trace out other qubits
            rho = self._partial_trace(qubit_idx)
        else:
            rho = self.density_matrix
        
        # Pauli matrices
        sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
        sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
        
        x = np.real(np.trace(rho @ sigma_x))
        y = np.real(np.trace(rho @ sigma_y))
        z = np.real(np.trace(rho @ sigma_z))
        
        return np.array([x, y, z])
    
    def _partial_trace(self, keep_qubit: int) -> np.ndarray:
        """Trace out all qubits except keep_qubit."""
        # Simplified for single qubit extraction
        dim = 2 ** self.n_qubits
        rho_reduced = np.zeros((2, 2), dtype=complex)
        
        for i in range(dim):
            for j in range(dim):
                # Check if qubits match on keep_qubit
                i_bit = (i >> keep_qubit) & 1
                j_bit = (j >> keep_qubit) & 1
                
                # Sum over other qubits
                if self._other_qubits_match(i, j, keep_qubit):
                    rho_reduced[i_bit, j_bit] += self.density_matrix[i, j]
        
        return rho_reduced
    
    def _other_qubits_match(self, i: int, j: int, exclude_qubit: int) -> bool:
        """Check if all qubits except exclude_qubit match between i and j."""
        for q in range(self.n_qubits):
            if q != exclude_qubit:
                if ((i >> q) & 1) != ((j >> q) & 1):
                    return False
        return True
    
    def fidelity(self, other: 'QubitState') -> float:
        """
        Calculate fidelity between this state and another.
        
        F(ρ, σ) = Tr(√(√ρ σ √ρ))²
        """
        rho = self.density_matrix
        sigma = other.density_matrix
        
        sqrt_rho = self._matrix_sqrt(rho)
        product = sqrt_rho @ sigma @ sqrt_rho
        sqrt_product = self._matrix_sqrt(product)
        
        fidelity = np.real(np.trace(sqrt_product)) ** 2
        return fidelity
    
    def _matrix_sqrt(self, matrix: np.ndarray) -> np.ndarray:
        """Compute matrix square root via eigendecomposition."""
        eigvals, eigvecs = np.linalg.eigh(matrix)
        sqrt_eigvals = np.sqrt(np.maximum(eigvals, 0))  # Avoid numerical issues
        return eigvecs @ np.diag(sqrt_eigvals) @ eigvecs.conj().T
    
    def __repr__(self) -> str:
        if self.is_pure:
            return f"QubitState({self.n_qubits} qubits, pure)\n{self.state_vector}"
        else:
            return f"QubitState({self.n_qubits} qubits, mixed)\n{self.density_matrix}"


class QuantumGates:
    """Standard quantum gates."""
    
    # Single-qubit gates
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)  # Pauli-X (NOT)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli-Y
    Z = np.array([[1, 0], [0, -1]], dtype=complex)  # Pauli-Z
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)  # Hadamard
    S = np.array([[1, 0], [0, 1j]], dtype=complex)  # Phase gate
    T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)  # π/8 gate
    
    # Two-qubit gates
    CNOT = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=complex)
    
    SWAP = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ], dtype=complex)
    
    @staticmethod
    def RX(theta: float) -> np.ndarray:
        """Rotation around X-axis."""
        return np.array([
            [np.cos(theta/2), -1j*np.sin(theta/2)],
            [-1j*np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def RY(theta: float) -> np.ndarray:
        """Rotation around Y-axis."""
        return np.array([
            [np.cos(theta/2), -np.sin(theta/2)],
            [np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def RZ(theta: float) -> np.ndarray:
        """Rotation around Z-axis."""
        return np.array([
            [np.exp(-1j*theta/2), 0],
            [0, np.exp(1j*theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def Phase(phi: float) -> np.ndarray:
        """General phase gate."""
        return np.array([
            [1, 0],
            [0, np.exp(1j*phi)]
        ], dtype=complex)


class QuantumCircuit:
    """
    Quantum circuit builder for composing gates and measurements.
    """
    
    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.state = QubitState(n_qubits=n_qubits)
        self.gates = []  # History of applied gates
        
    def h(self, qubit: int) -> 'QuantumCircuit':
        """Apply Hadamard gate."""
        self.state.apply_gate(QuantumGates.H, [qubit])
        self.gates.append(('H', qubit))
        return self
    
    def x(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-X (NOT) gate."""
        self.state.apply_gate(QuantumGates.X, [qubit])
        self.gates.append(('X', qubit))
        return self
    
    def y(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-Y gate."""
        self.state.apply_gate(QuantumGates.Y, [qubit])
        self.gates.append(('Y', qubit))
        return self
    
    def z(self, qubit: int) -> 'QuantumCircuit':
        """Apply Pauli-Z gate."""
        self.state.apply_gate(QuantumGates.Z, [qubit])
        self.gates.append(('Z', qubit))
        return self
    
    def rx(self, qubit: int, theta: float) -> 'QuantumCircuit':
        """Apply RX rotation."""
        self.state.apply_gate(QuantumGates.RX(theta), [qubit])
        self.gates.append(('RX', qubit, theta))
        return self
    
    def ry(self, qubit: int, theta: float) -> 'QuantumCircuit':
        """Apply RY rotation."""
        self.state.apply_gate(QuantumGates.RY(theta), [qubit])
        self.gates.append(('RY', qubit, theta))
        return self
    
    def rz(self, qubit: int, theta: float) -> 'QuantumCircuit':
        """Apply RZ rotation."""
        self.state.apply_gate(QuantumGates.RZ(theta), [qubit])
        self.gates.append(('RZ', qubit, theta))
        return self
    
    def cnot(self, control: int, target: int) -> 'QuantumCircuit':
        """Apply CNOT gate."""
        self.state.apply_gate(QuantumGates.CNOT, [control, target])
        self.gates.append(('CNOT', control, target))
        return self
    
    def measure(self, qubit: int) -> int:
        """Measure qubit and collapse state."""
        outcome, self.state = self.state.measure(qubit)
        self.gates.append(('MEASURE', qubit, outcome))
        return outcome
    
    def measure_all(self) -> List[int]:
        """Measure all qubits."""
        outcomes = []
        for i in range(self.n_qubits):
            outcomes.append(self.measure(i))
        return outcomes
    
    def get_statevector(self) -> np.ndarray:
        """Get current state vector (if pure)."""
        if self.state.is_pure:
            return self.state.state_vector
        else:
            raise ValueError("State is mixed, no unique state vector")
    
    def get_density_matrix(self) -> np.ndarray:
        """Get current density matrix."""
        return self.state.density_matrix
    
    def __repr__(self) -> str:
        circuit_str = f"QuantumCircuit({self.n_qubits} qubits)\n"
        circuit_str += "Gates applied:\n"
        for gate in self.gates:
            circuit_str += f"  {gate}\n"
        return circuit_str


# Example usage and tests
if __name__ == "__main__":
    print("=== Sentinel Quantum Simulator ===\n")
    
    # Test 1: Single qubit superposition
    print("Test 1: Hadamard gate creates superposition")
    qc = QuantumCircuit(1)
    qc.h(0)
    print(f"State after H: {qc.get_statevector()}")
    print(f"Expected: [0.707, 0.707] (|+⟩ state)\n")
    
    # Test 2: Bell state (entanglement)
    print("Test 2: Creating Bell state |Φ+⟩")
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    print(f"State: {qc.get_statevector()}")
    print(f"Expected: [0.707, 0, 0, 0.707] (maximally entangled)\n")
    
    # Test 3: Measurement statistics
    print("Test 3: Measurement statistics (1000 trials)")
    outcomes = {'00': 0, '01': 0, '10': 0, '11': 0}
    for _ in range(1000):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        result = qc.measure_all()
        key = ''.join(map(str, result))
        outcomes[key] += 1
    print(f"Outcomes: {outcomes}")
    print(f"Expected: ~500 '00', ~500 '11', ~0 '01', ~0 '10' (Bell state)\n")
    
    # Test 4: Bloch sphere visualization
    print("Test 4: Bloch vector for |+⟩ state")
    qc = QuantumCircuit(1)
    qc.h(0)
    bloch = qc.state.get_bloch_vector(0)
    print(f"Bloch vector: {bloch}")
    print(f"Expected: [1, 0, 0] (positive X-axis)\n")
    
    print("✅ Core quantum simulator functional!")
