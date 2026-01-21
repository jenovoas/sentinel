# Dockerfile personalizado para n8n con workflows preloaded
# BASE: Imagen oficial de n8n
FROM n8nio/n8n:latest

# Usuario root temporalmente para copiar archivos
USER root

# Copiar el script de inicialización de workflows
COPY init-workflows.sh /usr/local/bin/init-workflows.sh
RUN chmod +x /usr/local/bin/init-workflows.sh

# Copiar el entrypoint wrapper
COPY entrypoint.sh /entrypoint-wrapper.sh
RUN chmod +x /entrypoint-wrapper.sh

# Copiar workflows JSON que serán inyectados
COPY workflows/ /tmp/workflows/

# Volver al usuario node (por seguridad)
USER node

# Usar nuestro entrypoint personalizado
ENTRYPOINT ["/entrypoint-wrapper.sh"]

# CÓMO FUNCIONA:
# 1. entrypoint-wrapper.sh inicia n8n en background
# 2. Ejecuta init-workflows.sh (que espera y luego inyecta)
# 3. Mantiene n8n corriendo en foreground
# 4. Los workflows quedan en la BD de n8n permanentemente
