
# Análisis de Métricas (Host)

- Muestras: 6603
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T15:00:00.103Z

## Promedios
- CPU: 224227.2%
- Memoria: 2746040.74%
- GPU: 3.87%
- WiFi (señal): 63.06%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
