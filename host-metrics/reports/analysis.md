
# Análisis de Métricas (Host)

- Muestras: 6841
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-20T18:59:00.225Z

## Promedios
- CPU: 216426.97%
- Memoria: 2650507.33%
- GPU: 3.74%
- WiFi (señal): 62.99%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
