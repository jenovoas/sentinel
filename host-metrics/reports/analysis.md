
# Análisis de Métricas (Host)

- Muestras: 7021
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T21:59:00.230Z

## Promedios
- CPU: 210878.83%
- Memoria: 2582556.86%
- GPU: 3.64%
- WiFi (señal): 62.94%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
