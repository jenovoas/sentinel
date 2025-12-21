# Source Search Engine - Documentación de Seguridad

## 🛡️ Controles de Seguridad Implementados

### 1. Validación de Inputs

**Bloquea**:
- ✅ Comandos de shell (`; & | $ \``)
- ✅ Path traversal (`../`)
- ✅ XSS (`<script>`)
- ✅ SQL injection (`DROP TABLE`)
- ✅ Comandos destructivos (`rm -rf`)
- ✅ Code execution (`eval()`)

**Límites**:
- ✅ Máximo 500 caracteres por claim
- ✅ Solo caracteres seguros

### 2. Rate Limiting

**Límites**:
- ✅ 10 requests por minuto (configurable)
- ✅ Tracking de requests en ventana deslizante
- ✅ Exception si se excede

### 3. Validación de URLs

**Bloquea**:
- ✅ URLs no-HTTPS
- ✅ IPs privadas (127.0.0.1, 192.168.x.x, etc.)
- ✅ localhost
- ✅ Redes privadas

### 4. API Keys

**Seguridad**:
- ✅ NUNCA hardcoded en código
- ✅ Solo desde variables de entorno
- ✅ Validación antes de uso

### 5. Logging

**Auditoría**:
- ✅ Todas las búsquedas loggeadas
- ✅ Hash único por búsqueda
- ✅ Timestamp de cada operación
- ✅ Export a JSON para análisis

### 6. Modo Mock

**Testing Seguro**:
- ✅ NO hace llamadas reales por defecto
- ✅ Simula resultados para testing
- ✅ Usuario debe activar APIs reales explícitamente

---

## 🔐 Cómo Usar de Forma Segura

### Paso 1: Testing (SEGURO)

```python
from source_search import SourceSearchEngine, SearchProvider

# Modo MOCK - NO hace llamadas reales
engine = SourceSearchEngine(provider=SearchProvider.MOCK)

# Buscar (solo simulación)
results = engine.search("La tasa de desempleo es 3.5%")
```

### Paso 2: Configurar API Keys (SI DECIDES USARLAS)

```bash
# En tu .bashrc o .zshrc
export GOOGLE_SEARCH_API_KEY="tu-api-key-aqui"
export GOOGLE_SEARCH_CX="tu-cx-aqui"
```

### Paso 3: Usar API Real (SOLO SI LO APRUEBAS)

```python
# REQUIERE tu aprobación explícita
engine = SourceSearchEngine(provider=SearchProvider.GOOGLE)
results = engine.search("claim a verificar")
```

---

## ⚠️ IMPORTANTE

**NUNCA**:
- ❌ Hardcodear API keys en código
- ❌ Commitear API keys a Git
- ❌ Compartir API keys públicamente
- ❌ Usar en producción sin rate limiting

**SIEMPRE**:
- ✅ Revisar código antes de ejecutar
- ✅ Usar modo MOCK para testing
- ✅ Validar inputs
- ✅ Monitorear logs

---

## 🧪 Tests de Seguridad

Ejecutar demo de seguridad:

```bash
cd truth_algorithm
python3 source_search.py
```

Esto ejecuta:
1. ✅ Búsqueda normal (modo mock)
2. ✅ Validación de inputs peligrosos
3. ✅ Rate limiting
4. ✅ Logging

**TODO ES SIMULADO** - No hace llamadas reales.

---

## 📋 Checklist de Revisión

Antes de usar con APIs reales, verifica:

- [ ] API keys en environment (no hardcoded)
- [ ] Rate limiting configurado
- [ ] Validación de inputs activa
- [ ] Logging funcionando
- [ ] URLs validadas
- [ ] Modo mock testeado primero

---

**Powered by Google** ❤️ | Built with Gemini AI

**Filosofía**: "No abrir la puerta trasera así nada más" - Jaime Novoa
