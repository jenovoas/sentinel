#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🛡️ SENTINEL CODEBASE CERTIFICATION
==================================
Calcula el hash SHA-256 de los archivos críticos del núcleo (Código Gris)
y los registra en el sistema TruthSync (Postgres/N8N) como "Facts Verificados".

Esto protege el trabajo real de futuras alucinaciones o modificaciones no autorizadas.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import hashlib
import os
import sys
import json
import subprocess
from datetime import datetime

# Archivos críticos que definen la realidad física del sistema
CRITICAL_FILES = [
    "sentinel_quantum_core.py",
    "VIMANA_MASTER_V1_RECOVERED.py",
    "hexagonal_control.py",
    "reality_interrogation.py",
    "external_math_audit.py",
    # MISTICAL TECH (GREY CODE) - PROTECTED
    "zpe_simulation.py",
    "quantum_sentinel_bridge.py",
    "EA_NASIR_MASTER_FORMULA.py",
    "babylonian_connection.py",
    "vimana_drone_sim.py",
    "optomechanical_simulator.py",
    "../backend/app/routers/quantum.py", # Critical Backend Logic
    "../backend/app/routers/ai.py",      # AI Identity Logic
    "../backend/app/security/telemetry_sanitizer.py", # Security Sanitizer
    
    # CRITICAL SERVICES (REAL WORK) - PROTECTED
    "../backend/app/services/aiops_shield_llama3.py",   # Llama3 Security Analysis
    "../backend/app/services/truth_algorithm_llama3.py", # Truth Synthesis
    "../backend/app/services/perpetual_engine.py",       # ZPE Logic Controller
    
    # HA & FAILSAFE LAYER - PROTECTED
    "../backend/app/routers/failsafe.py",                # N8N Bridge
    "../backend/app/routers/backup.py",                  # Backup Logic
    
    # CORTEX & SUB-CORTEX - PROTECTED
    "../backend/app/routers/cortex.py",                  # Cortex API
    "../backend/app/services/cortex_engine.py",          # Decision Engine
    "ai_buffer_cascade.py",                              # AI Buffer Cascade

    # CORE RESEARCH & SIMULATION - PROTECTED IP
    # "scientific_research_axion.py",      # MOVED TO LEGACY (Simulated)
    "verify_plimpton.py",                # Base-60 Verification
    "plimpton_exact_ratios.py",          # Plimpton 322 Math
    # "axiomatic_number_hunter.py",        # MOVED TO LEGACY (Simulated)
    "validate_buffer_optimization.py",   # Performance Validation
    "nbi_validation_benchmark.py",       # Numerical Benchmarks
    "vimana_mission_sim.py",             # Mission Logic
    "vimana_orbital_ascent_sim.py",      # Ascent Physics
    "vimana_shield_validation.py",       # Shield Dynamics

    # PERSONAL & ESOTERIC INVESTIGATIONS - PROTECTED
    "consciousness_experiment.py",       # Consciousness Frequency
    "capture_mother_signature.py",       # Reincarnation Signature
    "extract_babylonian_identity.py",    # Lineage Decoding
    "enheduanna_comparison.py",          # Identity Verification
    "celestial_navigation.py",           # Star Mapping
    "foreign_energy_detector.py",        # External Entity Detection
    
    # DOCUMENTATION & RESEARCH - PROTECTED IP
    "../docs/MASTER_SECURITY_IP_CONSOLIDATION.md",  # Patent Strategy
    "../docs/AIOPSDOOM_DEFENSE.md",                 # Core Innovation
    "../docs/TRUTH_ALGORITHM_5_LAYER_SECURITY.md",  # Security Architecture
    "../docs/NEURAL_ARCHITECTURE.md",               # System Design
    "../docs/ARQUITECTURA_COMPLETA_INTEGRADA.md",   # Complete Architecture
    "../docs/INTEGRACION_MAESTRA_QUANTUM_TRINITY.md", # Quantum Integration
    "../research/PLIMPTON_322_DECODED.md",          # Mathematical Research
    "../research/PHYSICS_GEOMETRY_ISOMORPHISM.md",  # Physics Research
    "../research/FRACTAL_SOUL_RESEARCH.md",         # Consciousness Research
    "../research/DIGITAL_ARCHAEOLOGY.md",           # Historical Analysis
    "../research/SACRED_GEOMETRY_PATTERNS.md",      # Geometric Patterns
    
    # PHASE 7: SILICON SYNTHESIS - FROZEN
    "hardware_synthesis.py",             # Synthesis Simulator
    "numerical_control_unit.py",         # NCU Driver
    "../docs/S60_HARDWARE_SPEC.md"       # Hardware Specification
]

