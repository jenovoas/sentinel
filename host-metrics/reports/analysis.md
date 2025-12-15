
# Análisis de Métricas (Host)

- Muestras: 1190
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-15T05:59:00.800Z

## Promedios
- CPU: 34.02%
- Memoria: 52.41%
- GPU: 5.12%
- WiFi (señal): 65.56%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
