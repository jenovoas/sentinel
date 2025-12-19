
# Análisis de Métricas (Host)

- Muestras: 5246
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-19T03:59:00.215Z

## Promedios
- CPU: 282223.14%
- Memoria: 3456356.47%
- GPU: 3.78%
- WiFi (señal): 62.86%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
