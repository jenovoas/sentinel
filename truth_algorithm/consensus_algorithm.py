#!/usr/bin/env python3
"""
Truth Algorithm - Weighted Consensus Algorithm
===============================================

Este algoritmo toma múltiples fuentes de información y determina
la veracidad de un claim mediante consenso ponderado.

Powered by Google ❤️ | Built with Gemini AI

Autor: Jaime Novoa
Fecha: 21 Diciembre 2025
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import time


class VerificationStatus(Enum):
    """Estados posibles de verificación"""
    VERIFIED = "✅ VERIFIED"           # 95%+ confianza
    PARTIAL = "⚠️ PARTIALLY VERIFIED"  # 60-95% confianza
    UNVERIFIED = "❓ UNVERIFIED"       # Sin fuentes suficientes
    CONTRADICTED = "⚡ CONTRADICTED"   # Fuentes en desacuerdo
    FABRICATED = "❌ FABRICATED"       # Probado falso


class SourceType(Enum):
    """Tipos de fuentes con diferentes pesos de confianza"""
    OFFICIAL = "official"       # Gobierno, organizaciones oficiales
    ACADEMIC = "academic"       # Papers peer-reviewed
    NEWS_TIER1 = "news_tier1"   # NYT, BBC, Reuters
    NEWS_TIER2 = "news_tier2"   # Medios regionales confiables
    EXPERT = "expert"           # Expertos verificados
    COMMUNITY = "community"     # Reportes comunitarios


# Pesos de confianza por tipo de fuente (0.0 - 1.0)
SOURCE_WEIGHTS = {
    SourceType.OFFICIAL: 1.0,
    SourceType.ACADEMIC: 0.95,
    SourceType.NEWS_TIER1: 0.85,
    SourceType.NEWS_TIER2: 0.70,
    SourceType.EXPERT: 0.80,
    SourceType.COMMUNITY: 0.50,
}


@dataclass
class Source:
    """Representa una fuente de información"""
    name: str
    type: SourceType
    verdict: bool  # True = claim es verdadero, False = claim es falso
    confidence: float  # 0.0 - 1.0
    date: str  # ISO format
    url: str = ""
    snippet: str = ""
    
    @property
    def weight(self) -> float:
        """Peso efectivo de esta fuente"""
        return SOURCE_WEIGHTS[self.type] * self.confidence


@dataclass
class ConsensusResult:
    """Resultado del algoritmo de consenso"""
    status: VerificationStatus
    confidence: float  # 0.0 - 1.0
    supporting_sources: int
    contradicting_sources: int
    total_weight_supporting: float
    total_weight_contradicting: float
    explanation: str
    processing_time_ms: float


class WeightedConsensusAlgorithm:
    """
    Algoritmo de Consenso Ponderado
    
    Funciona así:
    1. Cada fuente tiene un peso basado en su tipo y confianza
    2. Sumamos pesos de fuentes que apoyan vs contradicen el claim
    3. Calculamos ratio de consenso
    4. Determinamos status basado en thresholds
    """
    
    def __init__(self):
        # Thresholds para determinar status
        self.VERIFIED_THRESHOLD = 0.95
        self.PARTIAL_THRESHOLD = 0.60
        self.CONTRADICTED_THRESHOLD = 0.40  # Si hay mucha contradicción
        
    def verify_claim(self, claim: str, sources: List[Source]) -> ConsensusResult:
        """
        Verifica un claim usando consenso ponderado
        
        Args:
            claim: El claim a verificar
            sources: Lista de fuentes que evaluaron el claim
            
        Returns:
            ConsensusResult con el veredicto y métricas
        """
        start_time = time.perf_counter()
        
        # Caso 1: Sin fuentes
        if not sources:
            return ConsensusResult(
                status=VerificationStatus.UNVERIFIED,
                confidence=0.0,
                supporting_sources=0,
                contradicting_sources=0,
                total_weight_supporting=0.0,
                total_weight_contradicting=0.0,
                explanation="No hay fuentes disponibles para verificar este claim.",
                processing_time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        # Separar fuentes que apoyan vs contradicen
        supporting = [s for s in sources if s.verdict is True]
        contradicting = [s for s in sources if s.verdict is False]
        
        # Calcular pesos totales
        weight_supporting = sum(s.weight for s in supporting)
        weight_contradicting = sum(s.weight for s in contradicting)
        total_weight = weight_supporting + weight_contradicting
        
        # Caso 2: Sin peso total (fuentes sin confianza)
        if total_weight == 0:
            return ConsensusResult(
                status=VerificationStatus.UNVERIFIED,
                confidence=0.0,
                supporting_sources=len(supporting),
                contradicting_sources=len(contradicting),
                total_weight_supporting=0.0,
                total_weight_contradicting=0.0,
                explanation="Las fuentes no tienen suficiente confianza.",
                processing_time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        # Calcular ratio de consenso (0.0 - 1.0)
        # 1.0 = todas las fuentes apoyan
        # 0.0 = todas las fuentes contradicen
        consensus_ratio = weight_supporting / total_weight
        
        # Determinar status basado en ratio
        if consensus_ratio >= self.VERIFIED_THRESHOLD:
            status = VerificationStatus.VERIFIED
            explanation = f"{len(supporting)} fuentes confiables confirman este claim."
            
        elif consensus_ratio >= self.PARTIAL_THRESHOLD:
            status = VerificationStatus.PARTIAL
            explanation = f"Verificación parcial: {len(supporting)} fuentes apoyan, {len(contradicting)} contradicen."
            
        elif consensus_ratio <= (1 - self.VERIFIED_THRESHOLD):
            status = VerificationStatus.FABRICATED
            explanation = f"{len(contradicting)} fuentes confiables desmienten este claim."
            
        elif abs(consensus_ratio - 0.5) < self.CONTRADICTED_THRESHOLD:
            status = VerificationStatus.CONTRADICTED
            explanation = f"Fuentes en desacuerdo: {len(supporting)} apoyan, {len(contradicting)} contradicen."
            
        else:
            status = VerificationStatus.PARTIAL
            explanation = f"Evidencia mixta: {len(supporting)} fuentes apoyan, {len(contradicting)} contradicen."
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return ConsensusResult(
            status=status,
            confidence=consensus_ratio,
            supporting_sources=len(supporting),
            contradicting_sources=len(contradicting),
            total_weight_supporting=weight_supporting,
            total_weight_contradicting=weight_contradicting,
            explanation=explanation,
            processing_time_ms=processing_time
        )


def print_result(claim: str, result: ConsensusResult):
    """Imprime el resultado de forma legible"""
    print("\n" + "="*70)
    print(f"CLAIM: {claim}")
    print("="*70)
    print(f"\nStatus: {result.status.value}")
    print(f"Confidence: {result.confidence*100:.1f}%")
    print(f"\nFuentes:")
    print(f"  Apoyan:      {result.supporting_sources} (peso: {result.total_weight_supporting:.2f})")
    print(f"  Contradicen: {result.contradicting_sources} (peso: {result.total_weight_contradicting:.2f})")
    print(f"\nExplicación: {result.explanation}")
    print(f"Tiempo de procesamiento: {result.processing_time_ms:.2f}ms")


if __name__ == '__main__':
    # Demo del algoritmo
    algorithm = WeightedConsensusAlgorithm()
    
    # Ejemplo 1: Claim verificado (múltiples fuentes confiables)
    claim1 = "La tasa de desempleo en EE.UU. es 3.5% según BLS"
    sources1 = [
        Source("Bureau of Labor Statistics", SourceType.OFFICIAL, True, 1.0, "2025-12-01", "https://bls.gov"),
        Source("New York Times", SourceType.NEWS_TIER1, True, 0.9, "2025-12-01", "https://nyt.com"),
        Source("Reuters", SourceType.NEWS_TIER1, True, 0.95, "2025-12-01", "https://reuters.com"),
    ]
    result1 = algorithm.verify_claim(claim1, sources1)
    print_result(claim1, result1)
    
    # Ejemplo 2: Claim fabricado (fuentes lo desmienten)
    claim2 = "La vacuna COVID causa autismo"
    sources2 = [
        Source("CDC", SourceType.OFFICIAL, False, 1.0, "2025-12-01", "https://cdc.gov"),
        Source("WHO", SourceType.OFFICIAL, False, 1.0, "2025-12-01", "https://who.int"),
        Source("Nature Medicine", SourceType.ACADEMIC, False, 0.95, "2025-12-01", "https://nature.com"),
        Source("Lancet", SourceType.ACADEMIC, False, 0.95, "2025-12-01", "https://lancet.com"),
    ]
    result2 = algorithm.verify_claim(claim2, sources2)
    print_result(claim2, result2)
    
    # Ejemplo 3: Claim contradictorio (fuentes en desacuerdo)
    claim3 = "La economía está en recesión"
    sources3 = [
        Source("Economist A", SourceType.EXPERT, True, 0.8, "2025-12-01"),
        Source("Economist B", SourceType.EXPERT, False, 0.8, "2025-12-01"),
        Source("Wall Street Journal", SourceType.NEWS_TIER1, True, 0.85, "2025-12-01"),
        Source("Financial Times", SourceType.NEWS_TIER1, False, 0.85, "2025-12-01"),
    ]
    result3 = algorithm.verify_claim(claim3, sources3)
    print_result(claim3, result3)
    
    print("\n" + "="*70)
    print("DEMO COMPLETADO")
    print("="*70)
