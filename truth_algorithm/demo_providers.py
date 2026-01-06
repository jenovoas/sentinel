#!/usr/bin/env python3
"""
Demo de Providers - Truth Algorithm
====================================

Muestra todos los providers disponibles: MOCK, DuckDuckGo, Google, Perplexity

Powered by Google ❤️ & Perplexity 💜
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from source_search import SourceSearchEngine, SearchProvider


def demo_all_providers():
    """Demo de todos los providers"""
    print("="*70)
    print("TRUTH ALGORITHM - SOURCE SEARCH DEMO")
    print("="*70)
    print()
    
    claim = "Python programming language"
    providers = [
        (SearchProvider.MOCK, "🎭 MOCK (Testing)"),
        (SearchProvider.DUCKDUCKGO, "🦆 DuckDuckGo (Gratis)"),
        (SearchProvider.PERPLEXITY, "💜 Perplexity (IA Premium)"),
        (SearchProvider.GOOGLE, "🔍 Google (Requiere API)"),
    ]
    
    for provider, name in providers:
        print()
        print("="*70)
        print(f"Provider: {name}")
        print("="*70)
        
        engine = SourceSearchEngine(provider=provider)
        results = engine.search(claim, max_results=3)
        
        print(f"✅ Búsqueda exitosa: {len(results)} resultados")
        print()
        
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r.source_type}] {r.title[:60]}...")
            print(f"     Confidence: {r.confidence*100:.1f}%")
            print(f"     URL: {r.url[:60]}...")
        print()
    
    # Resumen
    print("="*70)
    print("RESUMEN")
    print("="*70)
    print()
    print("✅ MOCK: Siempre disponible para testing")
    print("🦆 DuckDuckGo: Gratis cuando esté instalado")
    print("   → pip install duckduckgo-search")
    print("💜 Perplexity: IA premium con fuentes verificadas")
    print("   → Requiere PERPLEXITY_API_KEY")
    print("   → https://www.perplexity.ai/settings/api")
    print("🔍 Google: Listo para cuando tengas API key")
    print("   → Requiere GOOGLE_SEARCH_API_KEY y GOOGLE_SEARCH_CX")
    print()
    print("💡 Recomendación por caso de uso:")
    print("   - Testing: MOCK")
    print("   - Gratis: DuckDuckGo")
    print("   - Máxima calidad: Perplexity")
    print("   - Volumen alto: Google")
    print()
    print("Powered by Google ❤️ & Perplexity 💜")


if __name__ == '__main__':
    demo_all_providers()
