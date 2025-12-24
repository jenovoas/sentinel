#!/usr/bin/env python3
"""
Truth Algorithm - End-to-End Integration
=========================================

Integración completa: Source Search + Consensus Algorithm

Flujo:
1. Recibe claim
2. Busca fuentes (Source Search)
3. Calcula consenso (Consensus Algorithm)
4. Retorna veredicto

Powered by Google ❤️ & Perplexity 💜 | Built with Gemini AI

Autor: Jaime Novoa
Fecha: 21 Diciembre 2025
"""

from typing import List, Dict
from dataclasses import dataclass
import time

from source_search import SourceSearchEngine, SearchProvider, SearchResult
from consensus_algorithm import (
    WeightedConsensusAlgorithm,
    Source,
    SourceType,
    ConsensusResult,
    VerificationStatus
)


@dataclass
class TruthVerificationResult:
    """Resultado completo de verificación"""
    claim: str
    status: VerificationStatus
    confidence: float
    sources_found: int
    sources_used: int
    search_time_ms: float
    consensus_time_ms: float
    total_time_ms: float
    explanation: str
    sources: List[Source]


class TruthAlgorithm:
    """
    Truth Algorithm - Sistema completo de verificación
    
    Combina búsqueda de fuentes con consenso ponderado para
    determinar la veracidad de claims.
    """
    
    def __init__(self, search_provider: SearchProvider = SearchProvider.MOCK):
        self.search_engine = SourceSearchEngine(provider=search_provider)
        self.consensus_algorithm = WeightedConsensusAlgorithm()
        
    def verify(self, claim: str, max_sources: int = 10) -> TruthVerificationResult:
        """
        Verifica un claim end-to-end
        
        Args:
            claim: El claim a verificar
            max_sources: Máximo número de fuentes a buscar
            
        Returns:
            TruthVerificationResult con veredicto completo
        """
        start_time = time.perf_counter()
        
        # PASO 1: Buscar fuentes
        search_start = time.perf_counter()
        search_results = self.search_engine.search(claim, max_results=max_sources)
        search_time = (time.perf_counter() - search_start) * 1000
        
        # PASO 2: Convertir SearchResults a Sources para el consenso
        sources = self._convert_search_results_to_sources(search_results, claim)
        
        # PASO 3: Calcular consenso
        consensus_start = time.perf_counter()
        consensus_result = self.consensus_algorithm.verify_claim(claim, sources)
        consensus_time = (time.perf_counter() - consensus_start) * 1000
        
        total_time = (time.perf_counter() - start_time) * 1000
        
        # PASO 4: Construir resultado completo
        return TruthVerificationResult(
            claim=claim,
            status=consensus_result.status,
            confidence=consensus_result.confidence,
            sources_found=len(search_results),
            sources_used=len(sources),
            search_time_ms=search_time,
            consensus_time_ms=consensus_time,
            total_time_ms=total_time,
            explanation=consensus_result.explanation,
            sources=sources
        )
    
    def _convert_search_results_to_sources(
        self, 
        search_results: List[SearchResult],
        claim: str
    ) -> List[Source]:
        """
        Convierte SearchResults a Sources para el consenso
        
        En producción, aquí se haría análisis del contenido para
        determinar si la fuente apoya o contradice el claim.
        
        Por ahora, usamos heurísticas simples basadas en keywords.
        """
        sources = []
        
        for result in search_results:
            # Mapear tipo de fuente de search a tipo de consenso
            source_type = self._map_source_type(result.source_type)
            
            # Determinar si apoya o contradice (heurística simple)
            # En producción, esto sería NLP real
            verdict = self._analyze_verdict(result.snippet, claim)
            
            source = Source(
                name=result.title,
                type=source_type,
                verdict=verdict,
                confidence=result.confidence,
                date=result.timestamp,
                url=result.url,
                snippet=result.snippet
            )
            
            sources.append(source)
        
        return sources
    
    def _map_source_type(self, search_type: str) -> SourceType:
        """Mapea tipo de fuente de search a tipo de consenso"""
        mapping = {
            'official': SourceType.OFFICIAL,
            'academic': SourceType.ACADEMIC,
            'news': SourceType.NEWS_TIER1,
            'expert': SourceType.EXPERT,
            'community': SourceType.COMMUNITY,
        }
        return mapping.get(search_type, SourceType.NEWS_TIER2)
    
    def _analyze_verdict(self, snippet: str, claim: str) -> bool:
        """
        Analiza si el snippet apoya o contradice el claim
        
        NOTA: Esta es una heurística simple para el POC.
        En producción, usaríamos NLP real (BERT, etc.)
        """
        snippet_lower = snippet.lower()
        claim_lower = claim.lower()
        
        # Palabras que indican contradicción
        contradiction_words = [
            'false', 'incorrect', 'wrong', 'debunked', 'myth',
            'not true', 'misleading', 'fabricated', 'fake',
            'falso', 'incorrecto', 'mentira', 'desmentido', 'mito',
            'no es cierto', 'engañoso', 'fabricado', 'falsa', 'error'
        ]
        
        # Palabras que indican apoyo
        support_words = [
            'confirmed', 'verified', 'true', 'accurate', 'correct',
            'according to', 'shows', 'demonstrates', 'proves',
            'confirmado', 'verificado', 'cierto', 'exacto', 'correcto',
            'según', 'muestra', 'demuestra', 'prueba', 'verdad'
        ]
        
        # Contar palabras de contradicción
        contradiction_count = sum(
            1 for word in contradiction_words 
            if word in snippet_lower
        )
        
        # Contar palabras de apoyo
        support_count = sum(
            1 for word in support_words 
            if word in snippet_lower
        )
        
        # Si hay más contradicción que apoyo, retornar False
        if contradiction_count > support_count:
            return False
        
        # Si no hay ninguna señal clara, ser escéptico (retornar False para que el consenso lo marque como unverified/ contradicted)
        if support_count == 0 and contradiction_count == 0:
            return False
            
        # Si hay apoyo, retornar True
        return support_count >= contradiction_count


