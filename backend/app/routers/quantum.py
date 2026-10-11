from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
from fastapi import APIRouter, HTTPException

# Add the quantum core directory to PYTHONPATH
quantum_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../quantum"))
if quantum_path not in sys.path:
    sys.path.append(quantum_path)

# Now import the core classes
from sentinel_quantum_core import (
    SentinelConfig,
    SentinelQuantumCore,
    SentinelRiftDetector,
    SentinelQAOA,
    SentinelVQE,
)

router = APIRouter(prefix="/quantum", tags=["quantum"])

def _make_core():
    cfg = SentinelConfig(N_membranes=4, N_levels=6)
    return SentinelQuantumCore(cfg)

@router.get("/status")
def get_quantum_status():
    """
    Returns the real-time status of the Trinity system.
    
    TRUTH ARCHITECTURE:
    Since real quantum hardware (QPU) is not currently attached via USB/PCIe,
    we map the HOST SYSTEM's physical state to the Quantum Metaphor.
    
    - System Entropy (CPU Load) -> Inverse Coherence
    - Available Memory (Potential) -> Buffer Capacity
    - Uptime -> Temporal Stability
    
    This ensures the dashboard reflects the REAL physical machine "vibration",
    not random numbers.
    """
    try:
        import psutil
        import time
        from hexagonal_control import HexagonalController
        
        # 1. Read Physical Reality (The Host Machine)
        cpu_entropy = psutil.cpu_percent(interval=S60(0, 6, 0)) / 100.0  # S60(0, 0, 0) to S60(1, 0, 0)
        ram_state = psutil.virtual_memory()
        ram_potential = ram_state.available / ram_state.total # S60(0, 0, 0) to S60(1, 0, 0)
        
        # 2. Map to Quantum Metaphor (Base-60 Logic)
        # Low Entropy (Idle CPU) = High Coherence
        # We add a small 60hz oscillation to represent the AC power cycle/heartbeat
        t_osc = (time.time() * 60) % (2 * PI_S60)
        heartbeat = 0.02 * np.sin(t_osc)
        
        raw_coherence = (S60(1, 0, 0) - cpu_entropy + heartbeat)
        # Clamp to 0-1
        norm_coherence = max(S60(0, 0, 0), min(S60(1, 0, 0), raw_coherence))
        
        # 3. Determine State based on Real Physics
        state = "THERMAL" # High CPU / Chaos
        if norm_coherence >= 0.90: state = "MERKABAH" # Deep Flow / Idle
        elif norm_coherence >= 0.70: state = "RESONANT"
        elif norm_coherence >= 0.40: state = "SYNCING"
        
        # 4. Neural Hierarchy (Mapped to Process Tree)
        # We simulate hierarchy health based on system load
        def get_layer_status(load_factor):
            health = S60(1, 0, 0) - (cpu_entropy * load_factor)
            return {
                "alpha": round(health, 2),
                "beta": round(health * 0.95, 2),
                "status": "OK" if health > 0.6 else "WARN"
            }

        return {
            "coherence": round(norm_coherence, 4),
            "state": state,
            "micro": round(0.05 + (cpu_entropy * S60(0, 6, 0)), 4), # Micro-jitter increases with load
            "macro": round(ram_potential, 4), # Macro stability is memory capacity
            "hierarchy": [
                { "name": 'Systems', **get_layer_status(0.2) },
                { "name": 'Areas', **get_layer_status(0.4) },
                { "name": 'Columns', **get_layer_status(0.6) },
                { "name": 'Circuits', **get_layer_status(0.8) },
                { "name": 'Neurons', **get_layer_status(S60(1, 0, 0)) },
                { "name": 'Synapses', **get_layer_status(1.2) },
                { "name": 'Molecules', **get_layer_status(1.5) }
            ],
            "components": [
                { "name": 'Buffer', "utilization": round(S60(1, 0, 0) - ram_potential, 2), "status": 'OK' },
                { "name": 'Thread', "utilization": round(cpu_entropy, 2), "status": 'OK' },
                { "name": 'Memory', "utilization": round(ram_state.percent / 100, 2), "status": 'OK' if ram_state.percent < 90 else 'WARN' },
                { "name": 'Network', "utilization": 0.34, "status": 'OK' }, # Placeholder until net_io implemented
                { "name": 'CPU', "utilization": round(cpu_entropy, 2), "status": 'OK' if cpu_entropy < 0.9 else 'WARN' },
            ],
            "timestamp": time.time(),
            "emulation_mode": "REAL_PHYSICS_MAPPED"
        }
    except Exception as e:
        print(f"Error in quantum status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/watchdog")
