#!/usr/bin/env python3
"""
Truth Algorithm - Source Search Engine
=======================================

Búsqueda segura de fuentes para verificación de claims.

SEGURIDAD:
- Rate limiting estricto
- Validación de inputs
- No ejecución de código externo
- Logging de todas las búsquedas
- API keys en variables de entorno (NUNCA hardcoded)

Powered by Google ❤️ | Built with Gemini AI

Autor: Jaime Novoa
Fecha: 21 Diciembre 2025
"""

import os
import time
import hashlib
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import re


class SearchProvider(Enum):
    """Proveedores de búsqueda soportados"""
    GOOGLE = "google"
    DUCKDUCKGO = "duckduckgo"  # Alternativa sin API key
    MOCK = "mock"  # Para testing sin llamadas reales


@dataclass
class SearchResult:
    """Resultado de búsqueda"""
    title: str
    url: str
    snippet: str
    source_type: str  # "official", "academic", "news", etc.
    confidence: float  # 0.0 - 1.0
    timestamp: str


class SecurityValidator:
    """Validador de seguridad para inputs"""
    
    @staticmethod
    def validate_claim(claim: str) -> bool:
        """
        Valida que el claim sea seguro para buscar
        
        Bloquea:
        - Comandos de shell
        - SQL injection
        - Path traversal
        - Scripts maliciosos
        """
        # Longitud razonable
        if len(claim) > 500:
            raise ValueError("Claim demasiado largo (max 500 caracteres)")
        
        # Patrones peligrosos
        dangerous_patterns = [
            r'[;&|`$]',  # Shell commands
            r'\.\./',     # Path traversal
            r'<script',   # XSS
            r"['\"].*OR.*['\"]",  # SQL injection con OR
            r'DROP\s+TABLE',  # SQL injection
            r'rm\s+-rf',  # Comandos destructivos
            r'eval\(',    # Code execution
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, claim, re.IGNORECASE):
                raise ValueError(f"Claim contiene patrón peligroso: {pattern}")
        
        return True
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Valida que la URL sea segura"""
        # Solo HTTPS
        if not url.startswith('https://'):
            return False
        
        # Bloquear IPs privadas
        private_ips = [
            r'127\.0\.0\.1',
            r'localhost',
            r'192\.168\.',
            r'10\.',
            r'172\.(1[6-9]|2[0-9]|3[0-1])\.',
        ]
        
        for pattern in private_ips:
            if re.search(pattern, url):
                return False
        
        return True


class RateLimiter:
    """Rate limiter para prevenir abuso"""
    
    def __init__(self, max_requests_per_minute: int = 10):
        self.max_requests = max_requests_per_minute
        self.requests = []
    
    def check_rate_limit(self) -> bool:
        """Verifica si se puede hacer otra request"""
        now = time.time()
        
        # Limpiar requests antiguas (> 1 minuto)
        self.requests = [r for r in self.requests if now - r < 60]
        
        if len(self.requests) >= self.max_requests:
            raise Exception(f"Rate limit excedido: {self.max_requests} requests/minuto")
        
        self.requests.append(now)
        return True


class SourceSearchEngine:
    """
    Motor de búsqueda seguro para Truth Algorithm
    
    IMPORTANTE:
    - NO hace llamadas a APIs externas sin API key válida
    - Valida todos los inputs
    - Rate limiting estricto
    - Logging de todas las operaciones
    """
    
    def __init__(self, provider: SearchProvider = SearchProvider.MOCK):
        self.provider = provider
        self.validator = SecurityValidator()
        self.rate_limiter = RateLimiter(max_requests_per_minute=10)
        self.search_log = []
        
        # API keys desde environment (NUNCA hardcoded)
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_cx = os.getenv('GOOGLE_SEARCH_CX')
        
    def search(self, claim: str, max_results: int = 10) -> List[SearchResult]:
        """
        Busca fuentes para verificar un claim
        
        Args:
            claim: El claim a verificar
            max_results: Máximo número de resultados
            
        Returns:
            Lista de SearchResult
            
        Raises:
            ValueError: Si el claim no pasa validación de seguridad
            Exception: Si se excede rate limit
        """
        # SEGURIDAD: Validar input
        self.validator.validate_claim(claim)
        
        # SEGURIDAD: Rate limiting
        self.rate_limiter.check_rate_limit()
        
        # Log de búsqueda
        search_id = hashlib.sha256(
            f"{claim}{time.time()}".encode()
        ).hexdigest()[:16]
        
        log_entry = {
            'search_id': search_id,
            'claim': claim,
            'timestamp': time.time(),
            'provider': self.provider.value
        }
        self.search_log.append(log_entry)
        
        # Ejecutar búsqueda según provider
        if self.provider == SearchProvider.MOCK:
            return self._mock_search(claim, max_results)
        elif self.provider == SearchProvider.GOOGLE:
            return self._google_search(claim, max_results)
        elif self.provider == SearchProvider.DUCKDUCKGO:
            return self._duckduckgo_search(claim, max_results)
        else:
            raise ValueError(f"Provider no soportado: {self.provider}")
    
    def _mock_search(self, claim: str, max_results: int) -> List[SearchResult]:
        """
        Búsqueda mock para testing (NO hace llamadas reales)
        """
        # Simular resultados basados en keywords
        mock_results = []
        
        keywords = claim.lower().split()
        
        # Simular fuentes oficiales
        if any(k in keywords for k in ['gobierno', 'oficial', 'census', 'bls']):
            mock_results.append(SearchResult(
                title=f"Official data about {claim[:30]}",
                url="https://example.gov/data",
                snippet=f"Official statistics confirm {claim[:50]}...",
                source_type="official",
                confidence=0.95,
                timestamp=time.strftime("%Y-%m-%d")
            ))
        
        # Simular fuentes académicas
        if any(k in keywords for k in ['study', 'research', 'science']):
            mock_results.append(SearchResult(
                title=f"Research paper on {claim[:30]}",
                url="https://example.edu/paper",
                snippet=f"Peer-reviewed study shows {claim[:50]}...",
                source_type="academic",
                confidence=0.90,
                timestamp=time.strftime("%Y-%m-%d")
            ))
        
        # Simular fuentes de noticias
        mock_results.append(SearchResult(
            title=f"News coverage: {claim[:30]}",
            url="https://example.com/news",
            snippet=f"According to reports, {claim[:50]}...",
            source_type="news",
            confidence=0.75,
            timestamp=time.strftime("%Y-%m-%d")
        ))
        
        return mock_results[:max_results]
    
    def _google_search(self, claim: str, max_results: int) -> List[SearchResult]:
        """
        Búsqueda real usando Google Custom Search API
        
        REQUIERE:
        - GOOGLE_SEARCH_API_KEY en environment
        - GOOGLE_SEARCH_CX en environment
        """
        if not self.google_api_key or not self.google_cx:
            raise ValueError(
                "Google Search requiere API key y CX en environment.\n"
                "Set: GOOGLE_SEARCH_API_KEY y GOOGLE_SEARCH_CX"
            )
        
        # TODO: Implementar llamada real a Google API
        # Por ahora, retornar mock
        print("⚠️  Google Search API no implementado aún. Usando mock.")
        return self._mock_search(claim, max_results)
    
    def _duckduckgo_search(self, claim: str, max_results: int) -> List[SearchResult]:
        """
        Búsqueda usando DuckDuckGo (no requiere API key)
        """
        # TODO: Implementar con duckduckgo_search library
        print("⚠️  DuckDuckGo search no implementado aún. Usando mock.")
        return self._mock_search(claim, max_results)
    
    def get_search_log(self) -> List[Dict]:
        """Retorna log de búsquedas (para auditoría)"""
        return self.search_log
    
    def save_log(self, filepath: str = "search_log.json"):
        """Guarda log de búsquedas"""
        with open(filepath, 'w') as f:
            json.dump(self.search_log, f, indent=2)
        print(f"✅ Log guardado en: {filepath}")


def demo_secure_search():
    """Demo del motor de búsqueda seguro"""
    print("="*70)
    print("DEMO - SOURCE SEARCH ENGINE (MODO SEGURO)")
    print("="*70)
    
    # Crear engine en modo MOCK (sin llamadas reales)
    engine = SourceSearchEngine(provider=SearchProvider.MOCK)
    
    # Test 1: Búsqueda normal
    print("\n📊 Test 1: Búsqueda normal")
    claim1 = "La tasa de desempleo en EE.UU. es 3.5%"
    results1 = engine.search(claim1)
    print(f"Claim: {claim1}")
    print(f"Resultados: {len(results1)}")
    for i, r in enumerate(results1, 1):
        print(f"  {i}. [{r.source_type}] {r.title}")
        print(f"     Confidence: {r.confidence*100:.1f}%")
    
    # Test 2: Validación de seguridad
    print("\n🛡️  Test 2: Validación de seguridad")
    dangerous_claims = [
        "Test; rm -rf /",
        "Test' OR '1'='1",
        "Test<script>alert('xss')</script>",
    ]
    
    for claim in dangerous_claims:
        try:
            engine.search(claim)
            print(f"❌ FALLO: Claim peligroso no bloqueado: {claim}")
        except ValueError as e:
            print(f"✅ BLOQUEADO: {claim[:30]}...")
    
    # Test 3: Rate limiting
    print("\n⏱️  Test 3: Rate limiting")
    try:
        for i in range(12):  # Exceder límite de 10/min
            engine.search(f"Test claim {i}")
        print("❌ FALLO: Rate limit no funcionó")
    except Exception as e:
        print(f"✅ Rate limit funcionando: {str(e)}")
    
    # Guardar log
    print("\n💾 Guardando log de búsquedas...")
    engine.save_log()
    
    print("\n" + "="*70)
    print("DEMO COMPLETADO - SISTEMA SEGURO ✅")
    print("="*70)


if __name__ == '__main__':
    demo_secure_search()