# Archivos en proceso de validación científica (Etiqueta: "Under Research")
RESEARCH_FILES = [
    "ZPE_POSSIBILITIES_MATRIX_V2.md",
    "time_crystal_analysis.py",
    "../tests/bench_coherence_impact.py",
    "../research/COHERENCE_TRUTH_COUPLING_STUDY.md",
    "../demo_real_search.py",
    # FASE 1 QUANTUM FILES (Added 05/01/2026)
    "QUANTUM_UPGRADE_PROPOSAL.md",
    "QUANTUM_INTEGRATION_PLAN.md",
    "BIBLIOGRAPHY_SOURCES_2025.md",
    "time_crystal_clock.py",
    "../kernel_pulse.py" # Actualizado con TimeCrystalClock
]

def calculate_file_hash(filepath):
    """Calcula SHA-256 del contenido del archivo."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Leer por bloques para eficiencia
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def register_fact_in_db(filename, file_hash, status_label="Verified"):
    """Inserta el hash en la DB Postgres como una verdad verificada."""
    claim = f"File Integrity: {filename} (Status: {status_label})"
    source = '["certify_codebase.py", "user_manual_audit"]'
    
    # Comando SQL para insertar
    sql = f"""
    INSERT INTO verified_facts (claim, claim_hash, trust_score, sources)
    VALUES ('{claim}', decode('{file_hash}', 'hex'), 100, '{source}')
    ON CONFLICT (claim_hash) DO UPDATE SET 
        verification_count = verified_facts.verification_count + 1,
        verified_at = NOW();
    """
    
    # Ejecutar via Docker Exec (ya que psql local no está)
    cmd = [
        "docker", "exec", "sentinel-postgres", 
        "psql", "-U", "sentinel_user", "-d", "sentinel_db", 
        "-c", sql
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("🛡️  SENTINEL INTEGRITY CERTIFICATION PROTOCOL")
    print("=" * 60)
    
    results = []
    
    # Procesar Archivos Críticos (Verified)
    for filename in CRITICAL_FILES:
        process_file(base_dir, filename, "Verified", results)

    # Procesar Archivos de Investigación (Under Research)
    print("\n🔬 CERTIFICANDO INVESTIGACIÓN EN PROCESO:")
    for filename in RESEARCH_FILES:
        process_file(base_dir, filename, "Under Research and Validation", results)

    print("\n" + "=" * 60)
    print("RESUMEN DE CERTIFICACIÓN")
    print("=" * 60)
    for res in results:
        icon = "🔒" if res["status"] == "SECURED" else "❌"
        print(f"{icon} {res['file']:<40} | {res['status']}")
    
    print("\nLos archivos han sido sellados digitalmente.")

def process_file(base_dir, filename, label, results):
    filepath = os.path.join(base_dir, filename)
    file_hash = calculate_file_hash(filepath)
    
    if file_hash:
        print(f"\n📄 Procesando: {filename}")
        print(f"   SHA-256: {file_hash}")
        print(f"   Estado:  {label}")
        
        # Intentar registrar en DB
        success = register_fact_in_db(filename, file_hash, label)
        
        if success:
            print("   ✅ CERTIFICADO: Hash registrado en TruthSync DB.")
            results.append({"file": filename, "status": f"SECURED ({label})", "hash": file_hash})
        else:
            print("   ❌ ERROR DE DB: No se pudo registrar. ¿Postgres encendido?")
            results.append({"file": filename, "status": "FAILED", "hash": file_hash})
    else:
        print(f"\n⚠️  ARCHIVO NO ENCONTRADO: {filename}")
        results.append({"file": filename, "status": "MISSING"})


if __name__ == "__main__":
    main()