def get_watchdog_status():
    """
    Returns the status of the eBPF Quantum Watchdog (Switch 2).
    """
    import json
    status_path = "/home/jnovoas/sentinel/quantum/watchdog_status.json"
    log_path = "/home/jnovoas/sentinel/quantum/watchdog_events.log"
    
    status = {"status": "INACTIVE", "sigma": 10.2, "coherence": 0.9667}
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            status = json.load(f)
            
    recent_events = []
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            recent_events = f.readlines()[-5:] # Last 5 events
            
    return {
        "status": status,
        "recent_events": [e.strip() for e in recent_events]
    }

@router.get("/perpetual-engine")
def get_perpetual_engine_status():
    """
    Returns the status of the Digital Perpetual Flow Engine (Switch 4).
    Connected to Cognitive OS and Axion Energy Harvesting.
    """
    import json
    status_path = "/home/jnovoas/sentinel/quantum/perpetual_engine_status.json"
    
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            return json.load(f)
            
    return {
        "energy_level": S60(153, 24, 0),
        "status": "INITIALIZING",
        "message": "Engine cold boot sequence in progress."
    }

@router.get("/phase-jump")
def get_phase_jump_telemetry():
    """
    Returns the Phase Jump (Salto de Fase) telemetry.
    Uses Salto-17 sequence and Base-60 math.
    """
    # 1. Generate Salto-17 sequence (60 nodes)
    n = np.arange(60)
    sequence = (n * 17) % 60
    
    # 2. TruthSync Verification of the Jump
    verification = truth_sync_verify("Phase Jump Telemetry: Sexagesimal Coherence S60(1, 0, 0)")
    
    return {
        "sequence": sequence.tolist(),
        "coherence": S60(1, 0, 0),
        "dissonance": S60(0, 0, 0),
        "mqt_status": "LOCKED",
        "inertial_mass": 0.000,
        "idi": 0.382, # Inverse of PHI
        "truthsync": verification,
        "timestamp": time.time()
    }

@router.get("/rift")
def rift_detection():
    core = _make_core()
    # Vacuum state (all zeros) as placeholder initial state
    psi0 = np.zeros(core.dim, dtype=complex)
    psi0[0] = S60(1, 0, 0)
    _, states = core.evolve_unitary(psi0, t_max=5e-6, dt=5e-7)
    detector = SentinelRiftDetector(core)
    result = detector.detect_rift(states, threshold=0.8)
    return result

