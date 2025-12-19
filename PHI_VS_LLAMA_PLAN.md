# 🔬 Comparación phi3 vs llama3 - Plan de Pruebas

## 🎯 Objetivo

Comparar latencias de diferentes modelos pequeños para encontrar el más rápido en GTX 1050 (3GB VRAM).

## 📋 Modelos a Probar

| Modelo | Tamaño | Parámetros | Estado |
|--------|--------|------------|--------|
| **phi3:mini** | 2.2 GB | 2.7B | ✅ Instalado |
| **llama3.2:1b** | 1.3 GB | 1B | 🔄 Descargando |

## 🧪 Metodología

### Test por Modelo
- 5 requests con mensajes variados
- Medir TTFB (Time To First Byte)
- Calcular: promedio, mediana, mín, máx

### Métricas Clave
- **TTFB Promedio**: Latencia típica
- **TTFB Mínimo**: Mejor caso (modelo en RAM)
- **TTFB Máximo**: Peor caso (carga desde disco)
- **Estabilidad**: Varianza entre requests

## 📊 Hipótesis

### llama3.2:1b (1B params, 1.3GB)
**Ventajas**:
- ✅ Más pequeño (cabe mejor en 3GB VRAM)
- ✅ Menos parámetros = más rápido
- ✅ Menos swapping CPU/GPU

**Desventajas**:
- ⚠️ Menor calidad de respuestas
- ⚠️ Menos conocimiento

**TTFB Esperado**: 1-2s (mejor que phi3)

### phi3:mini (2.7B params, 2.2GB)
**Ventajas**:
- ✅ Mejor calidad de respuestas
- ✅ Más conocimiento
- ✅ Ya probado (baseline conocido)

**Desventajas**:
- ⚠️ Más grande (2.2GB)
- ⚠️ Más parámetros = más lento
- ⚠️ Más swapping en 3GB VRAM

**TTFB Esperado**: 3-5s (baseline actual con keep_alive)

## 🎯 Criterios de Decisión

### Si llama3.2:1b es >30% más rápido
→ **Usar llama3.2:1b** (velocidad > calidad)

### Si diferencia <30%
→ **Usar phi3:mini** (mejor calidad)

### Si ambos >5s TTFB
→ **Considerar upgrade GPU** o modelos más pequeños

## 📝 Ejecución

```bash
# 1. Esperar descarga llama3.2:1b
ollama list

# 2. Configurar keep_alive para ambos
bash scripts/ollama_keep_alive.sh phi3:mini
bash scripts/ollama_keep_alive.sh llama3.2:1b

# 3. Ejecutar benchmark comparativo
cd backend
python benchmark_phi_vs_llama.py
```

## 📊 Resultados Esperados

### Escenario Optimista
```
llama3.2:1b: 1-2s TTFB
phi3:mini: 3-5s TTFB
Ganador: llama3.2:1b (50% más rápido)
```

### Escenario Realista
```
llama3.2:1b: 2-3s TTFB
phi3:mini: 4-6s TTFB
Ganador: llama3.2:1b (40% más rápido)
```

### Escenario Pesimista
```
llama3.2:1b: 3-4s TTFB
phi3:mini: 5-7s TTFB
Ganador: llama3.2:1b (30% más rápido)
```

## 🚀 Próximos Pasos

1. ✅ Descargar llama3.2:1b
2. ⏳ Ejecutar benchmark comparativo
3. ⏳ Documentar resultados
4. ⏳ Elegir modelo ganador
5. ⏳ Configurar Sentinel con modelo óptimo

---

**Estado**: 🔄 Descargando llama3.2:1b...  
**Próxima acción**: Ejecutar `benchmark_phi_vs_llama.py`
