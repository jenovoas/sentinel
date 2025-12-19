# 🔍 Análisis de Mejoras Adicionales - Sentinel

**Fecha**: 19 Diciembre 2024, 13:53  
**Estado**: keep_alive configurado, mejora moderada  
**Próximo paso**: Identificar cuellos de botella adicionales

---

## 📊 COMPARACIÓN: Antes vs Después de keep_alive

### Resultados Medidos

| Métrica | Sin keep_alive | Con keep_alive | Mejora | Observación |
|---------|----------------|----------------|--------|-------------|
| **E2E p50** | 6,520ms | 7,244ms | **-11%** ❌ | Empeoró ligeramente |
| **LLM TTFB p50** | 1,230ms | 1,213ms | **+1.4%** ⚠️ | Mejora marginal |
| **Mejor caso E2E** | 639ms | 591ms | **+7.5%** ✅ | Mejor caso mejoró |
| **Mejor caso TTFB** | 507ms | 571ms | **-13%** ❌ | Empeoró |
| **CPU** | 14.1% | 18.7% | **-33%** ❌ | Peor eficiencia |

### Conclusión

**keep_alive NO resolvió el problema principal** ⚠️

La varianza sigue siendo alta:
- E2E: 591ms (mejor) vs 12,376ms (peor) = **20.9x diferencia**
- TTFB: 571ms (mejor) vs 1,615ms (peor) = **2.8x diferencia**

---

## 🔍 ANÁLISIS DE CUELLO DE BOTELLA

### ¿Por qué sigue lento?

**Hipótesis 1: Hardware Limitado (GTX 1050 3GB)** ✅ MÁS PROBABLE

```
EVIDENCIA:
├── TTFB promedio: 1,213ms (vs objetivo <300ms)
├── Alta varianza: 2.8x diferencia
├── CPU picos: 38.9% (GPU no puede manejar carga)
└── Modelo: llama3.2:1b (1.3GB) cabe en VRAM pero es lento

CAUSA RAÍZ:
└── GTX 1050 es GPU antigua (2016)
    ├── CUDA cores: 640 (vs RTX 3060: 3,584)
    ├── Tensor cores: 0 (vs RTX 3060: 112)
    └── Performance: ~5x más lento que GPUs modernas
```

**Hipótesis 2: Modelo No Optimizado** ✅ PROBABLE

```
EVIDENCIA:
├── Modelo actual: llama3.2:1b (no quantizado)
├── Tamaño: 1.3GB (puede ser más pequeño)
└── Formato: GGUF (puede optimizarse más)

SOLUCIÓN:
└── Probar modelos más pequeños/optimizados
    ├── tinyllama (637MB, 1.1B params)
    ├── phi3:mini-q4_K_M (2.2GB quantizado)
    └── qwen2.5:0.5b (500MB, ultra rápido)
```

**Hipótesis 3: Configuración Ollama Subóptima** ✅ POSIBLE

```
EVIDENCIA:
├── num_ctx: 2048 (puede ser muy grande)
├── num_batch: 128 (puede optimizarse)
└── num_thread: default (puede ajustarse)

SOLUCIÓN:
└── Ajustar parámetros Ollama
    ├── num_ctx: 512 (reducir context window)
    ├── num_batch: 64 (reducir batch size)
    └── num_thread: 4 (optimizar para CPU)
```

**Hipótesis 4: Código Python Overhead** ⚠️ MENOS PROBABLE

```
EVIDENCIA:
├── Streaming async: Puede tener overhead
├── Buffers: Pueden agregar latencia
└── httpx: Puede ser más lento que requests

SOLUCIÓN:
└── Optimizar código Python
    ├── Usar aiohttp en lugar de httpx
    ├── Reducir overhead de buffers
    └── Profiling con cProfile
```

---

## 🎯 PLAN DE MEJORAS (Ordenado por Impacto)

### 1. Probar Modelo Más Pequeño (ALTO IMPACTO)

**Acción**: Cambiar a `qwen2.5:0.5b` (500MB, ultra rápido)

```bash
# Descargar modelo
ollama pull qwen2.5:0.5b

# Configurar keep_alive
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:0.5b",
  "prompt": "warmup",
  "keep_alive": -1
}'

# Actualizar sentinel_fluido.py
# model: str = "qwen2.5:0.5b"

# Re-ejecutar benchmark
python sentinel_global_benchmark.py
```

**Mejora Esperada**: 1,213ms → **400-600ms** (2-3x)

### 2. Optimizar Parámetros Ollama (MEDIO IMPACTO)

**Acción**: Reducir context window y batch size

```python
# En sentinel_fluido.py, línea ~190
"options": {
    "temperature": 0.7,
    "num_predict": 256,      # Reducir de 512
    "num_ctx": 512,          # Reducir de 2048 (4x)
    "num_batch": 64,         # Reducir de 128 (2x)
    "num_gpu": 1,            # Forzar GPU
    "num_thread": 4          # Optimizar CPU
}
```

**Mejora Esperada**: 1,213ms → **800-1,000ms** (1.2-1.5x)

### 3. Usar Modelo Quantizado (MEDIO IMPACTO)

**Acción**: Probar `phi3:mini-q4_K_M` (quantizado 4-bit)

