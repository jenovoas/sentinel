
# Análisis de Métricas (Host)

- Muestras: 5999
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-19T20:59:00.652Z

## Promedios
- CPU: 246801.18%
- Memoria: 3022517.21%
- GPU: 4.01%
- WiFi (señal): 63.32%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
