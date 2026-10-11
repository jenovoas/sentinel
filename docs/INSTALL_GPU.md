#  Instalación Rápida de NVIDIA Container Toolkit

## Comandos de Instalación

```bash
# 1. Configurar repositorio
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
   && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
      sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
      sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2. Instalar toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 3. Configurar Docker
sudo nvidia-ctk runtime configure --runtime=docker

# 4. Reiniciar Docker
sudo systemctl restart docker

# 5. Verificar instalación
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi

# 6. Iniciar Ollama con GPU
cd /home/jnovoas/sentinel
docker-compose up -d ollama
docker-compose up ollama-init
```

## Verificación

```bash
# Ver logs de Ollama
docker-compose logs ollama | grep -i gpu

# Debería mostrar: "GPU detected: NVIDIA GeForce GTX 1050"
```

## Beneficios

- ⚡ **5-10x más rápido**: 100-500ms vs 1-3s
- 💻 **CPU libre**: No consume CPU durante inferencia
-  **Mejor UX**: Respuestas casi instantáneas
