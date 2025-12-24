
# Análisis de Métricas (Host)

- Muestras: 12022
- Rango: 2025-12-14T01:30:27.903492Z → 0

## Promedios
- CPU: 68817768.44%
- Memoria: 198115976.2%
- GPU: 2.48%
- WiFi (señal): 47.13%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
