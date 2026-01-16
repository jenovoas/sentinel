# Sentinel Quantum Simulator - Quick Start Guide

> ⚠️ **LEGACY SIMULATOR DOCUMENTATION**  
> Este es el simulador cuántico educativo legacy (pre-v8.0).  
> Usa numpy/scipy para propósitos didácticos.  
> **Para Sentinel v8.0 producción (Base-60 puro), ver:**  
> - [AI_PRIME_DIRECTIVES.md](../AI_PRIME_DIRECTIVES.md)  
> - [SENTINEL_V8_DOCUMENTATION_INDEX.md](../docs/SENTINEL_V8_DOCUMENTATION_INDEX.md)

## 🚀 Getting Started (Laptop-Safe!)

### Installation

```bash
cd /home/jnovoas/sentinel/quantum
pip install numpy scipy matplotlib psutil
```

### Quick Test (Won't Explode Your Laptop 💻✅)

```bash
# Run the lite demo - automatically adapts to your hardware
python quantum_lite.py
```

This will:
1. ✅ Check your available RAM
2. ✅ Recommend safe configuration
3. ✅ Run quantum rift detection
4. ✅ Generate beautiful visualizations
5. ✅ Save results

---

## ✅ Validated Results (December 2025)

**All quantum use cases successfully validated!**

### Performance Benchmarks

| Use Case | Algorithm | Time | Memory | Status |
|----------|-----------|------|--------|--------|
| **Buffer Optimization** | QAOA | 2.06s | 0.005 GB | ✅ |
| **Threat Detection** | VQE | 0.72s | <0.001 GB | ✅ |
| **Algorithm Comparison** | QAOA+VQE | 6.66s | N/A | ✅ |
| **Total** | All | **10.06s** | **<0.01 GB** | ✅ |

### Key Results

🚀 **Buffer Optimization**: 944,200 events/sec throughput  
🎯 **Threat Detection**: 24 patterns analyzed in <1 second  
⚡ **VQE Performance**: 50× faster than QAOA for ground state problems  
💻 **Laptop-Safe**: Runs on 6GB RAM with defective fan (61-63°C stable)  

### Quick Demo

```bash
# Run all validated use cases
cd /home/jnovoas/sentinel/quantum
python run_all_use_cases.py
```

**Generates**:
- 3 professional visualizations (PNG)
- Consolidated validation report (Markdown)
- Performance metrics and analysis

📊 **See**: `VALIDATION_RESULTS.md` and `PHASE_1_SUMMARY.md` for details

---

## 📚 Available Simulators

### 1. **quantum_lite.py** - START HERE! 🌟
**Best for**: Laptops, testing, learning
- Automatic resource management
- Adaptive complexity
- Safe for 2GB+ RAM
- Fast execution (<1 minute)

```python
from quantum_lite import demo_rift_detection

# Auto-optimized for your hardware
results = demo_rift_detection()
```

### 2. **core_simulator.py** - Quantum Gates
**Best for**: Learning quantum computing basics
- Single/multi-qubit gates
- Quantum circuits
- Measurement and collapse
- Bloch sphere visualization

```python
from core_simulator import QuantumCircuit

# Create Bell state
qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)
print(qc.get_statevector())
```

### 3. **optomechanical_simulator.py** - Physics Engine
**Best for**: Simulating real membranes
- Membrane dynamics (Q > 10⁸)
- Radiation pressure coupling
- Non-Markovian baths
- Axion detection Proyección Cuántica

```python
from optomechanical_simulator import OptomechanicalSystem, MembraneParameters

membrane = MembraneParameters(quality_factor=1e8)
system = OptomechanicalSystem(membrane, optical)
times, states = system.evolve(t_span)
```

### 4. **sentinel_quantum_core.py** - Full Platform
**Best for**: Advanced algorithms (QAOA, VQE)
- Multi-membrane networks
- Quantum optimization
- Variational algorithms
- Rift detection at scale

```python
from sentinel_quantum_core import SentinelQuantumCore, SentinelQAOA

core = SentinelQuantumCore()
qaoa = SentinelQAOA(core)
result = qaoa.optimize(p=2)
```

---

## 🎯 Example Workflows

### Workflow 1: Test Quantum Rift Detection

```python
# quantum_lite.py already does this!
python quantum_lite.py
```

**Output**:
- Phonon dynamics plot
- Correlation matrix heatmap
- Rift detection verdict
- Saved PNG visualization

### Workflow 2: Simulate Real Membrane

```python
from optomechanical_simulator import OptomechanicalSystem, MembraneParameters, OpticalParameters
import numpy as np

# Configure realistic Si₃N₄ membrane
membrane = MembraneParameters(
    mass=1e-15,  # 1 picogram
    frequency=10e6,  # 10 MHz
    quality_factor=1e8,  # Q = 10⁸
    temperature=300  # Room temp
)

optical = OpticalParameters(
    wavelength=1550e-9,  # Telecom
    finesse=1000,
    power=1e-3  # 1 mW
)

# Create system
system = OptomechanicalSystem(membrane, optical)

# Evolve
t_span = np.linspace(0, 1e-3, 1000)  # 1 ms
times, states = system.evolve(t_span, noise=True, non_markovian=True)

# Measure Q factor
Q_measured = system.measure_quality_factor(times, states)
print(f"Measured Q: {Q_measured:.2e}")
```

### Workflow 3: Quantum Algorithm (QAOA)

