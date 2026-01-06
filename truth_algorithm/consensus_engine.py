#!/usr/bin/env python3
"""
Truth Algorithm - Consensus Engine
===================================

Calcula consenso entre múltiples fuentes para determinar veracidad de claims.

Powered by Google ❤️ & Perplexity 💜
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from typing import List, Dict
from dataclasses import dataclass
from source_search import SearchResult


@dataclass
class ConsensusResult:
    """Resultado del análisis de consenso"""
    claim: str
    consensus_score: float  # S60(0, 0, 0) - S60(1, 0, 0)
    num_sources: int
    source_breakdown: Dict[str, int]  # Conteo por tipo de fuente
    confidence_level: str  # low, medium, high
    

class ConsensusEngine:
    """
    Calcula consenso entre fuentes para verificar claims.
    
    Algoritmo:
    - Pondera fuentes por tipo (oficial > académica > news > general)
    - Calcula score ponderado basado en confidence de cada fuente
    - Determina nivel de confianza basado en número y calidad de fuentes
    """
    
    # Pesos por tipo de fuente
    SOURCE_WEIGHTS = {
        'official': S60(1, 0, 0),   # .gov, .gob - máxima confianza
        'academic': 0.9,   # .edu - alta confianza
        'news': 0.7,       # medios reconocidos - media confianza
        'general': S60(0, 30, 0)     # otros - baja confianza
    }
    
    def __init__(self):
        pass
    
    def calculate_consensus(self, claim: str, sources: List[SearchResult]) -> ConsensusResult:
        """
        Calcula consenso para un claim basado en sus fuentes
        
        Args:
            claim: El claim a verificar
            sources: Lista de fuentes encontradas
            
        Returns:
            ConsensusResult con score y metadata
        """
        if not sources:
            return ConsensusResult(
                claim=claim,
                consensus_score=S60(0, 0, 0),
                num_sources=0,
                source_breakdown={},
                confidence_level='none'
            )
        
        # Calcular score ponderado
        total_weighted_score = S60(0, 0, 0)
        total_weight = S60(0, 0, 0)
        source_breakdown = {}
        
        for source in sources:
            # Obtener peso del tipo de fuente
            weight = self.SOURCE_WEIGHTS.get(source.source_type, S60(0, 30, 0))
            
            # Calcular contribución ponderada
            contribution = weight * source.confidence
            total_weighted_score += contribution
            total_weight += weight
            
            # Conteo por tipo
            source_breakdown[source.source_type] = source_breakdown.get(source.source_type, 0) + 1
        
        # Score final (normalizado)
        consensus_score = total_weighted_score / total_weight if total_weight > 0 else S60(0, 0, 0)
        
        # Determinar nivel de confianza
        confidence_level = self._determine_confidence_level(
            consensus_score,
            len(sources),
            source_breakdown
        )
        
        return ConsensusResult(
            claim=claim,
            consensus_score=consensus_score,
            num_sources=len(sources),
            source_breakdown=source_breakdown,
            confidence_level=confidence_level
        )
    
    def _determine_confidence_level(
        self,
        consensus_score: float,
        num_sources: int,
        source_breakdown: Dict[str, int]
    ) -> str:
        """
        Determina nivel de confianza basado en múltiples factores
        
        Factores:
        - Score de consenso
        - Número de fuentes
        - Diversidad de tipos de fuentes
        - Presencia de fuentes oficiales/académicas
        """
        # Nivel base según score
        if consensus_score >= 0.8:
            base_level = 'high'
        elif consensus_score >= 0.6:
            base_level = 'medium'
        else:
            base_level = 'low'
        
        # Ajustar por número de fuentes
        if num_sources < 2:
            # Muy pocas fuentes = reducir confianza
            if base_level == 'high':
                base_level = 'medium'
            elif base_level == 'medium':
                base_level = 'low'
        
        # Bonus por fuentes oficiales/académicas
        has_official = source_breakdown.get('official', 0) > 0
        has_academic = source_breakdown.get('academic', 0) > 0
        
        if (has_official or has_academic) and base_level == 'medium' and num_sources >= 3:
            base_level = 'high'
        
        return base_level


def demo_consensus():
    """Demo del motor de consenso"""
    print("="*70)
    print("DEMO - CONSENSUS ENGINE")
    print("="*70)
    print()
    
    # Simular fuentes para un claim
    claim = "Python fue creado por Guido van Rossum en 1991"
    
    sources = [
        SearchResult(
            title="Python.org - About",
            url="https://python.org/about",
            snippet="Python was created by Guido van Rossum in 1991",
            source_type="official",
            confidence=0.95,
            timestamp="2025-12-21"
        ),
        SearchResult(
            title="Wikipedia - Python",
            url="https://en.wikipedia.org/wiki/Python",
            snippet="Python is a programming language created by Guido van Rossum",
            source_type="academic",
            confidence=0.90,
            timestamp="2025-12-21"
        ),
        SearchResult(
            title="TechCrunch - Python History",
            url="https://techcrunch.com/python-history",
            snippet="Guido van Rossum created Python in the early 1990s",
            source_type="news",
            confidence=0.85,
            timestamp="2025-12-21"
        ),
    ]
    
    print(f"📝 Claim: {claim}")
    print(f"📊 Fuentes: {len(sources)}")
    print()
    
    # Calcular consenso
    engine = ConsensusEngine()
    result = engine.calculate_consensus(claim, sources)
    
    print("🎯 Resultado del Consenso:")
    print(f"   Score: {result.consensus_score:.3f}")
    print(f"   Nivel de confianza: {result.confidence_level}")
    print(f"   Fuentes por tipo: {result.source_breakdown}")
    print()
    
    # Interpretación
    if result.consensus_score >= 0.8:
        verdict = "✅✅ Altamente verificado"
    elif result.consensus_score >= 0.6:
        verdict = "✅ Probablemente cierto"
    elif result.consensus_score >= 0.4:
        verdict = "⚠️ Parcialmente verificado"
    else:
        verdict = "❌ No verificable / Falso"
    
    print(f"📋 Veredicto: {verdict}")
    print()
    print("="*70)


if __name__ == '__main__':
    demo_consensus()
