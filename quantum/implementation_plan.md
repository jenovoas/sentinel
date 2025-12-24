# VQE Ansatz Improvement - Implementation Plan

## Problem Statement

The current `SentinelVQE.ansatz()` method is a placeholder that returns the initial state `|0⟩` without applying any variational transformations. This causes:
- **0% accuracy** in VQE ground state finding
- **Meaningless optimization** in threat detection use case
- **No quantum advantage** demonstration

## Proposed Solution

Implement a **hardware-efficient ansatz** that creates a parameterized quantum state through:
1. **Single-qubit rotations** (R_y gates) on each membrane level
2. **Entangling operations** (simulated CNOT-like coupling) between adjacent membranes
3. **Layered structure** for expressibility

### Technical Approach

The ansatz will transform the state vector through matrix operations that simulate:

```
|ψ(θ)⟩ = U_layer3(θ₃) U_layer2(θ₂) U_layer1(θ₁) |0⟩

where each layer applies:
  - R_y(θᵢ) rotation on each membrane
  - Coupling between adjacent membranes (beam-splitter-like)
```

## Code Changes

### File: `sentinel_quantum_core.py`

#### [MODIFY] `SentinelVQE.ansatz()` (lines 450-474)

**Current implementation:**
```python
def ansatz(self, params: np.ndarray) -> np.ndarray:
    n_layers = len(params) // self.core.N
    psi = np.zeros(self.core.dim, dtype=complex)
    psi[0] = 1.0  # Start from |0⟩
    
    for layer in range(n_layers):
        for i in range(self.core.N):
            theta = params[layer * self.core.N + i]
            pass  # ← PLACEHOLDER
    
    return psi
```

**New implementation:**
- Build rotation operators for each membrane using phonon creation/annihilation
- Apply rotations sequentially to evolve the state
- Add entangling layer between membranes
- Return properly transformed state vector

**Key changes:**
1. Implement `_rotation_operator(membrane_idx, theta)` helper method
2. Implement `_entangling_layer()` helper method
3. Apply transformations to `psi` in each layer
4. Ensure proper normalization

## Verification Plan

### 1. Unit Test: VQE Convergence
**File:** `test_vqe_improvement.py` (NEW)

**Test:** Verify that VQE finds ground state with >90% accuracy

```python
def test_vqe_ground_state_accuracy():
    config = SentinelConfig(N_membranes=4, N_levels=6)
    core = SentinelQuantumCore(config)
    vqe = SentinelVQE(core)
    
    result = vqe.optimize(maxiter=100)
    
    accuracy = 1.0 - (result['error'] / abs(result['exact_energy']))
    assert accuracy > 0.90, f"VQE accuracy {accuracy:.1%} below 90% threshold"
```

**Run command:**
```bash
cd /home/jnovoas/sentinel/quantum
python test_vqe_improvement.py
```

### 2. Integration Test: Algorithm Comparison
**File:** `demo_algorithms.py` (EXISTING)

**Test:** Re-run full algorithm demo and verify VQE accuracy improvement

**Run command:**
```bash
cd /home/jnovoas/sentinel/quantum
python demo_algorithms.py
```

**Expected output:**
- VQE accuracy: >90% (currently 0%)
- VQE energy close to exact ground state
- Updated visualization showing convergence

### 3. Use Case Validation: Threat Detection
**File:** `use_case_threat_detection.py` (EXISTING)

**Test:** Re-run threat detection with improved VQE

**Run command:**
```bash
cd /home/jnovoas/sentinel/quantum
python use_case_threat_detection.py
```

**Expected output:**
- Precision/Recall/F1 > 0% (currently all 0%)
- Optimized weights different from baseline
- Visual evidence of pattern detection improvement

### 4. Manual Verification: Visual Inspection

**Steps:**
1. Run `demo_algorithms.py`
2. Open generated `algorithm_comparison.png`
3. Verify VQE subplot shows:
   - Energy convergence curve (not flat line)
   - Accuracy >90% (not 0%)
   - Error bars showing optimization progress

## Success Criteria

- ✅ VQE accuracy >90% in `demo_algorithms.py`
- ✅ Threat detection metrics >0% in `use_case_threat_detection.py`
- ✅ Visual evidence of convergence in plots
- ✅ No performance regression (execution time <5s for VQE)

## Risk Mitigation

**Risk:** Ansatz too complex → slow optimization
- **Mitigation:** Start with 2-3 layers, profile performance

**Risk:** Numerical instability in state evolution
- **Mitigation:** Normalize state after each layer, add stability checks

**Risk:** Still low accuracy due to limited expressibility
- **Mitigation:** Document limitations, propose future improvements (more layers, different gates)
