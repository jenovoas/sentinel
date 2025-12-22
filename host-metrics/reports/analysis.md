
# Análisis de Métricas (Host)

- Muestras: 8286
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-22T02:59:00.596Z

## Promedios
- CPU: 178688.01%
- Memoria: 2188294.15%
- GPU: 3.26%
- WiFi (señal): 63.81%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
