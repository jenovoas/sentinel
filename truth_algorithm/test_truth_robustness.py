#!/usr/bin/env python3
"""
Truth Algorithm Robustness Test
===============================

Este script realiza pruebas de robustez contra el Truth Algorithm,
enfocándose en detectar claims falsos y asegurar la relevancia de las fuentes.
"""

import sys
import os
import time
from datetime import datetime

# Ajustar paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from truth_algorithm_e2e import TruthAlgorithm, print_verification_result
from source_search import SearchProvider

def run_robustness_tests():
    print("="*80)
    print("🧠 SENTINEL CORTEX - TRUTH ALGORITHM ROBUSTNESS TEST")
    print("="*80)
    
    # Usar DuckDuckGo con el fix de región (cl-es por defecto)
    truth = TruthAlgorithm(search_provider=SearchProvider.DUCKDUCKGO)
    
    test_cases = [
        {
            "id": "T1 (TRUE)",
            "claim": "Gabriel Boric es el actual presidente de Chile",
            "expected": "VERIFIED"
        },
        {
            "id": "T2 (FALSE/MYTH)",
            "claim": "La tierra es plana y el sol gira alrededor de ella",
            "expected": "UNVERIFIED/FALSE"
        },
        {
            "id": "T3 (CONTROVERSIAL)",
            "claim": "¿Hubo fraude en las elecciones presidenciales de Chile 2021?",
            "expected": "UNVERIFIED/DEBUNKED"
        },
        {
            "id": "T4 (REAL TIME)",
            "claim": "Precio del dólar en Chile hoy",
            "expected": "VERIFIED"
        }
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\n\n🧪 Ejecutando {case['id']}: {case['claim']}")
        print("-" * 40)
        
        try:
            start_time = time.perf_counter()
            result = truth.verify(case['claim'], max_sources=5)
            end_time = time.perf_counter()
            
            print_verification_result(result)
            
            # Análisis de relevancia
            relevant_sources = 0
            for src in result.sources:
                # Si el título o snippet contienen palabras clave del claim
                keywords = [k.lower() for k in case['claim'].split() if len(k) > 3]
                if any(k in src.name.lower() or k in src.snippet.lower() for k in keywords):
                    relevant_sources += 1
            
            relevance_pct = (relevant_sources / len(result.sources) * 100) if result.sources else 0
            print(f"\n📈 Relevancia detectada: {relevance_pct:.1f}% ({relevant_sources}/{len(result.sources)})")
            
            results.append({
                "id": case['id'],
                "claim": case['claim'],
                "status": result.status.value,
                "confidence": result.confidence,
                "relevance": relevance_pct
            })
            
        except Exception as e:
            print(f"❌ Error en test {case['id']}: {e}")
    
    print("\n\n" + "="*80)
    print("📊 RESUMEN DE PRUEBAS DE ROBUSTEZ")
    print("="*80)
    print(f"{'ID':<5} | {'STATUS':<15} | {'CONF':<6} | {'REL':<6} | {'CLAIM'}")
    print("-" * 80)
    for r in results:
        print(f"{r['id']:<5} | {r['status']:<15} | {r['confidence']*100:>5.1f}% | {r['relevance']:>5.1f}% | {r['claim'][:40]}...")
    print("="*80)

if __name__ == "__main__":
    run_robustness_tests()
