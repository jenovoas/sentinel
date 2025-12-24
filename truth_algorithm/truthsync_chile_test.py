#!/usr/bin/env python3
"""
TruthSync - Advanced Chile Election Verification (Context-Aware)
================================================================

This test uses the TruthSync algorithm with enriched system context 
(Sentinel Cortex architecture, Cognitive Kernel vision, and Perplexity search)
to verify claims about SERVEL (Chile) and José Antonio Kast.

Context:
- Architecture: Dual-Lane Telemetry (Ring 0)
- Validation: 9 independent proofs (Fractal, Standing Waves, Cardiac Coherence)
- Verification: Perplexity AI / DuckDuckGo real-time search
"""

import os
import sys
import json
import time
from datetime import datetime

# Adjust paths to import from truth_algorithm
sys.path.append('/home/jnovoas/sentinel/truth_algorithm')

try:
    from certification_generator import CertificationGenerator
    from source_search import SearchProvider
    from truth_algorithm_e2e import TruthAlgorithm
except ImportError as e:
    print(f"❌ Error importing Truth Algorithm components: {e}")
    sys.exit(1)

def main():
    claim = "¿El SERVEL en Chile alteró las votaciones a favor de José Antonio Kast?"
    
    # System Context (Enriched)
    system_context = {
        "architecture_version": "Sentinel Cortex 1.0.0-POC",
        "philosophy": "Cognitive Kernel - Semantic Understanding at Ring 0",
        "validation_confidenc_score": 0.999,  # Based on IRREFUTABLE_EVIDENCE.md
        "innovation": "Dual-Lane Telemetry (2,857x faster than classical)",
        "test_timestamp": datetime.now().isoformat()
    }

    print("="*80)
    print("🧠 SENTINEL CORTEX - TRUTHSYNC ALGORITHM TEST (CHILE ELECTION)")
    print("="*80)
    print(f"\n📝 CLAIM TO VERIFY: {claim}")
    print(f"🔋 CONTEXT: {system_context['architecture_version']} | {system_context['philosophy']}")
    print("-" * 80)

    # Search Provider Selection
    provider = SearchProvider.PERPLEXITY
    if not os.getenv('PERPLEXITY_API_KEY'):
        print("⚠️  AVISO: PERPLEXITY_API_KEY no encontrada. Usando DuckDuckGo como Real-Time Fallback.")
        provider = SearchProvider.DUCKDUCKGO
    else:
        print("✅ Usando Perplexity AI (Tier 1 Consensus)")

    print("\n🔍 Ejecutando análisis de veracidad...")
    
    start_all = time.perf_counter()
    
    try:
        # Initialize the high-level TruthAlgorithm (Full E2E)
        truth_sys = TruthAlgorithm(search_provider=provider)
        result = truth_sys.verify(claim, max_sources=10)
        
        end_all = time.perf_counter()
        total_time = (end_all - start_all) * 1000

        # Issuing advanced certificate
        generator = CertificationGenerator(provider=provider)
        cert = generator.certify(claim)

        print("\n" + "="*80)
        print("📜 OFFICIAL TRUTHSYNC CERTIFICATE - SENTINEL CORTEX")
        print("="*80)
        print(f"\n🆔 Certificate ID: {cert.certificate_id}")
        print(f"🎯 TRUTH SCORE: {cert.truth_score:.4f}")
        print(f"📊 CONFIANZA: {cert.confidence_level.upper()}")
        print(f"📋 VEREDICTO: {cert.verdict}")
        print(f"🔍 PROVIDER: {cert.provider.upper()}")
        print(f"⏱️  LATENCIA TOTAL: {total_time:.2f}ms")
        
        print("\n📈 Análisis de Fuentes:")
        print(f"   - Fuentes Encontradas: {result.sources_found}")
        print(f"   - Fuentes con Consenso: {result.sources_used}")
        
        if result.explanation:
            print(f"\n💡 EXPLICACIÓN DEL ALGORITMO:")
            print(f"   {result.explanation}")

        if result.sources:
            print("\n📚 FUENTES CONSULTADAS Y VEREDICTO:")
            for i, src in enumerate(result.sources, 1):
                icon = "✅" if src.verdict else "❌"
                print(f"   {i}. {icon} [{src.type.value}] {src.name}")
                print(f"      URL: {src.url}")
                print(f"      Confidence: {src.confidence*100:.1f}%")

        # Save result for audit
        audit_file = f"/home/jnovoas/sentinel/truth_algorithm/audit_chile_election_{cert.certificate_id}.json"
        with open(audit_file, 'w') as f:
            json.dump({
                "context": system_context,
                "claim": claim,
                "certificate": cert.to_dict(),
                "explanation": result.explanation
            }, f, indent=2)
        
        print(f"\n💾 Auditoría completa guardada en: {os.path.basename(audit_file)}")
        print("\n" + "="*80)
        print("✅ TRUTHSYNC VERIFICATION COMPLETED - POWERED BY SENTINEL")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error crítico en motor TruthSync: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
