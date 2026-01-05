
import sys
import os
import asyncio
import logging

# Añadir el path para importar app
sys.path.append('/home/jnovoas/sentinel/backend')

from app.routers.health import biological_state
from consensus_algorithm import WeightedConsensusAlgorithm, Source, SourceType, VerificationStatus

# Configurar logging
logging.basicConfig(level=logging.INFO)

async def test_disonancia_logic():
    print("\n" + "="*70)
    print("TEST: LÓGICA DE PENALIZACIÓN POR DISONANCIA")
    print("="*70)

    algorithm = WeightedConsensusAlgorithm()
    claim = "La capital de Francia es París"
    
    # Mock sources that fully support the claim (Confidence 1.0)
    sources = [
        Source("Official Source", SourceType.OFFICIAL, True, 1.0, "2024-01-01"),
        Source("News Source", SourceType.NEWS_TIER1, True, 1.0, "2024-01-01")
    ]

    # CASE 1: Silencio Sistémico (Disonancia = 0)
    # Expected: VERIFIED, 100% confidence
    print("\n--- CASE 1: Silencio Sistémico (Disonancia = 0) ---")
    res1 = algorithm.verify_claim(claim, sources, disonancia=0.0)
    print(f"Status: {res1.status.value}")
    print(f"Confidence: {res1.confidence*100:.1f}%")
    print(f"Explanation: {res1.explanation}")

    # CASE 2: Ruido Moderado (Disonancia = 20)
    # Expected: PARTIAL, 80% confidence (Penalty 0.2)
    print("\n--- CASE 2: Ruido Moderado (Disonancia = 20) ---")
    res2 = algorithm.verify_claim(claim, sources, disonancia=20.0)
    print(f"Status: {res2.status.value}")
    print(f"Confidence: {res2.confidence*100:.1f}%")
    print(f"Explanation: {res2.explanation}")

    # CASE 3: Ruido Alto (Disonancia = 45)
    # Expected: PARTIAL, 55% confidence (Penalty 0.45)
    print("\n--- CASE 3: Ruido Alto (Disonancia = 45) ---")
    res3 = algorithm.verify_claim(claim, sources, disonancia=45.0)
    print(f"Status: {res3.status.value}")
    print(f"Confidence: {res3.confidence*100:.1f}%")
    print(f"Explanation: {res3.explanation}")

    # CASE 4: Veto por Caos (Disonancia = 60)
    # Expected: UNVERIFIED (VETO), 0% confidence
    print("\n--- CASE 4: Veto por Caos (Disonancia = 60) ---")
    res4 = algorithm.verify_claim(claim, sources, disonancia=60.0)
    print(f"Status: {res4.status.value}")
    print(f"Confidence: {res4.confidence*100:.1f}%")
    print(f"Explanation: {res4.explanation}")

    print("\n" + "="*70)
    print("TEST COMPLETADO")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_disonancia_logic())
