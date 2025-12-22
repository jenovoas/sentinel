
# Análisis de Métricas (Host)

- Muestras: 8466
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-22T05:59:01.014Z

## Promedios
- CPU: 174889.3%
- Memoria: 2141768.89%
- GPU: 3.34%
- WiFi (señal): 63.78%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
