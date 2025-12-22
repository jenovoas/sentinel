#!/usr/bin/env python3
"""
Truth Algorithm - Certification Generator
==========================================

Genera certificados de veracidad para contenido verificado.

Powered by Google ❤️ & Perplexity 💜
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

from consensus_engine import ConsensusResult
from truth_score_calculator import TruthScore
from source_search import SearchProvider


@dataclass
class VerificationCertificate:
    """Certificado de verificación de contenido"""
    # Identificación
    content_hash: str
    certificate_id: str
    timestamp: str
    
    # Truth Score
    truth_score: float
    confidence_level: str
    verdict: str
    
    # Estadísticas
    claims_total: int
    claims_verified: int
    verification_rate: float
    sources_total: int
    
    # Metadata
    provider: str  # google, duckduckgo, mock
    processing_time_ms: float
    
    # Detalles
    claim_details: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convierte a JSON"""
        return json.dumps(self.to_dict(), indent=indent)


class CertificationGenerator:
    """
    Genera certificados de veracidad para contenido.
    
    Integra todos los componentes del Truth Algorithm:
    1. ClaimExtractor - Extrae claims
    2. SourceSearch - Busca fuentes
    3. ConsensusEngine - Calcula consenso
    4. TruthScoreCalculator - Calcula score final
    5. CertificationGenerator - Genera certificado
    """
    
    def __init__(self, provider: SearchProvider = SearchProvider.MOCK):
        from source_search import SourceSearchEngine
        from consensus_engine import ConsensusEngine
        from truth_score_calculator import TruthScoreCalculator
        
        self.search_engine = SourceSearchEngine(provider=provider)
        self.consensus_engine = ConsensusEngine()
        self.score_calculator = TruthScoreCalculator()
        self.provider = provider.value
    
    def certify(self, content: str, claims: List[str] = None) -> VerificationCertificate:
        """
        Certifica contenido completo
        
        Args:
            content: Texto a certificar
            claims: Lista de claims (opcional, se extraen automáticamente si no se proveen)
            
        Returns:
            VerificationCertificate
        """
        start_time = datetime.now()
        
        # 1. Usar claims provistos o extraer del contenido
        if claims is None:
            # TODO: Integrar con ClaimExtractor cuando esté disponible
            # Por ahora, dividir en oraciones simples
            claims = self._simple_claim_extraction(content)
        
        # 2. Verificar cada claim con fuentes
        consensus_results = []
        total_sources = 0
        
        for claim in claims:
            # Buscar fuentes
            sources = self.search_engine.search(claim, max_results=5)
            total_sources += len(sources)
            
            # Calcular consenso
            consensus = self.consensus_engine.calculate_consensus(claim, sources)
            consensus_results.append(consensus)
        
        # 3. Calcular Truth Score final
        truth_score = self.score_calculator.calculate(consensus_results)
        
        # 4. Generar certificado
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        certificate_id = hashlib.sha256(
            f"{content_hash}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Determinar veredicto
        verdict = self._determine_verdict(truth_score.overall_score)
        
        # Tiempo de procesamiento
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        certificate = VerificationCertificate(
            content_hash=content_hash,
            certificate_id=certificate_id,
            timestamp=datetime.utcnow().isoformat(),
            truth_score=truth_score.overall_score,
            confidence_level=truth_score.confidence_level,
            verdict=verdict,
            claims_total=truth_score.claims_total,
            claims_verified=truth_score.claims_verified,
            verification_rate=truth_score.verification_rate,
            sources_total=total_sources,
            provider=self.provider,
            processing_time_ms=processing_time,
            claim_details=truth_score.details
        )
        
        return certificate
    
    def _simple_claim_extraction(self, content: str) -> List[str]:
        """Extracción simple de claims (fallback)"""
        import re
        # Dividir en oraciones
        sentences = re.split(r'[.!?]\s+', content)
        # Filtrar oraciones muy cortas
        claims = [s.strip() for s in sentences if len(s.split()) >= 5]
        return claims
    
    def _determine_verdict(self, score: float) -> str:
        """Determina veredicto basado en score"""
        if score >= 0.8:
            return "Contenido altamente verificado"
        elif score >= 0.6:
            return "Contenido probablemente cierto"
        elif score >= 0.4:
            return "Contenido parcialmente verificado"
        else:
            return "Contenido no verificable"


def demo_certification():
    """Demo del generador de certificados"""
    print("="*70)
    print("DEMO - CERTIFICATION GENERATOR")
    print("="*70)
    print()
    
    # Contenido de ejemplo
    content = """
    Python es un lenguaje de programación creado por Guido van Rossum en 1991.
    Es ampliamente usado en ciencia de datos y desarrollo web.
    La sintaxis de Python es clara y legible.
    """
    
    print("📄 Contenido a certificar:")
    print(content)
    print()
    
    # Generar certificado
    print("🔍 Certificando contenido...")
    print()
    
    generator = CertificationGenerator(provider=SearchProvider.MOCK)
    certificate = generator.certify(content)
    
    # Mostrar certificado
    print("="*70)
    print("📜 CERTIFICADO DE VERACIDAD")
    print("="*70)
    print()
    print(f"🆔 ID: {certificate.certificate_id}")
    print(f"📅 Timestamp: {certificate.timestamp}")
    print(f"🔐 Content Hash: {certificate.content_hash[:16]}...")
    print()
    print(f"🎯 TRUTH SCORE: {certificate.truth_score:.3f}")
    print(f"📊 Confianza: {certificate.confidence_level}")
    print(f"📋 Veredicto: {certificate.verdict}")
    print()
    print(f"📈 Estadísticas:")
    print(f"   Claims verificados: {certificate.claims_verified}/{certificate.claims_total}")
    print(f"   Tasa de verificación: {certificate.verification_rate*100:.1f}%")
    print(f"   Fuentes consultadas: {certificate.sources_total}")
    print(f"   Tiempo de procesamiento: {certificate.processing_time_ms:.2f}ms")
    print(f"   Provider: {certificate.provider}")
    print()
    
    print("📝 Detalles por claim:")
    for i, detail in enumerate(certificate.claim_details, 1):
        print(f"   {i}. {detail['claim'][:60]}...")
        print(f"      Score: {detail['score']:.2f} | Fuentes: {detail['sources']}")
    
    print()
    print("="*70)
    print("✅ Certificación completada")
    print("="*70)
    
    # Guardar certificado
    with open('certificate_demo.json', 'w') as f:
        f.write(certificate.to_json())
    print()
    print("💾 Certificado guardado en: certificate_demo.json")


if __name__ == '__main__':
    demo_certification()
