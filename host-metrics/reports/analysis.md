
# Análisis de Métricas (Host)

- Muestras: 1070
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-15T03:59:00.076Z

## Promedios
- CPU: 34.04%
- Memoria: 51.44%
- GPU: 5.39%
- WiFi (señal): 65.68%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
