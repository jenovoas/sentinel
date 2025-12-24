
# Análisis de Métricas (Host)

- Muestras: 11200
- Rango: 2025-12-14T01:30:27.903492Z → 0

## Promedios
- CPU: 62859588.63%
- Memoria: 124152893.32%
- GPU: 2.66%
- WiFi (señal): 50.59%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
