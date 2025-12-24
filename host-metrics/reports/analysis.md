
# Análisis de Métricas (Host)

- Muestras: 11092
- Rango: 2025-12-14T01:30:27.903492Z → 0

## Promedios
- CPU: 62915289.0%
- Memoria: 124930420.85%
- GPU: 2.69%
- WiFi (señal): 51.08%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
