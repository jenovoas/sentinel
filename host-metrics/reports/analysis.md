
# Análisis de Métricas (Host)

- Muestras: 1945
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-16T01:59:00.352Z

## Promedios
- CPU: 30.02%
- Memoria: 55.61%
- GPU: 4.23%
- WiFi (señal): 64.29%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
