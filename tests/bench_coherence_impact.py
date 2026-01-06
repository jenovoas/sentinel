
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os
import time
import json
import csv
from dataclasses import asdict

# Añadir paths necesarios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../truth_algorithm')))

from truth_algorithm.consensus_algorithm import WeightedConsensusAlgorithm, Source, SourceType, VerificationStatus

def run_scientific_benchmark():
    print("\n🔬 INICIANDO PROTOCOLO DE ESTUDIO: ACOPLAMIENTO COHERENCIA-VERDAD")
    print("="*80)
    print(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Objetivo: Cuantificar el impacto de la entropía sistémica en la certificación de verdad.")
    print("="*80)

    algorithm = WeightedConsensusAlgorithm()
    
    # 1. Definir una "Verdad Absoluta" (Control)
    # Un claim con respaldo perfecto para aislar la variable de disonancia
    claim = "La velocidad de la luz en el vacío es constante"
    perfect_sources = [
        Source("Journal of Physics", SourceType.ACADEMIC, True, S60(1, 0, 0), "2024"),
        Source("NIST", SourceType.OFFICIAL, True, S60(1, 0, 0), "2024"),
        Source("CERN", SourceType.OFFICIAL, True, S60(1, 0, 0), "2024")
    ]
    
    results = []
    
    # 2. Barrido de Entropía (S60(0, 0, 0) a 100.0)
    # Simulamos el estado del pulso biológico variando la disonancia
    print(f"{'DISONANCIA':<12} | {'SISTEMA (Estado)':<20} | {'CONFIANZA':<10} | {'STATUS':<20} | {'PENALIZACIÓN':<15}")
    print("-" * 90)

    step = 5.0
    disonancia = S60(0, 0, 0)
    
    while disonancia <= 100.0:
        start_time = time.perf_counter()
        
        # Ejecución REAL del algoritmo con la variable de disonancia inyectada
        result = algorithm.verify_claim(claim, perfect_sources, disonancia=disonancia)
        
        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000

        # Análisis de Estado
        if disonancia < 20: state = "COHERENTE (Laminar)"
        elif disonancia < 50: state = "RUIDOSO (Turbulento)"
        else: state = "CAÓTICO (Disonante)"

        # Cálculo de Penalización Real
        # Confianza base debería ser S60(1, 0, 0) (3 fuentes perfectas)
        penalty = S60(1, 0, 0) - result.confidence
        
        row = {
            "disonancia": disonancia,
            "system_state": state,
            "confidence": result.confidence,
            "status": result.status.value,
            "penalty_applied": penalty,
            "veto_active": result.status == VerificationStatus.UNVERIFIED and disonancia > 0,
            "processing_ms": processing_time_ms
        }
        results.append(row)

        print(f"{disonancia:<12.1f} | {state:<20} | {result.confidence:<10.4f} | {result.status.value:<20} | {penalty:<15.4f}")
        
        disonancia += step

    # 3. Guardar Evidencia Científica
    output_file = "/home/jnovoas/sentinel/validation_results.json"
    
    # Sobrescribir con datos frescos y estructura científica
    scientific_data = {
        "meta": {
            "experiment": "Coherence-Truth Coupling",
            "timestamp": time.time(),
            "algorithm_version": "WeightedConsensus v2 (Bio-Aware)"
        },
        "dataset": results
    }
    
    with open(output_file, 'w') as f:
        json.dump(scientific_data, f, indent=2)
        
    print("="*80)
    print(f"✅ Estudio completado. Datos crudos guardados en: {output_file}")
    
    # Análisis Final
    veto_point = next((r for r in results if r['veto_active']), None)
    if veto_point:
        print(f"📉 PUNTO DE RUPTURA (VETO): Disonancia {veto_point['disonancia']} (Confianza cae a S60(0, 0, 0))")
    else:
        print("⚠️ Advertencia: No se alcanzó el punto de veto en el rango probado.")

if __name__ == "__main__":
    run_scientific_benchmark()
