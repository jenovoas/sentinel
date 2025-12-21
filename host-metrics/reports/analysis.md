
# Análisis de Métricas (Host)

- Muestras: 7381
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-21T03:59:00.720Z

## Promedios
- CPU: 200594.45%
- Memoria: 2456598.57%
- GPU: 3.47%
- WiFi (señal): 62.95%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