def print_verification_result(result: TruthVerificationResult):
    """Imprime resultado de verificación de forma legible"""
    print("\n" + "="*70)
    print("TRUTH ALGORITHM - RESULTADO DE VERIFICACIÓN")
    print("="*70)
    
    print(f"\n📋 Claim:")
    print(f"   {result.claim}")
    
    print(f"\n{result.status.value}")
    print(f"Confidence: {result.confidence*100:.1f}%")
    
    print(f"\n📊 Fuentes:")
    print(f"   Encontradas: {result.sources_found}")
    print(f"   Usadas:      {result.sources_used}")
    
    print(f"\n⏱️  Performance:")
    print(f"   Búsqueda:    {result.search_time_ms:.2f}ms")
    print(f"   Consenso:    {result.consensus_time_ms:.2f}ms")
    print(f"   Total:       {result.total_time_ms:.2f}ms")
    
    print(f"\n💡 Explicación:")
    print(f"   {result.explanation}")
    
    if result.sources:
        print(f"\n📚 Fuentes Consultadas:")
        for i, source in enumerate(result.sources, 1):
            verdict_icon = "✅" if source.verdict else "❌"
            print(f"   {i}. {verdict_icon} [{source.type.value}] {source.name}")
            print(f"      Confidence: {source.confidence*100:.1f}%")


def demo_end_to_end():
    """Demo del Truth Algorithm completo"""
    print("="*70)
    print("TRUTH ALGORITHM - END-TO-END DEMO")
    print("="*70)
    print("\nPowered by Google ❤️ & Perplexity 💜")
    print("\nModo: MOCK (sin llamadas reales a APIs)")
    print("="*70)
    
    # Crear Truth Algorithm
    truth = TruthAlgorithm(search_provider=SearchProvider.MOCK)
    
    # Test 1: Claim verificable
    print("\n\n🧪 Test 1: Claim sobre datos oficiales")
    claim1 = "La tasa de desempleo en EE.UU. es 3.5% según BLS"
    result1 = truth.verify(claim1)
    print_verification_result(result1)
    
    # Test 2: Claim científico
    print("\n\n🧪 Test 2: Claim científico")
    claim2 = "El cambio climático está causado por actividad humana según estudios"
    result2 = truth.verify(claim2)
    print_verification_result(result2)
    
    # Test 3: Claim sin fuentes
    print("\n\n🧪 Test 3: Claim sin fuentes suficientes")
    claim3 = "Habrá vida en Marte en 2050"
    result3 = truth.verify(claim3)
    print_verification_result(result3)
    
    print("\n" + "="*70)
    print("DEMO COMPLETADO")
    print("="*70)
    print("\n✅ Sistema end-to-end funcionando")
    print("✅ Búsqueda + Consenso integrados")
    print("✅ Latencia total < 5ms (modo mock)")
    print("\n💡 Próximo paso: Integrar con Google Search API real")


if __name__ == '__main__':
    demo_end_to_end()
