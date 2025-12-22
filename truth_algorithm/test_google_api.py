#!/usr/bin/env python3
"""
Test Google Search API - Truth Algorithm
=========================================

Script para probar Google Custom Search API con credenciales reales.

Uso:
    export GOOGLE_SEARCH_API_KEY="tu_api_key"
    export GOOGLE_SEARCH_CX="80b08c4835fa24341"
    python test_google_api.py
"""

import os
from certification_generator import CertificationGenerator
from source_search import SearchProvider

def test_google_search():
    """Prueba Google Search API"""
    
    print("="*70)
    print("🔍 GOOGLE SEARCH API - TEST")
    print("="*70)
    print()
    
    # Verificar credenciales
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    cx = os.getenv('GOOGLE_SEARCH_CX')
    
    if not api_key:
        print("❌ GOOGLE_SEARCH_API_KEY no configurada")
        print()
        print("Configura con:")
        print("  export GOOGLE_SEARCH_API_KEY='tu_api_key'")
        return
    
    if not cx:
        print("❌ GOOGLE_SEARCH_CX no configurada")
        print()
        print("Configura con:")
        print("  export GOOGLE_SEARCH_CX='80b08c4835fa24341'")
        return
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ CX ID: {cx}")
    print()
    
    # Crear generador con Google
    print("🔍 Creando generador con Google Search...")
    generator = CertificationGenerator(provider=SearchProvider.GOOGLE)
    
    # Claim de prueba
    claim = "Python programming language was created by Guido van Rossum in 1991"
    
    print(f"📝 Claim: {claim}")
    print()
    print("🔍 Buscando con Google Custom Search API...")
    print()
    
    # Certificar
    certificate = generator.certify(claim)
    
    # Resultados
    print("="*70)
    print("🎯 RESULTADO")
    print("="*70)
    print()
    print(f"Truth Score: {certificate.truth_score:.3f}")
    print(f"Confianza: {certificate.confidence_level}")
    print(f"Veredicto: {certificate.verdict}")
    print()
    print(f"Claims verificados: {certificate.claims_verified}/{certificate.claims_total}")
    print(f"Fuentes consultadas: {certificate.sources_total}")
    print(f"Tiempo: {certificate.processing_time_ms:.2f}ms")
    print(f"Provider: {certificate.provider}")
    print()
    
    if certificate.sources_total > 1:
        print("✅ GOOGLE API FUNCIONANDO CORRECTAMENTE")
        print()
        print("Detalles de fuentes:")
        for i, detail in enumerate(certificate.claim_details, 1):
            print(f"  {i}. {detail['claim'][:60]}...")
            print(f"     Score: {detail['score']:.3f}")
            print(f"     Fuentes: {detail['sources']}")
        print()
        
        # Guardar certificado
        with open('google_test_certificate.json', 'w') as f:
            f.write(certificate.to_json(indent=2))
        print("💾 Certificado guardado en: google_test_certificate.json")
    else:
        print("⚠️  Google retornó pocas fuentes (posible problema con API)")
    
    print()
    print("="*70)

if __name__ == '__main__':
    test_google_search()
