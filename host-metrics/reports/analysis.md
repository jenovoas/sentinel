
# Análisis de Métricas (Host)

- Muestras: 12654
- Rango: 2025-12-14T01:30:27.903492Z → 0

## Promedios
- CPU: 77678375.31%
- Memoria: 240101259.42%
- GPU: 2.35%
- WiFi (señal): 44.77%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
