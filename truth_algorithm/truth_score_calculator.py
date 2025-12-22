#!/usr/bin/env python3
"""
Truth Algorithm - Truth Score Calculator
=========================================

Calcula el Truth Score final basado en consenso de múltiples claims.

Powered by Google ❤️ & Perplexity 💜
"""

from typing import List, Dict
from dataclasses import dataclass
from consensus_engine import ConsensusResult


@dataclass
class TruthScore:
    """Score de veracidad final"""
    overall_score: float  # 0.0 - 1.0
    confidence_level: str  # low, medium, high
    claims_verified: int
    claims_total: int
    verification_rate: float  # % de claims verificados
    details: List[Dict]  # Detalles por claim


class TruthScoreCalculator:
    """
    Calcula Truth Score final para contenido completo.
    
    Combina scores de consenso de múltiples claims con penalizaciones
    por claims no verificables.
    """
    
    def calculate(self, consensus_results: List[ConsensusResult]) -> TruthScore:
        """
        Calcula Truth Score final
        
        Args:
            consensus_results: Resultados de consenso para cada claim
            
        Returns:
            TruthScore con score final y metadata
        """
        if not consensus_results:
            return TruthScore(
                overall_score=0.0,
                confidence_level='none',
                claims_verified=0,
                claims_total=0,
                verification_rate=0.0,
                details=[]
            )
        
        # Calcular score promedio ponderado
        total_score = 0.0
        verified_claims = 0
        details = []
        
        for result in consensus_results:
            total_score += result.consensus_score
            
            # Considerar verificado si score >= 0.6
            if result.consensus_score >= 0.6:
                verified_claims += 1
            
            # Agregar detalles
            details.append({
                'claim': result.claim,
                'score': result.consensus_score,
                'confidence': result.confidence_level,
                'sources': result.num_sources
            })
        
        # Score base (promedio)
        base_score = total_score / len(consensus_results)
        
        # Aplicar penalización por claims no verificados
        verification_rate = verified_claims / len(consensus_results)
        penalty = (1.0 - verification_rate) * 0.2  # Penalización del 20% por claim no verificado
        
        final_score = max(0.0, base_score - penalty)
        
        # Determinar nivel de confianza final
        confidence_level = self._determine_overall_confidence(
            final_score,
            verification_rate,
            consensus_results
        )
        
        return TruthScore(
            overall_score=final_score,
            confidence_level=confidence_level,
            claims_verified=verified_claims,
            claims_total=len(consensus_results),
            verification_rate=verification_rate,
            details=details
        )
    
    def _determine_overall_confidence(
        self,
        score: float,
        verification_rate: float,
        results: List[ConsensusResult]
    ) -> str:
        """Determina nivel de confianza general"""
        # Nivel base según score
        if score >= 0.8 and verification_rate >= 0.8:
            return 'high'
        elif score >= 0.6 and verification_rate >= 0.6:
            return 'medium'
        else:
            return 'low'


def demo_truth_score():
    """Demo del calculador de Truth Score"""
    print("="*70)
    print("DEMO - TRUTH SCORE CALCULATOR")
    print("="*70)
    print()
    
    # Simular resultados de consenso
    from consensus_engine import ConsensusResult
    
    results = [
        ConsensusResult(
            claim="Python fue creado por Guido van Rossum",
            consensus_score=0.95,
            num_sources=4,
            source_breakdown={'official': 1, 'academic': 2, 'news': 1},
            confidence_level='high'
        ),
        ConsensusResult(
            claim="Python fue lanzado en 1991",
            consensus_score=0.90,
            num_sources=3,
            source_breakdown={'official': 1, 'academic': 1, 'news': 1},
            confidence_level='high'
        ),
        ConsensusResult(
            claim="Python es usado en ciencia de datos",
            consensus_score=0.85,
            num_sources=3,
            source_breakdown={'academic': 2, 'news': 1},
            confidence_level='high'
        ),
    ]
    
    print(f"📊 Claims a verificar: {len(results)}")
    print()
    
    # Calcular Truth Score
    calculator = TruthScoreCalculator()
    truth_score = calculator.calculate(results)
    
    print("🎯 TRUTH SCORE FINAL:")
    print(f"   Score: {truth_score.overall_score:.3f}")
    print(f"   Confianza: {truth_score.confidence_level}")
    print(f"   Claims verificados: {truth_score.claims_verified}/{truth_score.claims_total}")
    print(f"   Tasa de verificación: {truth_score.verification_rate*100:.1f}%")
    print()
    
    # Interpretación
    if truth_score.overall_score >= 0.8:
        verdict = "✅✅ Contenido altamente verificado"
    elif truth_score.overall_score >= 0.6:
        verdict = "✅ Contenido probablemente cierto"
    elif truth_score.overall_score >= 0.4:
        verdict = "⚠️ Contenido parcialmente verificado"
    else:
        verdict = "❌ Contenido no verificable"
    
    print(f"📋 Veredicto: {verdict}")
    print()
    
    print("📝 Detalles por claim:")
    for i, detail in enumerate(truth_score.details, 1):
        print(f"   {i}. {detail['claim'][:50]}...")
        print(f"      Score: {detail['score']:.2f} | Fuentes: {detail['sources']}")
    
    print()
    print("="*70)


if __name__ == '__main__':
    demo_truth_score()
