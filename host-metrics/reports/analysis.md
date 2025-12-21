
# Análisis de Métricas (Host)

- Muestras: 7321
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-21T02:59:00.055Z

## Promedios
- CPU: 202238.29%
- Memoria: 2476731.37%
- GPU: 3.49%
- WiFi (señal): 62.98%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
