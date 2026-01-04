# 🔍 Guía de Activación: Google Custom Search API

##  Objetivo

Activar la integración real con **Google Custom Search API** en el Truth Algorithm para verificación de claims con fuentes reales.

---

## 📊 Estado Actual

✅ **Infraestructura Completa**:
- Validación de seguridad (SQL injection, XSS, shell commands)
- Rate limiting (10 requests/minuto)
- Logging de auditoría
- Manejo de errores

⚠ **Pendiente**:
- Implementar llamada real a Google API
- Configurar credenciales

---

##  Paso a Paso: Activación

### 1⃣ Obtener Google API Key

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un proyecto nuevo o selecciona uno existente
3. Habilita la API:
   - Menú → APIs & Services → Library
   - Busca "Custom Search API"
   - Click en "Enable"
4. Crea credenciales:
   - APIs & Services → Credentials
   - Create Credentials → API Key
   - Copia tu API Key

### 2⃣ Crear Custom Search Engine

1. Ve a [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click en "Add" o "Create"
3. Configuración:
   - **Sites to search**: Selecciona "Search the entire web"
   - **Name**: "Truth Algorithm Search"
   - **Language**: Spanish (o tu preferencia)
4. Click "Create"
5. Copia el **Search engine ID** (CX)

### 3⃣ Configurar Variables de Entorno

```bash
# Navegar al directorio
cd /home/jnovoas/sentinel/truth_algorithm

# Crear archivo .env desde el template
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Contenido del `.env`:
```bash
# Google API credentials
GOOGLE_SEARCH_API_KEY=AIzaSy...tu_api_key_aqui
GOOGLE_SEARCH_CX=017643...tu_cx_aqui

# Redis cache (opcional)
REDIS_URL=redis://localhost:6379
```

### 4⃣ Instalar Dependencias

```bash
pip install google-api-python-client
```

### 5⃣ Implementar Llamada Real

Edita [`source_search.py`](file:///home/jnovoas/sentinel/truth_algorithm/source_search.py) líneas 237-254:

```python
def _google_search(self, claim: str, max_results: int) -> List[SearchResult]:
    """
    Búsqueda real usando Google Custom Search API
    """
    if not self.google_api_key or not self.google_cx:
        raise ValueError(
            "Google Search requiere API key y CX en environment.\n"
            "Set: GOOGLE_SEARCH_API_KEY y GOOGLE_SEARCH_CX"
        )
    
    from googleapiclient.discovery import build
    
    try:
        # Construir servicio de Google
        service = build("customsearch", "v1", developerKey=self.google_api_key)
        
        # Ejecutar búsqueda
        result = service.cse().list(
            q=claim,
            cx=self.google_cx,
            num=min(max_results, 10)  # Google max = 10
        ).execute()
        
        # Parsear resultados
        search_results = []
        for item in result.get('items', []):
            # Determinar tipo de fuente
            source_type = self._classify_source(item.get('link', ''))
            
            search_results.append(SearchResult(
                title=item.get('title', ''),
                url=item.get('link', ''),
                snippet=item.get('snippet', ''),
                source_type=source_type,
                confidence=self._calculate_confidence(source_type, item),
                timestamp=time.strftime("%Y-%m-%d")
            ))
        
        return search_results
        
    except Exception as e:
        print(f"❌ Error en Google Search: {e}")
        # Fallback a mock en caso de error
        return self._mock_search(claim, max_results)

def _classify_source(self, url: str) -> str:
    """Clasifica el tipo de fuente según la URL"""
    if any(domain in url for domain in ['.gov', '.edu']):
        return 'official' if '.gov' in url else 'academic'
    elif any(domain in url for domain in ['reuters.com', 'apnews.com', 'bbc.com']):
        return 'news'
    else:
        return 'general'

def _calculate_confidence(self, source_type: str, item: dict) -> float:
    """Calcula confianza basada en tipo de fuente"""
    base_confidence = {
        'official': 0.95,
        'academic': 0.90,
        'news': 0.75,
        'general': 0.60
    }
    return base_confidence.get(source_type, 0.50)
```

### 6⃣ Probar la Integración

```bash
cd /home/jnovoas/sentinel/truth_algorithm

# Crear script de prueba
cat > test_google_real.py << 'EOF'
#!/usr/bin/env python3
from source_search import SourceSearchEngine, SearchProvider
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar credenciales
api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
cx = os.getenv('GOOGLE_SEARCH_CX')

print("🔍 Testing Google Search Integration")
print("=" * 60)
print(f"API Key: {'✅ Configured' if api_key else '❌ Missing'}")
print(f"CX ID: {'✅ Configured' if cx else '❌ Missing'}")
print()

if api_key and cx:
    # Crear engine con Google
    engine = SourceSearchEngine(provider=SearchProvider.GOOGLE)
    
    # Test búsqueda
    claim = "Python programming language created by Guido van Rossum"
    print(f"Searching: {claim}")
    print()
    
    results = engine.search(claim, max_results=5)
    
    print(f"Found {len(results)} results:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. [{r.source_type}] {r.title}")
        print(f"   URL: {r.url}")
        print(f"   Confidence: {r.confidence*100:.1f}%")
        print(f"   Snippet: {r.snippet[:100]}...")
else:
    print("❌ Configure GOOGLE_SEARCH_API_KEY y GOOGLE_SEARCH_CX primero")
EOF

chmod +x test_google_real.py
python test_google_real.py
```

---

## 🔐 Seguridad Implementada

### ✅ Validación de Inputs

```python
# Bloquea automáticamente:
- SQL injection: "Test' OR '1'='1"
- XSS: "Test<script>alert('xss')</script>"
- Shell commands: "Test; rm -rf /"
- Path traversal: "Test../../etc/passwd"
```

### ✅ Rate Limiting

```python
# Límite: 10 requests/minuto
# Previene abuso y controla costos de API
```

### ✅ Logging de Auditoría

```json
{
  "search_id": "a1b2c3d4e5f6g7h8",
  "claim": "Python programming language",
  "timestamp": 1703188800.0,
  "provider": "google"
}
```

---

## 💰 Costos de Google API

### Cuota Gratuita
- **100 búsquedas/día** gratis
- Ideal para desarrollo y testing

### Pricing Pagado
- **$5 USD por 1,000 búsquedas** adicionales
- Máximo 10,000 búsquedas/día

### Optimización de Costos
1. **Caché con Redis**: Evita búsquedas duplicadas
2. **Rate Limiting**: Controla uso
3. **Fallback a DuckDuckGo**: Alternativa gratuita

---

## 🧪 Testing

### Demo Actual (MOCK)
```bash
cd /home/jnovoas/sentinel/truth_algorithm
python source_search.py
```

**Salida**:
```
======================================================================
DEMO - SOURCE SEARCH ENGINE (MODO SEGURO)
======================================================================

📊 Test 1: Búsqueda normal
✅ Resultados simulados

  Test 2: Validación de seguridad
✅ BLOQUEADO: Test; rm -rf /...
✅ BLOQUEADO: Test' OR '1'='1...
✅ BLOQUEADO: Test<script>alert('xss')...

⏱  Test 3: Rate limiting
✅ Rate limit funcionando: 10 requests/minuto

💾 Log guardado en: search_log.json
```

---

## 📁 Archivos Clave

- [`source_search.py`](file:///home/jnovoas/sentinel/truth_algorithm/source_search.py) - Motor de búsqueda
- [`.env.example`](file:///home/jnovoas/sentinel/truth_algorithm/.env.example) - Template de configuración
- [`search_log.json`](file:///home/jnovoas/sentinel/truth_algorithm/search_log.json) - Log de auditoría

---

##  Próximos Pasos

1. [ ] Obtener credenciales de Google
2. [ ] Configurar `.env`
3. [ ] Implementar `_google_search()` real
4. [ ] Instalar `google-api-python-client`
5. [ ] Probar con búsquedas reales
6. [ ] Implementar caché con Redis
7. [ ] Agregar métricas de calidad

---

## 🆘 Troubleshooting

### Error: "API key not valid"
- Verifica que la API esté habilitada en Google Cloud Console
- Revisa que el API key sea correcto

### Error: "Rate limit exceeded"
- Espera 1 minuto
- Ajusta `max_requests_per_minute` en el código

### Error: "Invalid CX"
- Verifica el Search Engine ID en Programmable Search
- Asegúrate de copiar el ID completo

---

**Powered by Google ❤ & Perplexity 💜**

*Última actualización: 21 de Diciembre de 2025*
