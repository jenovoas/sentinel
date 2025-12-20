
# Análisis de Métricas (Host)

- Muestras: 6901
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T19:59:00.788Z

## Promedios
- CPU: 214545.44%
- Memoria: 2627463.38%
- GPU: 3.71%
- WiFi (señal): 62.97%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
