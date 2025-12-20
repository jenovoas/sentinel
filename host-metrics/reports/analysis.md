
# Análisis de Métricas (Host)

- Muestras: 6961
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T20:59:00.826Z

## Promedios
- CPU: 212696.31%
- Memoria: 2604816.55%
- GPU: 3.67%
- WiFi (señal): 62.96%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
