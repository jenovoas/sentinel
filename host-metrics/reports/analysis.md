
# Análisis de Métricas (Host)

- Muestras: 6539
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T05:59:00.924Z

## Promedios
- CPU: 226421.58%
- Memoria: 2772917.0%
- GPU: 3.91%
- WiFi (señal): 63.09%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
