#!/usr/bin/env python3
"""
Test simple de Google Search - Sin dependencias de .env
Configura las credenciales directamente aquí para testing
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import sys

# ============================================================================
# CONFIGURACIÓN: Pon tus credenciales aquí SOLO para testing local
# IMPORTANTE: NO commitear este archivo con credenciales reales
# ============================================================================

# Opción 1: Descomentar y poner tus credenciales aquí
# os.environ['GOOGLE_SEARCH_API_KEY'] = "tu_api_key_aqui"
# os.environ['GOOGLE_SEARCH_CX'] = "80b08c4835fa24341"

# Opción 2: O pasarlas como argumentos
if len(sys.argv) == 3:
    os.environ['GOOGLE_SEARCH_API_KEY'] = sys.argv[1]
    os.environ['GOOGLE_SEARCH_CX'] = sys.argv[2]

# ============================================================================

from source_search import SourceSearchEngine, SearchProvider
import time

def test_google():
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    cx = os.getenv('GOOGLE_SEARCH_CX')
    
    print("="*70)
    print("TEST GOOGLE SEARCH")
    print("="*70)
    print()
    
    if not api_key or not cx:
        print("❌ Credenciales no configuradas")
        print()
        print("Opción 1: Editar este archivo y descomentar líneas 15-16")
        print("Opción 2: Ejecutar con argumentos:")
        print(f"   python {sys.argv[0]} TU_API_KEY 80b08c4835fa24341")
        return
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ CX ID: {cx}")
    print()
    
    # Crear engine
    engine = SourceSearchEngine(provider=SearchProvider.GOOGLE)
    
    # Test búsqueda
    claim = "Python programming language"
    print(f"🔍 Buscando: {claim}")
    print()
    
    start = time.time()
    results = engine.search(claim, max_results=5)
    elapsed = time.time() - start
    
    print(f"\n⏱️  Tiempo: {elapsed*1000:.2f}ms")
    print(f"📄 Resultados: {len(results)}")
    print()
    
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r.source_type}] {r.title[:60]}...")
        print(f"   Confidence: {r.confidence*100:.1f}%")
        print()

if __name__ == '__main__':
    test_google()
