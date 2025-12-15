
# Análisis de Métricas (Host)

- Muestras: 1130
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-15T04:59:00.478Z

## Promedios
- CPU: 33.76%
- Memoria: 51.94%
- GPU: 5.26%
- WiFi (señal): 65.55%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
