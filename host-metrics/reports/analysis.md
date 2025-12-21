
# Análisis de Métricas (Host)

- Muestras: 8072
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-21T22:59:00.763Z

## Promedios
- CPU: 183424.57%
- Memoria: 2246307.54%
- GPU: 3.2%
- WiFi (señal): 63.56%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
