#!/usr/bin/env python3
"""
Truth Algorithm - Benchmark Completo de Providers
==================================================

Compara velocidad y calidad de MOCK, DuckDuckGo y Perplexity.

Powered by Google ❤️ & Perplexity 💜
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import os
from certification_generator import CertificationGenerator
from source_search import SearchProvider


def benchmark_all_providers():
    """Benchmark completo de todos los providers"""
    
    print("="*70)
    print("🚀 TRUTH ALGORITHM - BENCHMARK COMPLETO")
    print("="*70)
    print()
    
    # Claims de prueba
    test_claims = [
        "Python programming language was created by Guido van Rossum in 1991",
        "The Earth orbits around the Sun",
        "Water boils at 100 degrees Celsius at sea level"
    ]
    
    # Providers a probar
    providers = [
        (SearchProvider.MOCK, "🎭 MOCK"),
        (SearchProvider.DUCKDUCKGO, "🦆 DuckDuckGo"),
        (SearchProvider.PERPLEXITY, "💜 Perplexity"),
    ]
    
    results = {}
    
    for provider, name in providers:
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print(f"{'='*70}\n")
        
        provider_results = []
        
        for i, claim in enumerate(test_claims, 1):
            print(f"Claim {i}/3: {claim[:50]}...")
            
            try:
                generator = CertificationGenerator(provider=provider)
                
                start = time.time()
                certificate = generator.certify(claim)
                elapsed = time.time() - start
                
                provider_results.append({
                    'claim': claim,
                    'score': certificate.truth_score,
                    'sources': certificate.sources_total,
                    'time': elapsed * 1000,  # ms
                    'confidence': certificate.confidence_level
                })
                
                print(f"  ✅ Score: {certificate.truth_score:.3f}")
                print(f"  📊 Fuentes: {certificate.sources_total}")
                print(f"  ⏱️  Tiempo: {elapsed*1000:.2f}ms")
                print()
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                print()
        
        results[name] = provider_results
    
    # Resumen comparativo
    print("\n" + "="*70)
    print("📊 RESUMEN COMPARATIVO")
    print("="*70)
    print()
    
    # Tabla de resultados
    print(f"{'Provider':<15} | {'Avg Score':<10} | {'Avg Sources':<12} | {'Avg Time':<10} | {'Status':<10}")
    print("-" * 70)
    
    for provider_name, provider_results in results.items():
        if provider_results:
            avg_score = sum(r['score'] for r in provider_results) / len(provider_results)
            avg_sources = sum(r['sources'] for r in provider_results) / len(provider_results)
            avg_time = sum(r['time'] for r in provider_results) / len(provider_results)
            
            status = "✅ OK" if avg_score > 0 else "⚠️  Low"
            
            print(f"{provider_name:<15} | {avg_score:<10.3f} | {avg_sources:<12.1f} | {avg_time:<10.2f} | {status:<10}")
    
    print()
    print("="*70)
    print("🏆 GANADORES POR CATEGORÍA")
    print("="*70)
    print()
    
    # Encontrar el mejor en cada categoría
    all_results = []
    for provider_name, provider_results in results.items():
        if provider_results:
            avg_score = sum(r['score'] for r in provider_results) / len(provider_results)
            avg_time = sum(r['time'] for r in provider_results) / len(provider_results)
            avg_sources = sum(r['sources'] for r in provider_results) / len(provider_results)
            all_results.append((provider_name, avg_score, avg_time, avg_sources))
    
    if all_results:
        # Mejor score
        best_score = max(all_results, key=lambda x: x[1])
        print(f"🎯 Mejor Truth Score: {best_score[0]} ({best_score[1]:.3f})")
        
        # Más rápido
        fastest = min(all_results, key=lambda x: x[2])
        print(f"⚡ Más Rápido: {fastest[0]} ({fastest[2]:.2f}ms)")
        
        # Más fuentes
        most_sources = max(all_results, key=lambda x: x[3])
        print(f"📚 Más Fuentes: {most_sources[0]} ({most_sources[3]:.1f} promedio)")
    
    print()
    print("="*70)
    print("💡 RECOMENDACIONES")
    print("="*70)
    print()
    print("🎭 MOCK: Testing y desarrollo (instantáneo)")
    print("🦆 DuckDuckGo: Producción gratis, claims generales (rápido)")
    print("💜 Perplexity: Claims técnicos específicos, máxima calidad (lento pero preciso)")
    print()
    print("="*70)


if __name__ == '__main__':
    # Verificar Perplexity API key
    if not os.getenv('PERPLEXITY_API_KEY'):
        print("⚠️  PERPLEXITY_API_KEY no configurada")
        print("   El benchmark de Perplexity usará fallback a MOCK")
        print()
    
    benchmark_all_providers()
