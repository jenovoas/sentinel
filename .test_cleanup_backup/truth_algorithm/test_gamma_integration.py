#!/usr/bin/env python3
"""
Truth Algorithm + Guardian Gamma - Integration Test
====================================================

Test de integración que simula certificar una decisión de Guardian Gamma.

"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import json
from datetime import datetime
from certification_generator import CertificationGenerator
from source_search import SearchProvider


def test_gamma_integration():
    """Test de integración con Guardian Gamma"""
    
    print("="*70)
    print("🛡️  TRUTH ALGORITHM + GUARDIAN GAMMA - INTEGRATION TEST")
    print("="*70)
    print()
    
    # Simular una decisión de Guardian Gamma
    gamma_decision = {
        "decision_id": "gamma_001",
        "timestamp": datetime.utcnow().isoformat(),
        "context": "Sentinel Cortex reduce packet drops en 67% durante bursts de tráfico",
        "decision": "APPROVE",
        "confidence": 0.85,
        "user_feedback": None
    }
    
    print("📋 Decisión de Guardian Gamma:")
    print(json.dumps(gamma_decision, indent=2))
    print()
    
    # Certificar la decisión con Truth Algorithm
    print("🔍 Certificando decisión con Truth Algorithm...")
    print()
    
    # Usar Perplexity si está disponible, sino MOCK
    api_key = os.getenv('PERPLEXITY_API_KEY')
    provider = SearchProvider.PERPLEXITY if api_key else SearchProvider.MOCK
    
    if not api_key:
        print("⚠️  PERPLEXITY_API_KEY no configurada, usando MOCK")
        print()
    
    generator = CertificationGenerator(provider=provider)
    certificate = generator.certify(gamma_decision["context"])
    
    # Agregar certificación a la decisión
    gamma_decision["truth_score"] = certificate.truth_score
    gamma_decision["truth_confidence"] = certificate.confidence_level
    gamma_decision["truth_sources"] = certificate.sources_total
    gamma_decision["certification"] = {
        "certificate_id": certificate.certificate_id,
        "verdict": certificate.verdict,
        "provider": certificate.provider,
        "timestamp": certificate.timestamp
    }
    
    # Mostrar decisión certificada
    print("="*70)
    print("✅ DECISIÓN CERTIFICADA")
    print("="*70)
    print()
    print(json.dumps(gamma_decision, indent=2))
    print()
    
    # Análisis
    print("="*70)
    print("📊 ANÁLISIS DE CERTIFICACIÓN")
    print("="*70)
    print()
    print(f"Decision ID: {gamma_decision['decision_id']}")
    print(f"Decision: {gamma_decision['decision']}")
    print(f"Guardian Confidence: {gamma_decision['confidence']*100:.1f}%")
    print()
    print(f"Truth Score: {gamma_decision['truth_score']:.3f}")
    print(f"Truth Confidence: {gamma_decision['truth_confidence']}")
    print(f"Sources Verified: {gamma_decision['truth_sources']}")
    print(f"Verdict: {gamma_decision['certification']['verdict']}")
    print()
    
    # Determinar si hay alineación
    guardian_high = gamma_decision['confidence'] >= 0.7
    truth_high = gamma_decision['truth_score'] >= 0.7
    
    if guardian_high and truth_high:
        status = "✅✅ ALTA CONFIANZA - Guardian y Truth Algorithm alineados"
    elif guardian_high or truth_high:
        status = "⚠️  CONFIANZA MIXTA - Revisar discrepancia"
    else:
        status = "❌ BAJA CONFIANZA - Requiere revisión humana"
    
    print(f"Status: {status}")
    print()
    
    # Guardar decisión certificada
    output_file = "gamma_certified_decision.json"
    with open(output_file, 'w') as f:
        json.dump(gamma_decision, f, indent=2)
    
    print(f"💾 Decisión certificada guardada en: {output_file}")
    print()
    print("="*70)
    print("🎉 INTEGRACIÓN EXITOSA")
    print("="*70)
    print()
    print("Próximos pasos:")
    print("1. Integrar en backend de Guardian Gamma")
    print("2. Mostrar Truth Score en UI")
    print("3. Agregar badge de certificación")
    print("4. Crear endpoint /api/gamma/certify/{decision_id}")
    print()


if __name__ == '__main__':
    test_gamma_integration()
