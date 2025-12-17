
# Análisis de Métricas (Host)

- Muestras: 2875
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-17T01:59:00.087Z

## Promedios
- CPU: 29.92%
- Memoria: 55.42%
- GPU: 3.63%
- WiFi (señal): 63.16%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
