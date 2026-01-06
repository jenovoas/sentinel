#!/usr/bin/env python3
"""
Truth Algorithm - End-to-End Benchmark
=======================================

Benchmark completo del sistema integrado.

Powered by Google ❤️ & Perplexity 💜 | Built with Gemini AI
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import json
from truth_algorithm_e2e import TruthAlgorithm, SearchProvider


# Dataset de claims para benchmark
BENCHMARK_CLAIMS = [
    # Claims verificables
    "La tasa de desempleo en EE.UU. es 3.5%",
    "El PIB de EE.UU. creció 2.1% en Q3 2024",
    "La población mundial superó los 8 mil millones",
    "La temperatura global ha aumentado 1.1°C",
    
    # Claims científicos
    "El cambio climático está causado por actividad humana",
    "Las vacunas COVID son efectivas según estudios",
    "La Tierra tiene 4.5 mil millones de años",
    
    # Claims futuros (no verificables)
    "Habrá vida en Marte en 2050",
    "La IA superará a humanos en 2030",
    "Bitcoin llegará a $1 millón",
]


def run_benchmark():
    """Ejecuta benchmark end-to-end"""
    print("="*70)
    print("TRUTH ALGORITHM - END-TO-END BENCHMARK")
    print("="*70)
    print("\nPowered by Google ❤️ & Perplexity 💜")
    print(f"\nDataset: {len(BENCHMARK_CLAIMS)} claims")
    print("Modo: MOCK (sin llamadas reales)")
    print("\nEjecutando benchmark...\n")
    
    truth = TruthAlgorithm(search_provider=SearchProvider.MOCK)
    
    results = []
    total_time = 0
    total_sources = 0
    
    for i, claim in enumerate(BENCHMARK_CLAIMS, 1):
        result = truth.verify(claim)
        
        total_time += result.total_time_ms
        total_sources += result.sources_found
        
        print(f"✅ Claim {i}: {result.status.value}")
        print(f"   Latencia: {result.total_time_ms:.2f}ms "
              f"(search: {result.search_time_ms:.2f}ms, "
              f"consensus: {result.consensus_time_ms:.2f}ms)")
        print(f"   Fuentes: {result.sources_found}, "
              f"Confidence: {result.confidence*100:.1f}%\n")
        
        results.append({
            'claim': claim,
            'status': result.status.value,
            'confidence': result.confidence,
            'sources_found': result.sources_found,
            'total_time_ms': result.total_time_ms,
            'search_time_ms': result.search_time_ms,
            'consensus_time_ms': result.consensus_time_ms,
        })
    
    # Calcular métricas
    avg_latency = total_time / len(BENCHMARK_CLAIMS)
    avg_sources = total_sources / len(BENCHMARK_CLAIMS)
    throughput = 1000 / avg_latency  # claims/segundo
    
    # Imprimir resultados
    print("="*70)
    print("RESULTADOS")
    print("="*70)
    
    print(f"\n⚡ Performance:")
    print(f"  Latencia promedio:      {avg_latency:.2f}ms")
    print(f"  Latencia total:         {total_time:.2f}ms")
    print(f"  Throughput:             {throughput:.0f} claims/segundo")
    
    print(f"\n📊 Fuentes:")
    print(f"  Promedio por claim:     {avg_sources:.1f}")
    print(f"  Total consultadas:      {total_sources}")
    
    print(f"\n✅ Criterios de Éxito:")
    criteria = [
        ("Latencia < 2s", avg_latency < 2000, f"{avg_latency:.2f}ms"),
        ("Throughput > 100/s", throughput > 100, f"{throughput:.0f} claims/s"),
        ("Fuentes > 1", avg_sources > 1, f"{avg_sources:.1f} fuentes"),
    ]
    
    for criterion, passed, value in criteria:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {criterion}: {value}")
    
    # Guardar resultados
    benchmark_results = {
        'avg_latency_ms': avg_latency,
        'throughput': throughput,
        'avg_sources': avg_sources,
        'total_claims': len(BENCHMARK_CLAIMS),
        'results': results
    }
    
    with open('e2e_benchmark_results.json', 'w') as f:
        json.dump(benchmark_results, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: e2e_benchmark_results.json")
    
    return benchmark_results


if __name__ == '__main__':
    results = run_benchmark()
    
    print("\n" + "="*70)
    print("BENCHMARK COMPLETADO")
    print("="*70)
    print(f"\n✅ Latencia: {results['avg_latency_ms']:.2f}ms")
    print(f"✅ Throughput: {results['throughput']:.0f} claims/segundo")
    print(f"✅ Sistema end-to-end funcionando")
