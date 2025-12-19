
# Análisis de Métricas (Host)

- Muestras: 5879
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-19T18:59:00.281Z

## Promedios
- CPU: 251838.37%
- Memoria: 3084210.58%
- GPU: 4.0%
- WiFi (señal): 63.4%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
