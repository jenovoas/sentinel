# Instrucciones para Benchmark de Google Search
# ===============================================

## ⚠️ IMPORTANTE: Seguridad de Credenciales

Este benchmark requiere credenciales de Google API, pero **NUNCA** las pongas en el código.

## 🔐 Configuración Segura

### Opción 1: Variables de Entorno (Recomendado)

```bash
# En tu terminal (NO en el código)
export GOOGLE_SEARCH_API_KEY="tu_api_key_aqui"
export GOOGLE_SEARCH_CX="tu_cx_id_aqui"

# Ejecutar benchmark
python benchmark_google_speed.py
```

### Opción 2: Archivo .env Local (NO commitear)

```bash
# Crear archivo .env (ya está en .gitignore)
echo "GOOGLE_SEARCH_API_KEY=tu_api_key" > .env
echo "GOOGLE_SEARCH_CX=tu_cx_id" >> .env

# Ejecutar benchmark
python benchmark_google_speed.py
```

## ✅ El Código es Público-Safe

- ✅ Las credenciales se leen desde variables de entorno
- ✅ NUNCA se hardcodean en el código
- ✅ El archivo `.env` está en `.gitignore`
- ✅ El código puede ser público sin riesgo

## 📊 Qué Mide el Benchmark

- Tiempo de respuesta de Google Search API
- Latencia de red
- Número de resultados obtenidos
- Estadísticas (promedio, mínimo, máximo)

## 🎯 Resultados Esperados

- Tiempo típico: 200-500ms por búsqueda
- Incluye latencia de red + procesamiento de Google
- Varía según ubicación geográfica

## 💡 Alternativa Sin Credenciales

Si no quieres usar tu API de Google, usa DuckDuckGo:

```bash
python benchmark_duckduckgo_speed.py  # (próximamente)
```

---

**Powered by Google ❤️ & Perplexity 💜**
