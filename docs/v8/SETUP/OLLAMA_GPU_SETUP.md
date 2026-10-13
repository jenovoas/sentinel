# Configuración de Ollama con GPU - Guía de Instalación

## Estado Actual

✅ **Ollama instalado con soporte NVIDIA GPU**  
✅ **Servicio systemd configurado**  
✅ **GPU detectada y funcionando**

---

## GPU Detectada

- **Modelo**: NVIDIA GeForce GTX 1050
- **VRAM**: 3072 MB (3 GB)
- **Driver**: 550.163.01
- **CUDA**: 12.4

---

## Beneficios de GPU

**Con GPU (actual):**
- ⚡ **Latencia**: ~1 segundo por query
- 🚀 **Capas en GPU**: 25/29 (86% del modelo)
- 💾 **VRAM usada**: 1.4GB / 3GB
- 🎯 **Velocidad**: 10-15x más rápido que CPU

**Sin GPU (CPU only):**
- 🐌 **Latencia**: 10-15 segundos por query
- 💻 **CPU**: Alto uso durante inferencia
- ⚠️ **Experiencia**: Degradada

---

## Instalación (Ya Completada)

### Paso 1: Instalar Ollama con GPU

```bash
# Instalar Ollama (detecta GPU automáticamente)
curl -fsSL https://ollama.com/install.sh | sh

# El script automáticamente:
# - Detecta NVIDIA GPU
# - Crea usuario 'ollama'
# - Configura servicio systemd
# - Habilita auto-start
```

### Paso 2: Verificar Instalación

```bash
# Verificar servicio
systemctl status ollama

# Verificar GPU detection
journalctl -u ollama -n 50 | grep -i "gpu\|cuda\|vram"

# Deberías ver:
# "offloaded 25/29 layers to GPU"
# "CUDA0 model buffer size = 1434.12 MiB"
```

### Paso 3: Descargar Modelos

```bash
# Modelo recomendado para GTX 1050
ollama pull llama3.2:3b

# Alternativa más rápida
ollama pull llama3.2:1b

# Verificar modelos instalados
ollama list
```

---

## Modelos Recomendados para GTX 1050 (3GB)

| Modelo | Tamaño | VRAM | Velocidad | Calidad | Recomendado |
|--------|--------|------|-----------|---------|-------------|
| `llama3.2:1b` | 1.3GB | ~1.5GB | ⚡⚡⚡ | 🧠🧠 | CPU fallback |
| `llama3.2:3b` | 2.0GB | ~1.4GB | ⚡⚡ | 🧠🧠🧠 | ✅ **Óptimo** |
| `phi3:mini` | 2.2GB | ~2GB | ⚡⚡ | 🧠🧠 | Alternativa |
| `llama3:8b` | 4.7GB | ~4GB | ❌ | 🧠🧠🧠🧠 | No cabe |

**Recomendación**: `llama3.2:3b` - Balance perfecto de velocidad y calidad para GTX 1050.

---

## Troubleshooting

### Problema: "0 B VRAM" o GPU no detectada

**Síntomas:**
```
entering low vram mode
total vram = 0 B
```

**Causa**: Ollama no encuentra las librerías CUDA.

**Solución:**
```bash
# 1. Verificar que CUDA está instalado
dpkg -l | grep -i cuda

# Deberías ver: libcudart12, nvidia-cuda-toolkit

# 2. Reinstalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 3. Reiniciar servicio
sudo systemctl restart ollama

# 4. Verificar GPU detection
journalctl -u ollama -n 50 | grep -i "offloaded"
```

---

### Problema: Modelo muy lento

**Síntomas**: Respuestas toman >5 segundos

**Diagnóstico:**
```bash
# Ver si GPU está siendo usada
journalctl -u ollama -f

# Mientras haces una query, deberías ver:
# "offloading X layers to GPU"
```

**Soluciones:**
1. **GPU no detectada**: Ver sección anterior
2. **Modelo muy grande**: Cambiar a `llama3.2:1b`
3. **VRAM llena**: Reiniciar Ollama para liberar memoria

---

### Problema: Servicio no inicia

```bash
# Ver logs de error
journalctl -u ollama -n 100 --no-pager

# Reiniciar servicio
sudo systemctl restart ollama

# Verificar puerto
sudo lsof -i :11434
```

---

## Verificación de GPU (Script Rápido)

```bash
#!/bin/bash
# Guardar como: check_ollama_gpu.sh

echo "🔍 GPU Info:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

echo -e "\n🔍 Servicio Ollama:"
systemctl status ollama | grep "Active:"

echo -e "\n🔍 GPU Offloading:"
journalctl -u ollama -n 20 | grep -i "offloaded\|vram" | tail -3

echo -e "\n🧪 Test Rápido:"
time ollama run llama3.2:3b "Test: 2+2="
```

---

## Monitoreo en Tiempo Real

```bash
# Terminal 1: Monitorear VRAM
watch -n 1 nvidia-smi

# Terminal 2: Ver logs de Ollama
journalctl -u ollama -f

# Terminal 3: Hacer queries
ollama run llama3.2:3b "Tu pregunta aquí"
```

---

## Configuración Avanzada

### Variables de Entorno

```bash
# En /etc/systemd/system/ollama.service
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"  # Exponer en red
Environment="OLLAMA_KEEP_ALIVE=5m"       # Mantener modelo en VRAM
Environment="OLLAMA_NUM_PARALLEL=2"      # Requests concurrentes
Environment="OLLAMA_MAX_LOADED_MODELS=1" # Solo 1 modelo en VRAM

# Recargar después de cambios
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

---

## Integración con Sentinel

### Backend API

El backend de Sentinel usa Ollama automáticamente:

```python
# backend/app/routers/ai.py
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
```

### Endpoints Disponibles

```bash
# Health check
curl http://localhost:8000/api/v1/ai/health

# Query con rol Sovereign
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analiza el estado del sistema",
    "role": "Sovereign",
    "max_tokens": 100
  }'
```

---

## Próximos Pasos

1. ✅ GPU configurada y funcionando
2. ✅ Modelo `llama3.2:3b` instalado
3. ✅ Servicio systemd habilitado
4. 📝 Ver `docs/AI_BACKEND_API.md` para API reference
5. 🧪 Ejecutar tests: `pytest backend/tests/test_ai_*.py`
6. 📊 Ejecutar benchmarks: `python backend/benchmarks/bench_ollama_gpu.py`

---

**Última actualización**: 2026-01-13  
**Versión**: 2.0 (systemd + GPU nativa)
