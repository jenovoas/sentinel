
# Análisis de Métricas (Host)

- Muestras: 12772
- Rango: 2025-12-14T01:30:27.903492Z → 0

## Promedios
- CPU: 78641707.66%
- Memoria: 241317776.9%
- GPU: 2.33%
- WiFi (señal): 44.36%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
