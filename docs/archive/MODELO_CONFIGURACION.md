# 🎯 Configuración de Modelos - Sentinel

## ✅ Modelo en Producción

**Modelo Activo**: `llama3.2:1b`

### Especificaciones
- **Tamaño**: 1.3 GB
- **Parámetros**: 1B
- **VRAM**: Cabe perfectamente en GTX 1050 (3GB)

### Métricas Validadas
- **TTFB Promedio**: 10.4s
- **TTFB Mínimo**: 5.3s (modelo en RAM)
- **TTFB Máximo**: 16.7s
- **Estabilidad**: ✅ Buena (varianza moderada)

### Ventajas
- ✅ **2.7x más rápido** que phi3:mini
- ✅ **63% menos latencia**
- ✅ Cabe mejor en 3GB VRAM
- ✅ Menos swapping CPU/GPU
- ✅ Respuestas consistentes

---

## 🧪 Modelos en Testing

### phi3:mini
**Estado**: Testing / Desarrollo

**Especificaciones**:
- Tamaño: 2.2 GB
- Parámetros: 2.7B

**Métricas**:
- TTFB Promedio: 28.1s
- TTFB Mínimo: 6.3s
- TTFB Máximo: 49.4s

**Razón Testing**:
- ⚠️ 2.7x más lento que llama3.2:1b
- ⚠️ Alta varianza (6s - 49s)
- ⚠️ Requiere optimización adicional

**Plan de Mejora**:
1. Probar versión quantizada (phi3:mini-q4_K_M)
2. Optimizar configuración Ollama
3. Evaluar con mejor GPU (futuro)

---

## 📊 Benchmark Comparativo

| Modelo | TTFB Avg | TTFB Min | TTFB Max | Tamaño | Estado |
|--------|----------|----------|----------|--------|--------|
| **llama3.2:1b** | **10.4s** | **5.3s** | **16.7s** | 1.3GB | ✅ **PRODUCCIÓN** |
| phi3:mini | 28.1s | 6.3s | 49.4s | 2.2GB | 🧪 Testing |

**Mejora**: llama3.2:1b es **2.7x más rápido**

---

## 🔧 Configuración Actual

### Sentinel Fluido
```python
# backend/app/services/sentinel_fluido.py
model: str = "llama3.2:1b"  # Modelo por defecto
```

### Keep Alive
```bash
# Mantener modelo en memoria
bash scripts/ollama_keep_alive.sh llama3.2:1b
```

### Verificar Estado
```bash
ollama list
curl -s http://localhost:11434/api/ps
```

---

## 🚀 Uso

### Código
```python
from app.services.sentinel_fluido import sentinel_fluido

# Usa llama3.2:1b por defecto
async for chunk, ttfb in sentinel_fluido.responder("user_id", "mensaje"):
    print(chunk, end='', flush=True)

# O especificar modelo manualmente
sentinel_custom = SentinelFluido(model="phi3:mini")  # Testing
```

### Tests
```bash
# Test con modelo por defecto (llama3.2:1b)
cd backend
python test_fluido.py

# Benchmark comparativo
python benchmark_phi_vs_llama.py
```

---

## 📝 Próximos Pasos

### Corto Plazo (Esta Semana)
1. ✅ Configurar llama3.2:1b como default
2. ✅ Documentar resultados
3. ⏳ Probar en casos de uso reales
4. ⏳ Validar calidad de respuestas

### Mediano Plazo (1-2 Semanas)
1. Optimizar phi3:mini (quantización)
2. Probar otros modelos pequeños
3. Documentar trade-offs calidad vs velocidad

### Largo Plazo (1-3 Meses)
1. Upgrade GPU (RTX 3060 12GB)
2. Migrar a vLLM
3. Implementar SPIRe + MTAD
4. Target: TTFB <200ms

---

## 🎯 Criterios de Cambio

### Cambiar a otro modelo si:
- Nuevo modelo >30% más rápido
- Calidad de respuestas significativamente mejor
- Cabe mejor en hardware actual

### Volver a phi3:mini si:
- Calidad de llama3.2:1b insuficiente
- Se optimiza phi3 a <10s TTFB
- Se hace upgrade GPU

---

**Última actualización**: 19 Diciembre 2024  
**Modelo activo**: llama3.2:1b  
**Próxima revisión**: Después de validar en producción
