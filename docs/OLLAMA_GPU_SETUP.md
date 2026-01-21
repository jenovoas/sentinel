# Configuración de Ollama con GPU - Guía de Instalación

## Problema Detectado

Docker no puede acceder a la GPU NVIDIA porque falta el **NVIDIA Container Toolkit**.

## GPU Detectada

- **Modelo**: NVIDIA GeForce GTX 1050
- **VRAM**: 3072 MB (3 GB)
- **Driver**: 580.105.08

## Beneficios de GPU

Con GPU:
- **Latencia**: 100-500ms por query
- **Modelos**: Puede correr phi3:mini (1.3B) cómodamente

Sin GPU (CPU):
- **Latencia**: 1-3 segundos por query
- **CPU**: Alto uso durante inferencia

## Instalación de NVIDIA Container Toolkit

### Paso 1: Instalar NVIDIA Container Toolkit

```bash
# Configurar repositorio
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Instalar
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configurar Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Paso 2: Verificar Instalación

```bash
# Test GPU en Docker
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Debería mostrar tu GTX 1050
```

### Paso 3: Iniciar Ollama con GPU

```bash
cd /home/jnovoas/sentinel
docker-compose up -d ollama
docker-compose logs -f ollama

# Verificar que detecta GPU
docker-compose exec ollama nvidia-smi
```

### Paso 4: Descargar Modelos

```bash
# Ejecutar model loader
docker-compose up ollama-init

# Ver progreso
docker-compose logs -f ollama-init
```

## Alternativa: Sin GPU

Si prefieres no instalar el toolkit, puedes usar Ollama sin GPU:

```yaml
# En docker-compose.yml, comentar la sección deploy:
    restart: unless-stopped
    # GPU support for NVIDIA GTX 1050 (3GB VRAM)
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]
```

Luego:
```bash
docker-compose up -d ollama
```

## Recomendación

Para tu GTX 1050 con 3GB VRAM, **SÍ vale la pena** instalar el toolkit:
- Latencia 5-10x más rápida
- Mejor experiencia de usuario
- CPU libre para otras tareas

## Modelos Recomendados para GTX 1050 (3GB)

- ✅ `phi3:mini` (1.3B) - Perfecto, usa ~2GB VRAM
- ✅ `llama3.2:1b` (1B) - Muy rápido, usa ~1.5GB VRAM
- ⚠️ `llama3.2:3b` (3B) - Justo en el límite, puede funcionar
- ❌ `llama3:8b` (8B) - Demasiado grande, no cabrá

## Próximos Pasos

1. Instalar NVIDIA Container Toolkit (comandos arriba)
2. Reiniciar Docker
3. Iniciar Ollama con GPU
4. Descargar modelos
5. Probar endpoint de IA
