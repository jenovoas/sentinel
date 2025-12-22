#!/usr/bin/env python3
"""
Test simple de búsqueda en Google a través de Truth Algorithm
"""

from source_search import SourceSearchEngine, SearchProvider

def main():
    print("="*70)
    print("BÚSQUEDA EN GOOGLE - TRUTH ALGORITHM")
    print("="*70)
    print()
    
    # Crear engine con Google
    engine = SourceSearchEngine(provider=SearchProvider.GOOGLE)
    
    # Tu búsqueda
    claim = input("¿Qué quieres buscar? ")
    print()
    print(f"🔍 Buscando: {claim}")
    print()
    
    # Ejecutar búsqueda
    results = engine.search(claim, max_results=5)
    
    # Mostrar resultados
    print(f"\n{'='*70}")
    print(f"RESULTADOS: {len(results)} encontrados")
    print(f"{'='*70}\n")
    
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r.source_type.upper()}] {r.title}")
        print(f"   URL: {r.url}")
        print(f"   Confidence: {r.confidence*100:.1f}%")
        print(f"   Snippet: {r.snippet[:150]}...")
        print()

if __name__ == '__main__':
    main()
