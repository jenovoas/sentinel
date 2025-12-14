
# Análisis de Métricas (Host)

- Muestras: 1
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-14T01:30:27.903492Z

## Promedios
- CPU: 17.0%
- Memoria: 61.3%
- GPU: 0.0%
- WiFi (señal): 0.0%

## Observaciones
- Si WiFi promedio < 30%, revisar interferencias o distancia.
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
