
# Análisis de Métricas (Host)

- Muestras: 8406
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-22T04:59:00.806Z

## Promedios
- CPU: 176137.47%
- Memoria: 2157055.91%
- GPU: 3.34%
- WiFi (señal): 63.79%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
