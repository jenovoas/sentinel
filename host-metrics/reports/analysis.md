
# Análisis de Métricas (Host)

- Muestras: 7081
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T22:59:00.827Z

## Promedios
- CPU: 209092.13%
- Memoria: 2560674.41%
- GPU: 3.61%
- WiFi (señal): 62.93%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
