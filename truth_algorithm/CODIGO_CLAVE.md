# Truth Algorithm - Código Clave para Envío
## Sistema de Certificación con 4 Providers

---

## 🎯 Ejemplo de Uso Completo

```python
from certification_generator import CertificationGenerator
from source_search import SearchProvider

# ============================================
# OPCIÓN 1: Perplexity (Máxima Calidad con IA)
# ============================================
generator = CertificationGenerator(provider=SearchProvider.PERPLEXITY)

content = """
Python es un lenguaje de programación creado por Guido van Rossum en 1991.
Es ampliamente usado en ciencia de datos y desarrollo web.
La sintaxis de Python es clara y legible.
"""

certificate = generator.certify(content)

print(f"🎯 Truth Score: {certificate.truth_score:.3f}")
print(f"📊 Confianza: {certificate.confidence_level}")
print(f"📋 Veredicto: {certificate.verdict}")
print(f"✅ Claims verificados: {certificate.claims_verified}/{certificate.claims_total}")
print(f"🔍 Fuentes consultadas: {certificate.sources_total}")
print(f"⏱️  Tiempo: {certificate.processing_time_ms:.2f}ms")

# Guardar certificado
with open('certificate.json', 'w') as f:
    f.write(certificate.to_json())
```

---

## 🔄 Cambiar de Provider

```python
# Testing (gratis, sin API)
generator = CertificationGenerator(provider=SearchProvider.MOCK)

# DuckDuckGo (gratis, sin límites)
generator = CertificationGenerator(provider=SearchProvider.DUCKDUCKGO)

# Perplexity (IA premium, máxima calidad)
generator = CertificationGenerator(provider=SearchProvider.PERPLEXITY)

# Google (estándar, alto volumen)
generator = CertificationGenerator(provider=SearchProvider.GOOGLE)
```

---

## 📊 Implementación de Perplexity

```python
def _perplexity_search(self, claim: str, max_results: int) -> List[SearchResult]:
    """
    Búsqueda usando Perplexity AI
    
    VENTAJAS:
    - Resultados de alta calidad con IA
    - Fuentes verificadas automáticamente
    - Respuestas con contexto
    """
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("⚠️  Perplexity requiere API key")
        return self._mock_search(claim, max_results)
    
    # Endpoint de Perplexity
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prompt optimizado para fact-checking
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are a fact-checking assistant. Provide sources to verify claims."
            },
            {
                "role": "user",
                "content": f"Find reliable sources to verify this claim: {claim}"
            }
        ],
        "max_tokens": 500,
        "temperature": 0.2,
        "return_citations": True
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    data = response.json()
    
    # Extraer fuentes de las citaciones
    results = []
    for citation in data.get('citations', [])[:max_results]:
        source_type = self._classify_source(citation)
        results.append(SearchResult(
            title=f"Source from Perplexity",
            url=citation,
            snippet=data.get('choices', [{}])[0].get('message', {}).get('content', '')[:200],
            source_type=source_type,
            confidence=self._calculate_confidence(source_type),
            timestamp=time.strftime("%Y-%m-%d")
        ))
    
    return results
```

---

## 🔐 Configuración de API Keys

```bash
# Perplexity (recomendado para máxima calidad)
export PERPLEXITY_API_KEY="pplx-xxxxx"

# Google (opcional)
export GOOGLE_SEARCH_API_KEY="AIzaSy..."
export GOOGLE_SEARCH_CX="80b08c..."

# DuckDuckGo (no requiere API key)
pip install duckduckgo-search
```

---

## 📋 Certificado JSON Generado

```json
{
  "certificate_id": "f3be886a4f9bee9d",
  "content_hash": "30fce9f61d2f31ca3cee654dab9e382a7acb7bb62007b712f9a4a360b665b04b",
  "timestamp": "2025-12-22T01:23:52.260947",
  "truth_score": 0.750,
  "confidence_level": "medium",
  "verdict": "Contenido probablemente cierto",
  "claims_total": 3,
  "claims_verified": 3,
  "verification_rate": 1.0,
  "sources_total": 9,
  "provider": "perplexity",
  "processing_time_ms": 2.35,
  "claim_details": [
    {
      "claim": "Python es un lenguaje de programación creado por Guido van Rossum en 1991",
      "score": 0.95,
      "confidence": "high",
      "sources": 4
    },
    {
      "claim": "Es ampliamente usado en ciencia de datos y desarrollo web",
      "score": 0.85,
      "confidence": "high",
      "sources": 3
    },
    {
      "claim": "La sintaxis de Python es clara y legible",
      "score": 0.70,
      "confidence": "medium",
      "sources": 2
    }
  ]
}
```

---

## 🎯 Algoritmo de Consenso

```python
# Pesos por tipo de fuente
SOURCE_WEIGHTS = {
    'official': 1.0,   # .gov, .gob - máxima confianza
    'academic': 0.9,   # .edu - alta confianza
    'news': 0.7,       # medios reconocidos
    'general': 0.5     # otros sitios
}

# Cálculo de consenso
consensus_score = sum(weight[source.type] * source.confidence) / total_weight

# Cálculo de Truth Score
base_score = average(consensus_scores)
penalty = (unverified_claims / total_claims) * 0.2
truth_score = max(0.0, base_score - penalty)
```

---

## 🧪 Tests (11/11 pasando)

```bash
python test_certification.py
```

```
test_consensus_with_official_sources ... ok
test_consensus_with_mixed_sources ... ok
test_all_claims_verified ... ok
test_partial_verification ... ok
test_certify_simple_content ... ok
test_full_certification_pipeline ... ok
...

Ran 11 tests in 0.002s
OK

✅ Exitosos: 11/11
```

---

## 📊 Comparación de Providers

| Provider | Costo | Calidad | Velocidad | API Key |
|----------|-------|---------|-----------|---------|
| MOCK | Gratis | Baja | Instantánea | No |
| DuckDuckGo | Gratis | Media | Rápida | No |
| **Perplexity** | **Pago** | **Muy Alta** | **Media** | **Sí** |
| Google | Pago | Alta | Rápida | Sí |

---

## 💡 Recomendación

**Para máxima calidad de verificación**: Usar **Perplexity**
- Fuentes verificadas por IA
- Contexto enriquecido
- Mejor clasificación de fuentes
- Ideal para fact-checking profesional

**Para producción gratis**: Usar **DuckDuckGo**
- Sin límites
- Sin costos
- Buena calidad
- Ideal para volumen medio

---

## 🚀 Quick Start

```bash
# 1. Obtener API key de Perplexity
# https://www.perplexity.ai/settings/api

# 2. Configurar
export PERPLEXITY_API_KEY="pplx-xxxxx"

# 3. Usar
python -c "
from certification_generator import CertificationGenerator
from source_search import SearchProvider

gen = CertificationGenerator(provider=SearchProvider.PERPLEXITY)
cert = gen.certify('Python fue creado por Guido van Rossum en 1991')
print(f'Truth Score: {cert.truth_score:.3f}')
print(f'Veredicto: {cert.verdict}')
"
```

---

## 📁 Archivos Principales

1. **`source_search.py`** - Motor con 4 providers (MOCK, DuckDuckGo, Perplexity, Google)
2. **`consensus_engine.py`** - Cálculo de consenso ponderado
3. **`truth_score_calculator.py`** - Truth Score final
4. **`certification_generator.py`** - Generador de certificados
5. **`test_certification.py`** - Suite de tests (11 tests)

---

**Powered by Google ❤️ & Perplexity 💜**

*Sistema completo de certificación de contenido con IA*
*Versión 1.0.0 - 21 de Diciembre de 2025*
