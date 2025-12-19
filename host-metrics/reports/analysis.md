
# Análisis de Métricas (Host)

- Muestras: 5699
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-19T15:59:00.620Z

## Promedios
- CPU: 259791.72%
- Memoria: 3181622.26%
- GPU: 3.9%
- WiFi (señal): 63.49%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
