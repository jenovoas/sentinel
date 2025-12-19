
# Análisis de Métricas (Host)

- Muestras: 5939
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-19T19:59:00.905Z

## Promedios
- CPU: 249294.34%
- Memoria: 3053052.29%
- GPU: 4.0%
- WiFi (señal): 63.34%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
