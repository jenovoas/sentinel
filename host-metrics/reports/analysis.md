
# Análisis de Métricas (Host)

- Muestras: 6721
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T16:59:00.867Z

## Promedios
- CPU: 220290.83%
- Memoria: 2697829.63%
- GPU: 3.81%
- WiFi (señal): 63.02%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
