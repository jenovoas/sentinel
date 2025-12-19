
# Análisis de Métricas (Host)

- Muestras: 5186
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-19T02:59:00.935Z

## Promedios
- CPU: 285487.82%
- Memoria: 3496344.42%
- GPU: 3.79%
- WiFi (señal): 62.74%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
