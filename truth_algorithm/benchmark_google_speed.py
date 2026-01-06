#!/usr/bin/env python3
"""
Benchmark de velocidad - Google Search API
==========================================

Mide la velocidad de búsqueda usando Google Custom Search API.

SEGURIDAD:
- Las credenciales se leen desde variables de entorno
- NUNCA se hardcodean en el código
- El código es público-safe

Para ejecutar:
1. Configurar variables de entorno:
   export GOOGLE_SEARCH_API_KEY="tu_api_key"
   export GOOGLE_SEARCH_CX="tu_cx_id"

2. Ejecutar:
   python benchmark_google_speed.py

Powered by Google ❤️ & Perplexity 💜
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import time
from source_search import SourceSearchEngine, SearchProvider

# Intentar cargar desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()  # Carga variables desde .env
except ImportError:
    pass  # python-dotenv no instalado, usar solo variables de entorno

def benchmark_google_search():
    """
    Benchmark de velocidad para Google Search API
    """
    print("="*70)
    print("BENCHMARK - GOOGLE SEARCH SPEED")
    print("="*70)
    print()
    
    # Verificar credenciales (sin mostrarlas)
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    cx = os.getenv('GOOGLE_SEARCH_CX')
    
    print("🔐 Verificando credenciales...")
    if api_key:
        print(f"   ✅ API Key: {api_key[:10]}...{api_key[-4:]} (oculta)")
    else:
        print("   ❌ API Key: No configurada")
    
    if cx:
        print(f"   ✅ CX ID: {cx[:10]}...{cx[-4:]} (oculta)")
    else:
        print("   ❌ CX ID: No configurada")
    
    print()
    
    if not api_key or not cx:
        print("⚠️  Para ejecutar este benchmark necesitas:")
        print("   export GOOGLE_SEARCH_API_KEY='tu_api_key'")
        print("   export GOOGLE_SEARCH_CX='tu_cx_id'")
        print()
        print("💡 El código NUNCA expone tus credenciales")
        print("   Solo las lee desde variables de entorno")
        return
    
    # Crear engine con Google
    engine = SourceSearchEngine(provider=SearchProvider.GOOGLE)
    
    # Claims de prueba
    test_claims = [
        "Python programming language",
        "Artificial intelligence machine learning",
        "Climate change global warming",
        "Quantum computing technology",
        "Renewable energy sources"
    ]
    
    print(f"📊 Ejecutando {len(test_claims)} búsquedas de prueba...")
    print()
    
    times = []
    
    for i, claim in enumerate(test_claims, 1):
        print(f"Test {i}/{len(test_claims)}: {claim[:40]}...")
        
        start = time.time()
        try:
            results = engine.search(claim, max_results=5)
            elapsed = time.time() - start
            times.append(elapsed)
            
            print(f"   ⏱️  Tiempo: {elapsed*1000:.2f}ms")
            print(f"   📄 Resultados: {len(results)}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # Rate limiting: esperar 1 segundo entre búsquedas
        if i < len(test_claims):
            time.sleep(1)
    
    # Estadísticas
    if times:
        print("="*70)
        print("RESULTADOS")
        print("="*70)
        print()
        print(f"📊 Búsquedas completadas: {len(times)}")
        print(f"⏱️  Tiempo promedio: {sum(times)/len(times)*1000:.2f}ms")
        print(f"⚡ Tiempo mínimo: {min(times)*1000:.2f}ms")
        print(f"🐌 Tiempo máximo: {max(times)*1000:.2f}ms")
        print()
        print("💡 Nota: Incluye latencia de red + procesamiento de Google")
    
    print()
    print("="*70)
    print("🔐 SEGURIDAD: Tus credenciales NUNCA fueron expuestas en el código")
    print("="*70)

if __name__ == '__main__':
    benchmark_google_search()