```bash
# Descargar modelo quantizado
ollama pull phi3:mini-q4_K_M

# Configurar keep_alive
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini-q4_K_M",
  "prompt": "warmup",
  "keep_alive": -1
}'
```

**Mejora Esperada**: 1,213ms → **700-900ms** (1.3-1.7x)

### 4. Optimizar Código Python (BAJO IMPACTO)

**Acción**: Reducir overhead de streaming

```python
# Opción 1: Usar aiohttp en lugar de httpx
import aiohttp

# Opción 2: Reducir overhead de buffers
# Eliminar buffer updates en cada chunk

# Opción 3: Profiling
python -m cProfile -o profile.stats sentinel_global_benchmark.py
```

**Mejora Esperada**: 1,213ms → **1,100-1,200ms** (1.01-1.1x)

### 5. Upgrade Hardware (MÁXIMO IMPACTO, COSTO)

**Acción**: Upgrade a RTX 3060 12GB (~$300)

**Mejora Esperada**: 1,213ms → **100-200ms** (6-12x) ✅

---

## 🚀 RECOMENDACIÓN INMEDIATA

### Prueba Rápida (5 minutos)

**Paso 1**: Probar modelo más pequeño

```bash
# 1. Descargar qwen2.5:0.5b (500MB, ultra rápido)
ollama pull qwen2.5:0.5b

# 2. Configurar keep_alive
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:0.5b",
  "prompt": "warmup",
  "keep_alive": -1
}'

# 3. Actualizar modelo en código
sed -i 's/llama3.2:1b/qwen2.5:0.5b/g' backend/app/services/sentinel_fluido.py

# 4. Re-ejecutar benchmark
cd backend && python sentinel_global_benchmark.py
```

**Paso 2**: Optimizar parámetros Ollama

```python
# Editar backend/app/services/sentinel_fluido.py
# Línea ~190, cambiar:
"options": {
    "temperature": 0.7,
    "num_predict": 256,      # ← CAMBIO
    "num_ctx": 512,          # ← CAMBIO
    "num_batch": 64,         # ← CAMBIO
    "num_gpu": 1,
    "num_thread": 4
}
```

**Paso 3**: Re-ejecutar benchmark

```bash
cd backend && python sentinel_global_benchmark.py
```

---

## 📊 MEJORA PROYECTADA (Combinando Optimizaciones)

### Escenario Optimista

| Optimización | Mejora Individual | Mejora Acumulada |
|--------------|-------------------|------------------|
| **Baseline** | - | 1,213ms |
| + Modelo pequeño (qwen2.5:0.5b) | 2-3x | **400-600ms** |
| + Parámetros optimizados | 1.2x | **330-500ms** |
| + Código optimizado | 1.1x | **300-450ms** |

**Resultado Final**: **300-450ms TTFB** ✅ (cerca del objetivo <300ms)

### Escenario Realista

| Optimización | Mejora Individual | Mejora Acumulada |
|--------------|-------------------|------------------|
| **Baseline** | - | 1,213ms |
| + Modelo pequeño (qwen2.5:0.5b) | 2x | **600ms** |
| + Parámetros optimizados | 1.3x | **460ms** |

**Resultado Final**: **~460ms TTFB** ✅ (objetivo <500ms cumplido)

---

## 🎯 OBJETIVOS ALCANZABLES

### Con Optimizaciones de Software (Sin Costo)

```
TTFB: 1,213ms → 300-460ms (2.6-4x mejora)
E2E: 7,244ms → 500-800ms (9-14x mejora)
Speedup total: 10-20x ✅ (cerca del objetivo)
```

### Con Upgrade Hardware ($300)

```
TTFB: 1,213ms → 100-200ms (6-12x mejora)
E2E: 7,244ms → 200-400ms (18-36x mejora)
Speedup total: 20-50x ✅ (supera objetivo)
```

---

## 📝 PRÓXIMOS PASOS

### Inmediato (HOY)

1. [ ] Probar `qwen2.5:0.5b` (modelo más pequeño)
2. [ ] Optimizar parámetros Ollama
3. [ ] Re-ejecutar benchmark
4. [ ] Documentar mejoras

### Corto Plazo (Esta Semana)

1. [ ] Probar `phi3:mini-q4_K_M` (quantizado)
2. [ ] Optimizar código Python
3. [ ] Validar 10-20x speedup
4. [ ] Preparar presentación ANID

### Mediano Plazo (1 Mes)

1. [ ] Evaluar upgrade GPU (RTX 3060)
2. [ ] Implementar Buffer ML
3. [ ] Validar 30x+ speedup
4. [ ] Presentar a ANID

---

## ✅ CONCLUSIÓN

**Resultados Actuales**:
- ✅ keep_alive configurado
- ⚠️ Mejora marginal (1.4%)
- ❌ Objetivo no alcanzado

**Problema Identificado**:
- 🔧 Hardware limitado (GTX 1050)
- 🔧 Modelo no optimizado
- 🔧 Parámetros Ollama subóptimos

**Solución Inmediata**:
- ✅ Probar modelo más pequeño (qwen2.5:0.5b)
- ✅ Optimizar parámetros Ollama
- ✅ Mejora proyectada: 2.6-4x (300-460ms TTFB)

**Próxima Acción**: Probar `qwen2.5:0.5b` y optimizar parámetros.

---

**¿Probamos el modelo más pequeño ahora?** 🚀
