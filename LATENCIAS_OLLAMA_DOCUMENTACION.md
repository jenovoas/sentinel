# 📊 Documentación de Latencias - Ollama Optimización

**Fecha**: 19 Diciembre 2024  
**Hardware**: GTX 1050 (3GB VRAM)  
**Objetivo**: Documentar mejoras de latencia antes/después optimización

---

## 🔬 BASELINE - phi3:mini (Sin Optimizar)

### Métricas Medidas

| Métrica | Valor | Observación |
|---------|-------|-------------|
| **TTFB Promedio** | **21,470ms** (~21.5s) | ❌ Muy alto |
| **TTFB Mediana** | **14,908ms** (~15s) | ❌ Muy alto |
| **TTFB Mínimo** | **3,627ms** (~3.6s) | ⚠️ Aceptable (modelo en RAM) |
| **TTFB Máximo** | **49,874ms** (~50s) | ❌ Inaceptable |
| **Requests** | 5 | - |

### Análisis

**Problema Identificado**: Ollama descarga/carga modelo entre requests
- Primera request: 3.6s (modelo ya en RAM)
- Segunda request: 49.9s (descarga modelo)
- Tercera request: 8.9s (carga desde disco)
- Cuarta request: 14.9s (carga desde disco)
- Quinta request: 30s (carga desde disco)

**Causa Raíz**: 
- Modelo phi3:mini (~3.5GB) no cabe completamente en 3GB VRAM
- Ollama hace swapping CPU ↔ GPU
- Sin configuración `keep_alive`, descarga modelo cada vez

---

## ⚡ OPTIMIZACIÓN PROPUESTA

### 1. Modelo Quantizado (phi3:mini-q4_K_M)

**Beneficios Esperados**:
```
Tamaño: 3.5GB → 2.2GB (-37%)
VRAM fit: ❌ → ✅ (cabe en 3GB)
TTFB esperado: 21.5s → <2s (-90%)
```

**Comando**:
```bash
ollama pull phi3:mini-q4_K_M
```

### 2. Keep Alive Permanente

**Beneficios Esperados**:
```
Modelo en RAM: Temporal → Permanente
TTFB subsecuente: 15s → <500ms (-97%)
```

**Comando**:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini-q4_K_M",
  "prompt": "warmup",
  "keep_alive": -1
}'
```

### 3. Configuración Optimizada

**Parámetros**:
```json
{
  "num_ctx": 2048,     // Reducir context window
  "num_batch": 128,    // Batch size optimizado
  "num_gpu": 1,        // Forzar GPU
  "num_thread": 4      // Threads CPU
}
```

---

## 🎯 TARGETS POST-OPTIMIZACIÓN

| Métrica | Baseline | Target | Mejora |
|---------|----------|--------|--------|
| **TTFB Primera** | 21.5s | <2s | **-90%** |
| **TTFB Subsecuente** | 15s | <500ms | **-97%** |
| **TTFB Promedio** | 21.5s | <1s | **-95%** |
| **Estabilidad** | ❌ Alta varianza | ✅ Consistente | - |

---

## 📋 PLAN DE EJECUCIÓN

### Paso 1: Descargar Modelo Optimizado
```bash
ollama pull phi3:mini-q4_K_M
```

### Paso 2: Configurar Keep Alive
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini-q4_K_M",
  "prompt": "warmup",
  "keep_alive": -1
}'
```

### Paso 3: Ejecutar Benchmark Comparativo
```bash
cd /home/jnovoas/sentinel/backend
python benchmark_comparativo.py
```

### Paso 4: Documentar Resultados
- Comparar TTFB antes/después
- Calcular % mejora
- Validar targets (<2s primera, <500ms subsecuente)

---

## 📊 RESULTADOS ESPERADOS

### Escenario Optimista (Modelo en RAM)
```
TTFB: 500-1000ms
Mejora: 95%+ vs baseline
Estado: ✅ Cumple targets
```

### Escenario Realista (Primera carga)
```
TTFB: 1500-2000ms
Mejora: 90%+ vs baseline
Estado: ✅ Cumple targets
```

### Escenario Pesimista (Swapping)
```
TTFB: 3000-5000ms
Mejora: 75%+ vs baseline
Estado: ⚠️ Mejor que baseline pero no ideal
```

---

## 🔍 VALIDACIÓN

### Criterios de Éxito
- ✅ TTFB promedio <2s
- ✅ TTFB subsecuente <500ms
- ✅ Varianza <50% (estabilidad)
- ✅ Modelo cabe en VRAM (sin swapping)

### Si No Cumple Targets
**Plan B**: Modelo más pequeño
```bash
ollama pull tinyllama  # 1.1B params, 637MB
```

**Plan C**: Upgrade GPU
```
RTX 3060 12GB (~$300)
→ Permite modelos más grandes
→ vLLM con SPIRe+MTAD
→ TTFB <200ms garantizado
```

---

## 📝 NOTAS TÉCNICAS

### Por Qué Funciona la Optimización

1. **Quantización 4-bit**:
   - Reduce tamaño 37%
   - Mantiene 95% calidad
   - Cabe en 3GB VRAM

2. **Keep Alive**:
   - Modelo permanece en RAM
   - Elimina overhead de carga
   - TTFB consistente

3. **Configuración Optimizada**:
   - Context window reducido
   - Batch size balanceado
   - GPU prioritizada

### Limitaciones Conocidas

- GTX 1050 (3GB) es el cuello de botella
- Modelos >2.5GB requieren swapping
- Upgrade GPU eliminaría limitación

---

## 🚀 PRÓXIMOS PASOS

1. **HOY**: Ejecutar optimización y validar
2. **Esta semana**: Documentar resultados reales
3. **Próximo mes**: Evaluar upgrade GPU si necesario

---

**Estado**: ✅ Baseline documentado, listo para optimizar  
**Próxima acción**: Ejecutar `ollama pull phi3:mini-q4_K_M`