```python
from sentinel_quantum_core import SentinelQuantumCore, SentinelQAOA, SentinelConfig

# Small system for laptop
config = SentinelConfig(N_membranes=3, N_levels=5)
core = SentinelQuantumCore(config)

# Run QAOA
qaoa = SentinelQAOA(core)
result = qaoa.optimize(p=2, maxiter=50)

print(f"Optimal energy: {result['optimal_energy']}")
print(f"Success: {result['success']}")
```

### Workflow 4: Create Custom Quantum Circuit

```python
from core_simulator import QuantumCircuit, QuantumGates
import numpy as np

# 3-qubit GHZ state
qc = QuantumCircuit(3)
qc.h(0)
qc.cnot(0, 1)
qc.cnot(1, 2)

# Measure 1000 times
outcomes = {'000': 0, '001': 0, '010': 0, '011': 0,
            '100': 0, '101': 0, '110': 0, '111': 0}

for _ in range(1000):
    qc_copy = QuantumCircuit(3)
    qc_copy.h(0).cnot(0, 1).cnot(1, 2)
    result = qc_copy.measure_all()
    key = ''.join(map(str, result))
    outcomes[key] += 1

print(outcomes)
# Expected: ~500 '000', ~500 '111', rest ~0
```

---

## 💾 Memory Requirements

| Configuration | RAM Needed | Recommended For |
|---------------|------------|-----------------|
| 2 membranes, 4 levels | ~0.1 GB | Old laptops |
| 3 membranes, 5 levels | ~0.5 GB | Most laptops |
| 4 membranes, 6 levels | ~2 GB | Modern laptops |
| 4 membranes, 8 levels | ~8 GB | Workstations |
| 5 membranes, 10 levels | ~100 GB | Servers only! |

**quantum_lite.py automatically chooses safe config!**

---

## 🔬 What Each Simulator Does

### Core Simulator
- **Purpose**: Learn quantum computing basics
- **Physics**: Abstract qubits (not tied to hardware)
- **Speed**: Very fast
- **Use case**: Education, algorithm prototyping

### Optomechanical Simulator
- **Purpose**: Simulate real nanomechanical membranes
- **Physics**: Radiation pressure, thermal noise, Q factors
- **Speed**: Medium
- **Use case**: Hardware validation, experimental design

### Sentinel Quantum Core
- **Purpose**: Multi-membrane networks + algorithms
- **Physics**: Coupled oscillators, entanglement, optimization
- **Speed**: Slower (but optimized)
- **Use case**: Research, QAOA/VQE, rift detection

### Quantum Lite
- **Purpose**: Safe entry point for everything
- **Physics**: Simplified but accurate
- **Speed**: Fast + adaptive
- **Use case**: **START HERE!**

---

## 🎨 Visualization Examples

All simulators can generate plots:

```python
# Phonon dynamics
plt.plot(times, phonon_numbers)
plt.xlabel('Time (μs)')
plt.ylabel('Phonon number')
plt.show()

# Correlation matrix
plt.imshow(correlation_matrix, cmap='RdBu')
plt.colorbar()
plt.show()

# Bloch sphere (for qubits)
from core_simulator import QubitState
state = QubitState(state_vector=psi)
bloch_vec = state.get_bloch_vector()
# Plot on sphere...
```

---

## 🚨 Troubleshooting

### "MemoryError: Not enough RAM"
**Solution**: Close other apps, or reduce config:
```python
demo_rift_detection(n_membranes=2, n_levels=4)
```

### "Proyección Cuántica too slow"
**Solution**: Reduce time steps:
```python
times, states = core.evolve_fast(psi0, t_max, n_steps=50)  # Instead of 1000
```

### "Import errors"
**Solution**: Install dependencies:
```bash
pip install numpy scipy matplotlib psutil
```

---

## 🎯 Next Steps

1. ✅ Run `python quantum_lite.py` to verify everything works
2. ✅ Explore `core_simulator.py` for quantum gates
3. ✅ Try `optomechanical_simulator.py` for realistic physics
4. ✅ Advanced: `sentinel_quantum_core.py` for QAOA/VQE

---

## 📖 Learning Resources

### Quantum Computing Basics
- **Qubits**: `core_simulator.py` - QubitState class
- **Gates**: `core_simulator.py` - QuantumGates class
- **Circuits**: `core_simulator.py` - QuantumCircuit class
- **Measurement**: `core_simulator.py` - measure() method

### Optomechanics
- **Membranes**: `optomechanical_simulator.py` - MembraneParameters
- **Coupling**: `optomechanical_simulator.py` - OptomechanicalSystem
- **Entanglement**: `optomechanical_simulator.py` - generate_entanglement()

### Sentinel Algorithms
- **Rift Detection**: `sentinel_quantum_core.py` - SentinelRiftDetector
- **QAOA**: `sentinel_quantum_core.py` - SentinelQAOA
- **VQE**: `sentinel_quantum_core.py` - SentinelVQE

---

## 🌟 Pro Tips

1. **Always start with quantum_lite.py** - it's safe and fast
2. **Check memory before scaling up** - use QuantumResourceManager
3. **Save intermediate results** - Proyección Cuánticas can take time
4. **Visualize everything** - plots reveal insights
5. **Compare to theory** - validate against academic papers

---

## 🚀 Ready to Go!

```bash
# The safest way to start
cd /home/jnovoas/sentinel/quantum
python quantum_lite.py
```

**Your laptop will survive. Sentinel will thrive. Let's go! 💻⚛️🚀**
