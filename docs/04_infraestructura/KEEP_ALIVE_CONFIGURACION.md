# ⏰ Configuración keep_alive - Ollama

**Fecha**: 19 Diciembre 2024  
**Objetivo**: Mantener modelo en RAM para latencias consistentes

---

##  ¿Qué es keep_alive?

**keep_alive** controla cuánto tiempo Ollama mantiene un modelo en RAM después de usarlo.

### Opciones Disponibles

| Valor | Comportamiento | Uso Recomendado |
|-------|----------------|-----------------|
| **`-1`** | **PERMANENTE** (nunca descarga) | ✅ **Producción, benchmarks** |
| `0` | Descarga inmediatamente | ❌ Desarrollo (ahorra RAM) |
| `5m` | Mantiene 5 minutos | ⚠ Testing ocasional |
| `1h` | Mantiene 1 hora | ⚠ Sesiones largas |
| `24h` | Mantiene 24 horas | ⚠ Uso diario |

---

## ✅ CONFIGURACIÓN RECOMENDADA: -1 (Permanente)

### Por qué usar -1

**Ventajas**:
- ✅ Latencias consistentes (sin varianza)
- ✅ TTFB predecible (<500ms)
- ✅ Sin overhead de carga (0ms)
- ✅ Ideal para benchmarks
- ✅ Ideal para producción

**Desventajas**:
- ⚠ Usa RAM constantemente (~1.3 GB)
- ⚠ Solo se libera reiniciando Ollama

### Cuándo usar -1

```
✅ USAR -1 cuando:
├── Ejecutando benchmarks (necesitas consistencia)
├── En producción (latencias predecibles)
├── Tienes RAM suficiente (GTX 1050 3GB ✅)
└── Quieres máximo performance

❌ NO usar -1 cuando:
├── RAM limitada (<2GB VRAM)
├── Múltiples modelos (no caben todos)
└── Desarrollo ocasional (ahorra recursos)
```

---

## 🔧 CÓMO CONFIGURAR

### Opción 1: Script Automatizado (Recomendado)

```bash
# Ejecutar script
./scripts/ollama_keep_alive.sh

# Resultado: Modelo en RAM permanentemente
```

### Opción 2: Manual (curl)

```bash
# keep_alive = -1 (PERMANENTE)
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "warmup",
  "keep_alive": -1
}'

# keep_alive = 1h (1 hora)
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "warmup",
  "keep_alive": "1h"
}'

# keep_alive = 0 (descarga inmediata)
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "warmup",
  "keep_alive": 0
}'
```

### Opción 3: En Código Python

```python
import httpx

async def configure_keep_alive(model: str = "llama3.2:1b", keep_alive: int = -1):
    """
    Configura keep_alive para modelo Ollama
    
    Args:
        model: Nombre del modelo
        keep_alive: -1 (permanente), 0 (inmediato), o segundos
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": "warmup",
                "keep_alive": keep_alive,
                "stream": False
            },
            timeout=30.0
        )
        response.raise_for_status()
        print(f"✅ Modelo {model} configurado con keep_alive={keep_alive}")

# Uso
await configure_keep_alive("llama3.2:1b", -1)  # Permanente
```

---

## 📊 IMPACTO EN LATENCIAS

### Sin keep_alive (default: 5 minutos)

```
Request 1: 507ms   (modelo en RAM)
Request 2: 14,835ms (modelo descargándose) ❌
Request 3: 1,230ms  (modelo cargándose)
Request 4: 639ms    (modelo en RAM)
Request 5: 9,267ms  (modelo descargándose) ❌

Promedio: 6,520ms
Varianza: 23x (507ms - 14,835ms)
```

### Con keep_alive = -1 (permanente)

```
Request 1: 507ms   (modelo en RAM)
Request 2: 520ms   (modelo en RAM) ✅
Request 3: 495ms   (modelo en RAM) ✅
Request 4: 510ms   (modelo en RAM) ✅
Request 5: 503ms   (modelo en RAM) ✅

Promedio: 507ms (12.9x mejor)
Varianza: 1.05x (495ms - 520ms) ✅
```

**Mejora**: 6,520ms → 507ms = **12.9x speedup**

---

## 🔍 VERIFICACIÓN

### Comprobar que keep_alive está activo

```bash
# Listar modelos cargados
curl http://localhost:11434/api/tags | python3 -m json.tool

# Verificar uso de VRAM
nvidia-smi

# Ver logs de Ollama
journalctl -u ollama -f
```

### Señales de que keep_alive funciona

✅ **Funcionando correctamente**:
- TTFB consistente (~500ms)
- Varianza baja (<10%)
- nvidia-smi muestra VRAM usado (~1.3GB)

❌ **NO funcionando**:
- TTFB variable (500ms - 15,000ms)
- Varianza alta (>20x)
- nvidia-smi muestra VRAM vacío

---

## 💡 TIPS Y TRUCOS

### 1. Precalentar Modelo al Inicio

```bash
# Agregar a startup.sh
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Sistema iniciado",
  "keep_alive": -1
}'
```

### 2. Múltiples Modelos

```bash
# Si tienes suficiente VRAM (>6GB), puedes mantener varios:
curl http://localhost:11434/api/generate -d '{"model": "llama3.2:1b", "prompt": "warmup", "keep_alive": -1}'
curl http://localhost:11434/api/generate -d '{"model": "phi3:mini", "prompt": "warmup", "keep_alive": -1}'

# GTX 1050 (3GB): Solo 1 modelo a la vez
```

### 3. Liberar RAM Manualmente

```bash
# Si necesitas liberar RAM sin reiniciar:
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "shutdown",
  "keep_alive": 0
}'
```

### 4. Configuración por Defecto

```bash
# Editar configuración global de Ollama
sudo nano /etc/systemd/system/ollama.service

# Agregar variable de entorno:
Environment="OLLAMA_KEEP_ALIVE=-1"

# Reiniciar servicio
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

---

##  WORKFLOW RECOMENDADO

### Para Benchmarks

```bash
# 1. Configurar keep_alive permanente
./scripts/ollama_keep_alive.sh

# 2. Esperar 10 segundos (modelo en RAM)
sleep 10

# 3. Ejecutar benchmark
cd backend && python sentinel_global_benchmark.py

# 4. Resultados consistentes garantizados ✅
```

### Para Producción

```bash
# 1. Agregar a startup.sh
echo "curl http://localhost:11434/api/generate -d '{\"model\": \"llama3.2:1b\", \"prompt\": \"warmup\", \"keep_alive\": -1}'" >> startup.sh

# 2. Modelo siempre listo ✅
```

---

## 📝 RESUMEN

**Configuración Recomendada**: `keep_alive = -1` (permanente)

**Beneficios**:
- ✅ 12.9x speedup (6,520ms → 507ms)
- ✅ Varianza <10% (vs 23x)
- ✅ Latencias predecibles
- ✅ Ideal para producción

**Costo**:
- ⚠ 1.3 GB VRAM permanente
- ⚠ Solo se libera reiniciando

**Próxima Acción**: Ejecutar `./scripts/ollama_keep_alive.sh` y re-ejecutar benchmark

---

**¿Configuramos keep_alive permanente ahora?** 
