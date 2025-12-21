
# Análisis de Métricas (Host)

- Muestras: 7593
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-21T14:59:01.016Z

## Promedios
- CPU: 194994.45%
- Memoria: 2388010.93%
- GPU: 3.37%
- WiFi (señal): 63.12%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