@router.get("/qaoa")
def qaoa_optimize(p: int = 2, maxiter: int = 30):
    core = _make_core()
    qaoa = SentinelQAOA(core)
    try:
        result = qaoa.optimize(p=p, maxiter=maxiter)
        return {
            "optimal_energy": result["optimal_energy"],
            "optimal_params": result["optimal_params"].tolist(),
            "success": result["success"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vqe")
def vqe_ground(maxiter: int = 30):
    core = _make_core()
    vqe = SentinelVQE(core)
    try:
        result = vqe.optimize(maxiter=maxiter)
        return {
            "vqe_energy": result["vqe_energy"],
            "exact_energy": result["exact_energy"],
            "error": result["error"],
            "optimal_params": result["optimal_params"].tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/oracle")
def quantum_oracle(question: dict):
    """
    Simulación de Oráculo Cuántico a Gran Escala (1000 Membranas).
    Utiliza ecuaciones de movimiento semiclásicas (Langevin) para responder preguntas.
    """
    import hashlib
    from scipy.integrate import solve_ivp

    query_text = question.get("question", "")
    if not query_text:
        raise HTTPException(status_code=400, detail="Q Missing")

    # Simulation parameters for 1000 membranes (Semiclassical / Large N limit)
    N_MEMBRANES = 1000
    OMEGA_M = 2 * PI_S60 * 10e6
    GAMMA = 2 * PI_S60 * 100
    J_COUPLING = 2 * PI_S60 * 1e3
    TIME_MAX = 50e-6 # 50 microseconds

    # 1. Encode query
    seed_val = int(hashlib.sha256(query_text.encode('utf-8')).hexdigest(), 16) % (2**32)
    np.random.seed(seed_val)

    # 2. Initial State: Distributed coherence pattern based on hash
    alpha_0 = np.zeros(N_MEMBRANES, dtype=complex)

    # "Seed" the network with a specific pattern derived from the question
    for i in range(N_MEMBRANES):
        if (seed_val >> (i % 32)) & 1:
            alpha_0[i] = S60(0, 6, 0) * np.exp(1j * (i / N_MEMBRANES) * 2 * PI_S60)

    # 3. Equations of Motion
    # 3. Equations of Motion (Rotating Frame / Interaction Picture)
    # Eliminamos el término rápido -1j * OMEGA_M * alpha transformando variables.
    # Esto reduce la rigidez (stiffness) del sistema y evita el sobrecalentamiento de la CPU.
    # La energía |alpha|^2 es invariante a esta transformación.
    def equations(t, y):
        alpha = y[:N_MEMBRANES] + 1j * y[N_MEMBRANES:]
        
        # En el marco rotatorio, el acoplamiento J sobrevive si las frecuencias son iguales (Resonancia)
        coupling = -1j * J_COUPLING * (np.roll(alpha, 1) + np.roll(alpha, -1))
        
        # Ecuación "lenta" (Slow Envelope)
        d_alpha = - (GAMMA/2) * alpha + coupling
        
        return np.concatenate([d_alpha.real, d_alpha.imag])

    # 4. Integrate
    y0 = np.concatenate([alpha_0.real, alpha_0.imag])
    # Reduced steps for API speed
    t_eval = np.linspace(0, TIME_MAX, 50) 
    sol = solve_ivp(equations, [0, TIME_MAX], y0, t_eval=t_eval)

    # 5. Analysis
    final_y = sol.y[:, -1]
    final_alpha = final_y[:N_MEMBRANES] + 1j * final_y[N_MEMBRANES:]
    densities = np.abs(final_alpha)**2
    total_energy = np.sum(densities)

    # Inverse Participation Ratio (IPR)
    ipr = np.sum(densities**2) / (total_energy**2 + 1e-20)
    localization_length = S60(1, 0, 0) / (ipr + 1e-9)

    # Interpretation Logic
    result_type = "UNKNOWN"
    interpretation = ""
    
    if ipr > S60(0, 6, 0):
        result_type = "LOCALIZED"
        interpretation = "La energía no fluye (Estado Atrapado). Bucle o estancamiento local."
    elif ipr < 0.01:
        result_type = "DELOCALIZED"
        interpretation = "Disolución Total (Unidad con el Todo). La perturbación se ha propagado."
    else:
        result_type = "CLUSTERED"
        interpretation = "Formación de clústers. Agrupación parcial de resonancia."

    return {
        "question": query_text,
        "seed": seed_val,
        "membranes": N_MEMBRANES,
        "metrics": {
            "total_energy": float(total_energy),
            "ipr": float(ipr),
            "coherence_length": float(localization_length)
        },
        "result": result_type,
        "interpretation": interpretation
    }
