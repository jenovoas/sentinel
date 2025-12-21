
# Análisis de Métricas (Host)

- Muestras: 8012
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-21T21:59:00.201Z

## Promedios
- CPU: 184798.03%
- Memoria: 2263129.19%
- GPU: 3.21%
- WiFi (señal): 63.56%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
