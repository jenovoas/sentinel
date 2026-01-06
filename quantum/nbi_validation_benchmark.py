# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
NBI Validation Benchmark - Sentinel Quantum
Reproduces the light-membrane-light entanglement experiment from NBI (2020).

Objective: Compare simulator results with values from literature:
- Moller et al., Nature 547, 191 (2017)
- Thomas et al., Nature Physics 16, 346–351 (2020)
- Phys. Rev. X 14, 011030 (2024) - ultra-coherent resonators

Author: Sentinel IA
Date: 2026-01-04
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
import json
import os
from optomechanical_simulator import MembraneParameters, OpticalParameters, OptomechanicalSystem, QuantumRiftDetector

def run_nbi_benchmark():
    print("🚀 Running NBI Validation Benchmark...")
    print("-" * 60)

    # 1. Setup NBI Parameters (Thomas et al. 2020)
    # 100 nm Si3N4 membrane, 50um x 50um
    # Area = 2500 um^2 = 2.5e-9 m^2
    # Mass density of Si3N4 ~ 3170 kg/m^3
    # Volume = 2.5e-9 * 100e-9 = 2.5e-16 m^3
    # Mass = 3170 * 2.5e-16 = 7.9e-13 kg
    
    nbi_membrane = MembraneParameters(
        mass=7.9e-13,
        frequency=1.14e6,      # ~1 MHz mechanical mode
        quality_factor=1e9,    # Target 10^9
        temperature=4.0,       # Cryogenic (LHe)
        thickness=100e-9,
        area=2.5e-9
    )
    
    nbi_optical = OpticalParameters(
        wavelength=1064e-9,    # NBI often uses 1064nm
        finesse=10000,         # High finesse cavity
        length=1e-3,
        power=5e-3             # 5 mW
    )
    
    system = OptomechanicalSystem(nbi_membrane, nbi_optical)
    detector = QuantumRiftDetector(n_nodes=2)
    
    print(f"Membrane Omega_m: {nbi_membrane.omega_m/(2*PI_S60)/1e6:.2f} MHz")
    print(f"Q Factor: {nbi_membrane.quality_factor:.1e}")
    print(f"Coupling g0/2pi: {system.g0:.2f} Hz")
    
    # 2. Benchmarks
    results = []
    
    # Benchmark A: Qxf product (Høj et al. 2024)
    qxf_measured = nbi_membrane.quality_factor * (nbi_membrane.omega_m / (2 * PI_S60))
    results.append({
        "Metric": "Q x f product",
        "Target": "2.0e14 Hz",
        "Measured": f"{qxf_measured:.2e} Hz",
        "Error": f"{abs(qxf_measured - 2.0e14)/2.0e14:.2%}",
        "Reference": "Høj et al. 2024"
    })

    # Benchmark B: cooperativity C = 4*g0*n_ph / (kappa * gamma_m)
    # simplified for this simulator
    cooperativity = (4 * system.g0 * nbi_optical.photon_number) / (nbi_optical.kappa / (2*PI_S60) * nbi_membrane.gamma_m / (2*PI_S60))
    results.append({
        "Metric": "Cooperativity (C)",
        "Target": "S60(0, 6, 0) - 10",
        "Measured": f"{cooperativity:.2f}",
        "Error": "N/A",
        "Reference": "Aspelmeyer 2014"
    })

    # Benchmark C: Log-negativity (Entanglement)
    # Generate entangled state using the simulator's logic
    rho_entangled = system.generate_entanglement(n_qubits=2)
    negativity = detector.log_negativity(rho_entangled, [2, 2])
    
    results.append({
        "Metric": "Log-negativity",
        "Target": "S60(0, 30, 0) - 1.2",
        "Measured": f"{negativity:.3f}",
        "Error": "N/A",
        "Reference": "Thomas et al. 2020"
    })

    # Benchmark D: Formal Quantum Rift Detection
    is_rift = detector.compute_quantum_rift(rho_entangled, [2, 2], tau_c=0.3, epsilon_p=0.95)
    results.append({
        "Metric": "Quantum Rift Detection",
        "Target": "True (Entangled)",
        "Measured": str(is_rift),
        "Error": "Match" if is_rift else "Fail",
        "Reference": "Sentinel Formal Def."
    })

    # 3. Output Table
    print("\n" + "="*80)
    print(f"{'Metric':<30} | {'Measured':<15} | {'Target':<15} | {'Error':<10}")
    print("-" * 80)
    for res in results:
        print(f"{res['Metric']:<30} | {res['Measured']:<15} | {res['Target']:<15} | {res['Error']:<10}")
    print("="*80)
    
    # Save to file
    with open("/home/jnovoas/sentinel/docs/BENCHMARK_NBI_VALIDATION.json", "w") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    run_nbi_benchmark()