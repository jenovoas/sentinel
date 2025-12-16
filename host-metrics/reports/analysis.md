
# Análisis de Métricas (Host)

- Muestras: 2005
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-16T02:59:00.181Z

## Promedios
- CPU: 30.14%
- Memoria: 56.01%
- GPU: 4.15%
- WiFi (señal): 64.24%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
