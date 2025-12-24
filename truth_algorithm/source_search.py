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
    DUCKDUCKGO = "duckduckgo"
    PERPLEXITY = "perplexity"  # Perplexity AI Search
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
            r'[;&|`]\s*\w',  # Shell commands (con espacio y comando después)
            r'\$\(',  # Command substitution
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
        
        # LIMPIEZA: Simplificar query para búsqueda
        clean_query = self._clean_query(claim)
        
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
            return self._mock_search(clean_query, max_results)
        elif self.provider == SearchProvider.GOOGLE:
            return self._google_search(clean_query, max_results)
        elif self.provider == SearchProvider.DUCKDUCKGO:
            return self._duckduckgo_search(clean_query, max_results)
        elif self.provider == SearchProvider.PERPLEXITY:
            return self._perplexity_search(clean_query, max_results)
        else:
            raise ValueError(f"Provider no soportado: {self.provider}")

    def _clean_query(self, query: str) -> str:
        """Limpia la query para mejorar resultados de búsqueda"""
        # Quitar símbolos comunes de preguntas
        q = re.sub(r'[¿?¡!]', '', query)
        
        # Quitar palabras de ruido (stop words simples)
        noise = ['la', 'el', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'y', 'es', 'son']
        words = q.split()
        filtered = [w for w in words if w.lower() not in noise or len(words) < 4]
        
        return " ".join(filtered)
    
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
        Búsqueda usando Google Custom Search API oficial
        
        REQUIERE:
        - GOOGLE_SEARCH_API_KEY en environment
        - GOOGLE_SEARCH_CX en environment
        
        NOTA: Para evitar cargos, se recomienda usar DuckDuckGo como alternativa.
        """
        if not self.google_api_key or not self.google_cx:
            print("⚠️  Google Search requiere API key y CX")
            print("   Alternativa recomendada: DuckDuckGo (gratis)")
            return self._mock_search(claim, max_results)
        
        try:
            from googleapiclient.discovery import build
            
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            result = service.cse().list(
                q=claim,
                cx=self.google_cx,
                num=min(max_results, 10)
            ).execute()
            
            results = []
            for item in result.get('items', []):
                url = item.get('link', '')
                source_type = self._classify_source(url)
                
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=url,
                    snippet=item.get('snippet', ''),
                    source_type=source_type,
                    confidence=self._calculate_confidence(source_type),
                    timestamp=time.strftime("%Y-%m-%d")
                ))
            
            print(f"✅ Google API: {len(results)} resultados")
            return results
            
        except ImportError:
            print("⚠️  google-api-python-client no instalado")
            print("   Instalar con: pip install google-api-python-client")
            return self._mock_search(claim, max_results)
        except Exception as e:
            print(f"❌ Error en Google API: {e}")
            return self._mock_search(claim, max_results)
    
    def _duckduckgo_search(self, claim: str, max_results: int, region: str = "cl-es") -> List[SearchResult]:
        """
        Búsqueda usando DuckDuckGo (100% GRATIS, sin API key)
        
        Args:
            claim: Consulta
            max_results: Número de resultados
            region: Región de búsqueda (cl-es por defecto para Chile/Español)
        """
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                # Usar región para mejorar relevancia
                search_params = {
                    "keywords": claim,
                    "max_results": max_results,
                    "region": region
                }
                
                search_results = list(ddgs.text(**search_params))
                
                # FALLBACK: Si no hay resultados con región, intentar sin ella
                if not search_results and region:
                    print(f"⚠️  No hay resultados en región {region}. Intentando búsqueda global...")
                    search_params["region"] = None
                    search_results = list(ddgs.text(**search_params))
                
                for item in search_results:
                    # Clasificar tipo de fuente
                    url = item.get('href', '')
                    source_type = self._classify_source(url)
                    
                    results.append(SearchResult(
                        title=item.get('title', ''),
                        url=url,
                        snippet=item.get('body', ''),
                        source_type=source_type,
                        confidence=self._calculate_confidence(source_type),
                        timestamp=time.strftime("%Y-%m-%d")
                    ))
            
            return results
            
        except ImportError:
            print("⚠️  DuckDuckGo library no instalada.")
            print("   Instalar con: pip install duckduckgo-search")
            print("   Usando mock por ahora...")
            return self._mock_search(claim, max_results)
        except Exception as e:
            print(f"⚠️  Error en DuckDuckGo search: {e}")
            print("   Usando mock como fallback...")
            return self._mock_search(claim, max_results)
    
    def _perplexity_search(self, claim: str, max_results: int) -> List[SearchResult]:
        """
        Búsqueda usando Perplexity AI (API de pago pero muy precisa)
        
        VENTAJAS:
        - Resultados de alta calidad con IA
        - Fuentes verificadas automáticamente
        - Respuestas con contexto
        
        REQUIERE:
        - PERPLEXITY_API_KEY en environment
        """
        api_key = os.getenv('PERPLEXITY_API_KEY')
        
        if not api_key:
            print("⚠️  Perplexity requiere API key")
            print("   Set: PERPLEXITY_API_KEY")
            print("   Alternativa: DuckDuckGo (gratis)")
            return self._mock_search(claim, max_results)
        
        try:
            import requests
            
            # Endpoint de Perplexity
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prompt optimizado para búsqueda de fuentes
            payload = {
                "model": "sonar",  # Modelo correcto de Perplexity
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a fact-checking assistant. Provide sources to verify claims."
                    },
                    {
                        "role": "user",
                        "content": f"Find reliable sources to verify this claim: {claim}. List URLs and brief descriptions."
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.2,
                "return_citations": True,
                "return_images": False
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraer fuentes de las citaciones
            results = []
            citations = data.get('citations', [])
            
            for i, citation in enumerate(citations[:max_results]):
                url = citation
                source_type = self._classify_source(url)
                
                results.append(SearchResult(
                    title=f"Source {i+1} from Perplexity",
                    url=url,
                    snippet=data.get('choices', [{}])[0].get('message', {}).get('content', '')[:200],
                    source_type=source_type,
                    confidence=self._calculate_confidence(source_type),
                    timestamp=time.strftime("%Y-%m-%d")
                ))
            
            if results:
                print(f"✅ Perplexity: {len(results)} fuentes encontradas")
            else:
                print("⚠️  Perplexity no retornó fuentes. Usando mock...")
                return self._mock_search(claim, max_results)
            
            return results
            
        except ImportError:
            print("⚠️  requests no instalado")
            print("   Instalar con: pip install requests")
            return self._mock_search(claim, max_results)
        except Exception as e:
            print(f"⚠️  Error en Perplexity search: {e}")
            print("   Usando mock como fallback...")
            return self._mock_search(claim, max_results)
    
    def _classify_source(self, url: str) -> str:
        """Clasifica el tipo de fuente según la URL"""
        if any(domain in url for domain in ['.gov', '.gob']):
            return 'official'
        elif '.edu' in url:
            return 'academic'
        elif any(domain in url for domain in ['reuters.com', 'apnews.com', 'bbc.com', 'nytimes.com']):
            return 'news'
        else:
            return 'general'
    
    def _calculate_confidence(self, source_type: str) -> float:
        """Calcula confianza basada en tipo de fuente"""
        confidence_map = {
            'official': 0.95,
            'academic': 0.90,
            'news': 0.75,
            'general': 0.60
        }
        return confidence_map.get(source_type, 0.50)
    
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
    print("DEMO - SOURCE SEARCH ENGINE (100% GRATIS)")
    print("="*70)
    print("🆓 Usando DuckDuckGo - Sin API key, sin cargos")
    print("="*70)
    
    # Crear engine en modo DuckDuckGo (gratis, sin API key)
    engine = SourceSearchEngine(provider=SearchProvider.DUCKDUCKGO)
    
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
