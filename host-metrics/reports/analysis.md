
# Análisis de Métricas (Host)

- Muestras: 3718
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-17T20:59:00.632Z

## Promedios
- CPU: 28.72%
- Memoria: 54.87%
- GPU: 3.49%
- WiFi (señal): 62.77%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
